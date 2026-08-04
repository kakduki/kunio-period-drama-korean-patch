-- Bounded route probe for identifying item/inventory state in SRAM.
-- It reuses the known entry route and map-input experiment, but captures
-- CPU RAM and SRAM snapshots at a fixed cadence instead of running forever.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."
local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/sram_route_probe")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "7200")
local CAPTURE_GAP = tonumber(os.getenv("KUNIO_SRAM_CAPTURE_GAP") or "60")
local CAPTURE_START = tonumber(os.getenv("KUNIO_SRAM_CAPTURE_START") or "120")
local UNIQUE_LIMIT = tonumber(os.getenv("KUNIO_STAGE_UNIQUE_LIMIT") or "72")
-- Full SRAM snapshots are useful for inventory analysis but too slow for a
-- route probe. Narrow the range when investigating a documented state byte.
local SRAM_START = tonumber(os.getenv("KUNIO_SRAM_START") or "0x6000")
local SRAM_LENGTH = tonumber(os.getenv("KUNIO_SRAM_LENGTH") or "0x2000")
local ADVANCE_AFTER_COMBAT = os.getenv("KUNIO_ADVANCE_AFTER_COMBAT") == "1"
local MAP_SOURCE_ROUTE = os.getenv("KUNIO_MAP_SOURCE_ROUTE") == "1"
local MAP_DIRECTION = os.getenv("KUNIO_MAP_DIRECTION") or "right"

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line)
    local f = assert(io.open(path, "a")); f:write(line .. "\n"); f:close()
end
local function byte_at(address, domain)
    local ok, value
    if domain ~= nil then
        ok, value = pcall(function() return memory.readbyte(address, domain) end)
        if ok and value ~= nil then return value end
    end
    ok, value = pcall(function() return memory.readbyte(address) end)
    return ok and value or 0
end
local function hex2(value) return string.format("%02X", (value or 0) % 0x100) end

local function dump_range(path, start_address, length, domain)
    local f = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        f:write(string.char(byte_at(start_address + offset, domain)))
    end
    f:close()
end

local function diff_snapshot(previous, current, base_address)
    local changes = {}
    for offset = 0, #current - 1 do
        local before = previous and previous:byte(offset + 1) or nil
        local after = current:byte(offset + 1)
        if before == nil or before ~= after then
            changes[#changes + 1] = string.format("%04X:%02X>%02X", base_address + offset, before or 0, after)
        end
    end
    return table.concat(changes, ",")
end

local function read_blob(start_address, length, domain)
    local values = {}
    for offset = 0, length - 1 do values[#values + 1] = string.char(byte_at(start_address + offset, domain)) end
    return table.concat(values)
end

local function fingerprint()
    local ok, ppu_byte = pcall(function() return ppu.readbyte(0x2000) end)
    local hash = ok and (ppu_byte or 0) or 0
    for address = 0x2000, 0x23BF, 8 do
        local value_ok, value = pcall(function() return ppu.readbyte(address) end)
        if value_ok and value ~= nil then hash = (hash * 131 + value + address) % 1000000007 end
    end
    return tostring(hash)
end

local function entry_input(frame)
    if frame >= 40 and frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    if frame >= 480 and frame < 490 then return { down = true } end
    if frame >= 540 and frame < 550 then return { A = true } end
    if frame >= 700 and frame < 712 then return { B = true } end
    return {}
end

local function combat_input(frame)
    if not ADVANCE_AFTER_COMBAT or not (byte_at(0x04F1) == 0x06 or byte_at(0x04F1) == 0x12) then
        local rel = frame - 900
        local cycle = rel % 240
        if cycle < 72 then return { right = true, A = true, B = true } end
        if cycle < 96 then return { right = true, B = true } end
        if cycle < 144 then return { left = true, A = true, B = true } end
        if cycle < 168 then return { left = true, A = true } end
        if cycle < 216 then return { right = true, A = true } end
        return { up = true, A = true, B = true }
    end
    if MAP_SOURCE_ROUTE then
        local map_cycle = frame % 192
        local direction = {}
        if MAP_DIRECTION == "left" then direction.left = true
        elseif MAP_DIRECTION == "up" then direction.up = true
        elseif MAP_DIRECTION == "down" then direction.down = true
        else direction.right = true end
        if map_cycle < 8 then return { start = true } end
        if map_cycle < 24 then return { B = true } end
        if map_cycle < 96 then direction.A = true; return direction end
        if map_cycle < 168 then direction.B = true; return direction end
    end
    return {}
end

mkdir(OUT_DIR)
local snapshot_path = OUT_DIR .. "/snapshots.tsv"
local delta_path = OUT_DIR .. "/sram_diff.tsv"
append(snapshot_path, "frame\tphase\tfingerprint\t04F1\t04FA\t04FB\t04FC\t0502\t0503\t0700\t0701\t0702\t0706\t0707\t071D\t071E\t071F\tcpu_file\tsram_file")
append(delta_path, "frame\tphase\tcpu_changed\tsram_changed")

local previous_cpu = nil
local previous_sram = nil
local last_capture = -999999
local last_fingerprint = nil
local unique = 0

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and unique < UNIQUE_LIMIT do
    local frame = emu.framecount()
    local phase = frame < 900 and "entry" or "combat_or_map"
    joypad.set(1, frame < 900 and entry_input(frame) or combat_input(frame))
    emu.frameadvance()

    if frame >= CAPTURE_START and frame - last_capture >= CAPTURE_GAP then
        local fp = fingerprint()
        if fp ~= last_fingerprint then
            unique = unique + 1
            last_fingerprint = fp
            last_capture = frame
            local stem = string.format("%s/frame_%06d", OUT_DIR, frame)
            local cpu = read_blob(0x0000, 0x0800)
            local sram = read_blob(SRAM_START, SRAM_LENGTH)
            local cpu_file = stem .. "_cpu_ram.bin"
            local sram_file = string.format("%s_sram_%04x_%04x.bin", stem, SRAM_START, SRAM_START + SRAM_LENGTH - 1)
            local f = assert(io.open(cpu_file, "wb")); f:write(cpu); f:close()
            f = assert(io.open(sram_file, "wb")); f:write(sram); f:close()
            append(snapshot_path, table.concat({
                frame, phase, fp, hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)),
                hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)), hex2(byte_at(0x0502)),
                hex2(byte_at(0x0503)), hex2(byte_at(0x0700)), hex2(byte_at(0x0701)),
                hex2(byte_at(0x0702)), hex2(byte_at(0x0706)), hex2(byte_at(0x0707)),
                hex2(byte_at(0x071D)), hex2(byte_at(0x071E)), hex2(byte_at(0x071F)),
                cpu_file, sram_file,
            }, "\t"))
            append(delta_path, table.concat({ frame, phase, diff_snapshot(previous_cpu, cpu, 0x0000), diff_snapshot(previous_sram, sram, SRAM_START) }, "\t"))
            previous_cpu, previous_sram = cpu, sram
            gui.text(2, 8, "Kunio SRAM route probe")
            gui.text(2, 17, phase .. " frame=" .. tostring(frame) .. " unique=" .. tostring(unique))
        end
    end
end

append(snapshot_path, table.concat({ emu.framecount(), "end", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "" }, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
