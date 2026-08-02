-- Bounded pre-pointer ownership scan.
--
-- The generated target table contains the bytes currently owned by the
-- runnable pointer-owner candidate. This script checks the expected Bank 1
-- CPU window during the known entry/combat route, registers read callbacks for
-- those locations, and records nearby PPU nametable writes and snapshots.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pre_pointer_runtime_scan"
local TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or "kunio_pre_pointer_runtime_targets.lua"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "7200")
local EXTRA_DIALOGUE_START = os.getenv("KUNIO_EXTRA_DIALOGUE_START") ~= "0"
local HIT_LIMIT = tonumber(os.getenv("KUNIO_HIT_LIMIT") or "50000")
local ok_targets, targets = pcall(function() return dofile(TARGETS_LUA) end)
if not ok_targets or type(targets) ~= "table" then targets = {} end

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line)
    local f = assert(io.open(path, "a")); f:write(line .. "\n"); f:close()
end
local function hex2(value) return string.format("%02X", (value or 0) % 0x100) end
local function hex4(value) return string.format("%04X", (value or 0) % 0x10000) end
local function byte_at(addr)
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    return ok and value or 0
end
local function bytes_text(values)
    local out = {}
    for _, value in ipairs(values) do out[#out + 1] = hex2(value) end
    return table.concat(out, " ")
end
local function pattern_at(addr, values)
    for index, expected in ipairs(values) do
        if byte_at(addr + index - 1) ~= expected then return false end
    end
    return true
end

local function entry_input(frame)
    if frame < 40 then return {} end
    if frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    if frame >= 480 and frame < 490 then return { down = true } end
    if frame >= 540 and frame < 550 then return { A = true } end
    if frame >= 700 and frame < 712 then return { B = true } end
    if EXTRA_DIALOGUE_START and frame >= 650 and frame < 665 then return { start = true } end
    return {}
end

local function combat_input(frame)
    local cycle = (frame - 900) % 240
    if cycle < 72 then return { right = true, A = true, B = true } end
    if cycle < 96 then return { right = true, B = true } end
    if cycle < 144 then return { left = true, A = true, B = true } end
    if cycle < 168 then return { left = true, A = true } end
    if cycle < 216 then return { right = true, A = true } end
    return { up = true, A = true, B = true }
end

local function register_read(addr, callback)
    if memory.registerread == nil then return false end
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(addr, 1, callback) end)
end
local function read_pc()
    local ok, value = pcall(function() return memory.getregister("pc") end)
    return ok and value or 0
end

local ppu_addr_high = nil
local ppu_addr = 0
local ppu_increment = 1
local ppu_write_count = 0
local ppu_hash = 0
local ppu_tail = {}
local source_read_count = 0
local source_read_limit_hit = false
local active = {}
local address_targets = {}
local seen = {}
local pending = {}
local source_pending = {}
local captured = {}
local source_captured = {}
local matched = 0

local summary_path = OUT_DIR .. "/summary.tsv"
local matches_path = OUT_DIR .. "/matches.tsv"
local reads_path = OUT_DIR .. "/source_reads.tsv"
local ppu_path = OUT_DIR .. "/ppu_writes.tsv"
mkdir(OUT_DIR)
append(summary_path, "frame\treason\ttargets\tmatched\tread_targets\tcaptured\tdetail")
append(matches_path, "frame\ttarget\trom_offset\tcpu_addr\tbytes\tppu_hash\tppu_writes")
append(reads_path, "frame\ttarget\trom_offset\tcpu_addr\tvalue\tpc\tppu_hash")
append(ppu_path, "frame\tppu_address\tvalue\tpc")

local function on_ppu_control(addr, size, value)
    ppu_increment = (math.floor((value or 0) / 4) % 2 == 1) and 32 or 1
end
local function on_ppu_status(addr, size, value) ppu_addr_high = nil end
local function on_ppu_scroll(addr, size, value) ppu_addr_high = nil end
local function on_ppu_address(addr, size, value)
    local byte = value or 0
    if ppu_addr_high == nil then ppu_addr_high = byte % 0x40
    else ppu_addr = ppu_addr_high * 0x100 + byte; ppu_addr_high = nil end
