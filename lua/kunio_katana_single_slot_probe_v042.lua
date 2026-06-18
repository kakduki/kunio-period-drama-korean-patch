-- Single-address inventory probe for the v0.4.2 Katana visual target.
--
-- Set KUNIO_SLOT_ADDR to one CPU address such as 0x0502. This intentionally
-- writes only one candidate slot so failed runs are interpretable.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."

KUNIO_TARGETS_LUA = LUA_DIR .. "/kunio_v041_conflict_safe_targets.lua"
KUNIO_MANUAL_DUMP_OUTPUT = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/katana_single_slot_probe_v042")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = true
local manual = dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = nil

local SLOT_ADDR = tonumber(os.getenv("KUNIO_SLOT_ADDR") or "0x0502")
local SLOT_VALUE = tonumber(os.getenv("KUNIO_SLOT_VALUE") or "0x84")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "2700")
local SNAPSHOT_GAP = 90
local summary_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/single_slot_probe_summary.tsv"
local last_fingerprint = nil
local last_dump_frame = -999999

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function byte_at(addr, domain)
    if domain ~= nil then
        local ok, value = pcall(function() return memory.readbyte(addr, domain) end)
        if ok and value ~= nil then return value end
    end
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return 0
end

local function write_byte(addr, value)
    pcall(function() memory.writebyte(addr, value) end)
end

local function screen_fingerprint()
    local hash = 0
    local sum = 0
    for addr = 0x2000, 0x23BF, 4 do
        local value = byte_at(addr, "ppu")
        hash = (hash * 131 + value + addr) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end

local function press_for(frame, start_frame, duration, buttons)
    if frame >= start_frame and frame < start_frame + duration then return buttons end
    return nil
end

local function input_for(frame)
    return press_for(frame, 40, 10, { start = true })
        or press_for(frame, 130, 10, { A = true })
        or press_for(frame, 220, 10, { start = true })
        or press_for(frame, 300, 10, { down = true })
        or press_for(frame, 360, 10, { A = true })
        or press_for(frame, 480, 10, { down = true })
        or press_for(frame, 540, 10, { A = true })
        or press_for(frame, 700, 12, { B = true })
        or press_for(frame, 880, 12, { A = true })
        or press_for(frame, 940, 12, { A = true })
        or press_for(frame, 1620, 12, { start = true })
        or press_for(frame, 1704, 12, { right = true })
        or press_for(frame, 1746, 12, { A = true })
        or press_for(frame, 1860, 12, { B = true })
        or press_for(frame, 2220, 12, { left = true })
        or press_for(frame, 2262, 12, { A = true })
        or {}
end

mkdir(KUNIO_MANUAL_DUMP_OUTPUT)
append(summary_path, "frame\tphase\tslot_addr\tslot_value\tfingerprint\tdump_prefix")
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    if frame >= 1500 and frame <= 2320 then
        write_byte(SLOT_ADDR, SLOT_VALUE)
    end
    local buttons = input_for(frame)
    joypad.set(1, buttons)
    gui.text(2, 8, "Kunio single-slot Katana probe")
    gui.text(2, 17, string.format("addr=$%04X value=$%02X frame=%d", SLOT_ADDR, SLOT_VALUE, frame))
    emu.frameadvance()

    if frame > 120 and frame - last_dump_frame >= SNAPSHOT_GAP then
        local fingerprint = screen_fingerprint()
        if fingerprint ~= last_fingerprint then
            last_fingerprint = fingerprint
            last_dump_frame = frame
            local ok, prefix = pcall(function() return manual.dump_current_screen() end)
            append(summary_path, table.concat({
                tostring(frame),
                frame >= 1500 and "inject" or "route",
                string.format("0x%04X", SLOT_ADDR),
                string.format("0x%02X", SLOT_VALUE),
                fingerprint,
                ok and tostring(prefix) or ("ERROR:" .. tostring(prefix)),
            }, "\t"))
        end
    end
end

append(summary_path, table.concat({ tostring(emu.framecount()), "done", string.format("0x%04X", SLOT_ADDR), string.format("0x%02X", SLOT_VALUE), tostring(last_fingerprint or ""), "" }, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