end
local function on_ppu_data(addr, size, value)
    local target = ppu_addr % 0x4000
    local byte = value or 0
    if target >= 0x2000 and target < 0x3000 then
        ppu_write_count = ppu_write_count + 1
        ppu_hash = (ppu_hash * 131 + target + byte + emu.framecount()) % 0x100000000
        if #ppu_tail >= 1200 then table.remove(ppu_tail, 1) end
        local row = table.concat({emu.framecount(), hex4(target), hex2(byte), hex4(read_pc())}, "\t")
        ppu_tail[#ppu_tail + 1] = row
        if ppu_write_count <= 50000 then append(ppu_path, row) end
    end
    ppu_addr = (ppu_addr + ppu_increment) % 0x4000
end

local function log_source_read(target, addr, value)
    if not active[target.id] or source_read_count >= HIT_LIMIT then
        if source_read_count >= HIT_LIMIT then source_read_limit_hit = true end
        return
    end
    source_read_count = source_read_count + 1
    append(reads_path, table.concat({
        emu.framecount(), target.id, target.rom_offset, "$" .. hex4(addr or target.cpu_addr),
        hex2(value or byte_at(addr or target.cpu_addr)), "$" .. hex4(read_pc()), string.format("%08X", ppu_hash)
    }, "\t"))
    if not source_captured[target.id] and not source_pending[target.id] then
        source_pending[target.id] = { target = target, frame = emu.framecount() + 1 }
    end
end

local function dump_ppu(path)
    local f = assert(io.open(path, "wb"))
    for offset = 0, 0x3BF do
        local ok, value = pcall(function() return ppu.readbyte(0x2000 + offset) end)
        if not ok or value == nil then f:close(); return false end
        f:write(string.char(value))
    end
    f:close(); return true
end

local function capture(target, frame)
    local stem = OUT_DIR .. "/" .. target.id
    local ok, shot = pcall(function() return gui.gdscreenshot() end)
    if ok and shot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb")); f:write(shot); f:close()
    end
    dump_ppu(stem .. "_nametable.bin")
    local tail = assert(io.open(stem .. "_ppu_tail.tsv", "w"))
    tail:write("frame\tppu_address\tvalue\tpc\n")
    for _, row in ipairs(ppu_tail) do tail:write(row .. "\n") end
    tail:close()
    captured[target.id] = true
end

local function capture_source(target, frame)
    if source_captured[target.id] then return end
    local stem = OUT_DIR .. "/" .. target.id .. "_source"
    local ok, shot = pcall(function() return gui.gdscreenshot() end)
    if ok and shot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb")); f:write(shot); f:close()
    end
    dump_ppu(stem .. "_nametable.bin")
    local tail = assert(io.open(stem .. "_ppu_tail.tsv", "w"))
    tail:write("frame\tppu_address\tvalue\tpc\n")
    for _, row in ipairs(ppu_tail) do tail:write(row .. "\n") end
    tail:close()
    source_captured[target.id] = true
end

local callbacks = 0
for _, target in ipairs(targets) do
    for index, _ in ipairs(target.bytes) do
        local address = target.cpu_addr + index - 1
        address_targets[address] = address_targets[address] or {}
        address_targets[address][#address_targets[address] + 1] = target
    end
end
for address, list in pairs(address_targets) do
    local callback_ok = register_read(address, function(addr, size, value)
        for _, target in ipairs(list) do log_source_read(target, addr, value) end
    end)
    if callback_ok then callbacks = callbacks + 1 end
end
register_read(0x2002, on_ppu_status)
pcall(function() memory.registerwrite(0x2000, 1, on_ppu_control) end)
pcall(function() memory.registerwrite(0x2005, 1, on_ppu_scroll) end)
pcall(function() memory.registerwrite(0x2006, 1, on_ppu_address) end)
pcall(function() memory.registerwrite(0x2007, 1, on_ppu_data) end)
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)
append(summary_path, table.concat({0, "lua_start", #targets, 0, 0, 0, "callbacks=" .. tostring(callbacks)}, "\t"))

while emu.framecount() < MAX_FRAMES and not source_read_limit_hit do
    local frame = emu.framecount()
    joypad.set(1, frame < 900 and entry_input(frame) or combat_input(frame))
    for _, target in ipairs(targets) do
        local is_active = pattern_at(target.cpu_addr, target.bytes)
        active[target.id] = is_active
        if is_active and not seen[target.id] then
            seen[target.id] = true
            matched = matched + 1
            append(matches_path, table.concat({
                frame, target.id, target.rom_offset, "$" .. hex4(target.cpu_addr), bytes_text(target.bytes),
                string.format("%08X", ppu_hash), ppu_write_count
            }, "\t"))
            pending[target.id] = { target = target, frame = frame + 5 }
        end
    end
    for id, item in pairs(pending) do
        if frame >= item.frame and not captured[id] then
            capture(item.target, frame, "match")
            pending[id] = nil
        end
    end
    for id, item in pairs(source_pending) do
        if frame >= item.frame and not source_captured[id] then
            capture_source(item.target, frame)
            source_pending[id] = nil
        end
    end
    if frame % 600 == 0 then
        local active_count = 0
        for _, is_active in pairs(active) do if is_active then active_count = active_count + 1 end end
        local captured_count = 0
        for _ in pairs(captured) do captured_count = captured_count + 1 end
        append(summary_path, table.concat({frame, "periodic", #targets, matched, active_count, captured_count, "reads=" .. tostring(source_read_count)}, "\t"))
    end
    gui.text(2, 8, "Pre-pointer runtime scan " .. tostring(frame))
    gui.text(2, 17, "matched=" .. tostring(matched) .. " reads=" .. tostring(source_read_count))
    emu.frameadvance()
end

local matched_ids = {}
for _, row in ipairs(targets) do if seen[row.id] then matched_ids[#matched_ids + 1] = row.id end end
local captured_count = 0
for _ in pairs(captured) do captured_count = captured_count + 1 end
append(summary_path, table.concat({
    emu.framecount(), source_read_limit_hit and "hit_limit" or "lua_done", #targets, matched,
    table.concat(matched_ids, ","), captured_count, "callbacks=" .. tostring(callbacks) .. ";reads=" .. tostring(source_read_count)
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
