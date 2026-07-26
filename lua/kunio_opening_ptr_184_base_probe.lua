-- Bounded context probe for the third opening dialogue record.
--
-- This follows only the already-proven title/menu route, acknowledges the
-- first two opening dialogue records once each, and stops as soon as pointer
-- 184 is read and captured. It never enters free-form gameplay.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/opening_ptr_184_base_probe_capture"
local TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or "kunio_opening_ptr_184_base_target.lua"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1430")
local HIT_LIMIT = tonumber(os.getenv("KUNIO_HIT_LIMIT") or "5000")
local FIRST_ADVANCE_START = tonumber(os.getenv("KUNIO_FIRST_ADVANCE_START") or "900")
local FIRST_ADVANCE_END = tonumber(os.getenv("KUNIO_FIRST_ADVANCE_END") or "910")
local SECOND_ADVANCE_START = tonumber(os.getenv("KUNIO_SECOND_ADVANCE_START") or "1110")
local SECOND_ADVANCE_END = tonumber(os.getenv("KUNIO_SECOND_ADVANCE_END") or "1120")
local SETTLE_FRAMES = tonumber(os.getenv("KUNIO_SETTLE_FRAMES") or "18")

local summary_path = OUT_DIR .. "/summary.tsv"
local reads_path = OUT_DIR .. "/opening_target_reads.tsv"
local record_path = OUT_DIR .. "/opening_target_record.tsv"
local hit_count = 0
local registered_count = 0
local complete_frame = nil
local captured = false
local stopped_for_limit = false

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function hex2(value)
    return string.format("%02X", (value or 0) % 0x100)
end

local function hex4(value)
    return string.format("%04X", (value or 0) % 0x10000)
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

local function dump_range(path, start_addr, length, domain)
    local f = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        f:write(string.char(byte_at(start_addr + offset, domain)))
    end
    f:close()
end

local function parse_bytes(text)
    local values = {}
    for token in string.gmatch(text or "", "%x%x") do
        values[#values + 1] = tonumber(token, 16)
    end
    return values
end

local function record_snapshot(target)
    local values = {}
    for addr = target.start, target.stop do
        values[#values + 1] = hex2(byte_at(addr))
    end
    return table.concat(values, " ")
end

local function record_matches(target)
    local expected = parse_bytes(target.bytes)
    if #expected ~= target.stop - target.start + 1 then return false end
    for index, value in ipairs(expected) do
        if byte_at(target.start + index - 1) ~= value then return false end
    end
    return true
end

local function route_input(frame)
    if frame >= 40 and frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    if frame >= 480 and frame < 490 then return { down = true } end
    if frame >= 540 and frame < 550 then return { A = true } end
    if frame >= 700 and frame < 712 then return { B = true } end

    -- Two deliberately bounded dialogue acknowledgements. No input is sent
    -- after the second one, even if the target is not reached.
    if frame >= FIRST_ADVANCE_START and frame < FIRST_ADVANCE_END then return { B = true } end
    if frame >= SECOND_ADVANCE_START and frame < SECOND_ADVANCE_END then return { B = true } end
    return {}
end

local function on_read_for(target)
    return function(addr, size, value)
        if hit_count >= HIT_LIMIT then
            stopped_for_limit = true
            return
        end
        hit_count = hit_count + 1
        local matches = record_matches(target)
        append(reads_path, table.concat({
            emu.framecount(),
            target.label,
            "$" .. hex4(addr or 0),
            hex2(value or byte_at(addr or 0)),
            tostring(matches),
            record_snapshot(target),
        }, "\t"))
        if matches and complete_frame == nil and hit_count >= (target.stop - target.start + 1) then
            complete_frame = emu.framecount()
        end
    end
end

local function register_read(addr, callback)
    if memory.registerread == nil then return false end
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerread(addr, 1, callback) end)
    return ok
end

local function capture(target)
    local frame = emu.framecount()
    local stem = OUT_DIR .. "/opening_dialogue_frame_" .. string.format("%06d", frame)
    local screenshot_ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if screenshot_ok and screenshot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb"))
        f:write(screenshot)
        f:close()
    end
    dump_range(stem .. "_cpu_ram.bin", 0x0000, 0x0800)
    dump_range(stem .. "_sram_6000_7fff.bin", 0x6000, 0x2000)
    dump_range(stem .. "_nametable_2000_23bf.bin", 0x2000, 0x03C0, "ppu")
    append(record_path, "frame\tlabel\tcpu_range\texpected_bytes\tactive_expected_match\trecord_snapshot")
    append(record_path, table.concat({
        frame,
        target.label,
        "$" .. hex4(target.start) .. "-$" .. hex4(target.stop),
        target.bytes,
        tostring(record_matches(target)),
        record_snapshot(target),
    }, "\t"))
    append(summary_path, table.concat({
        frame,
        "capture",
        registered_count,
        hit_count,
        "screenshot=" .. tostring(screenshot_ok) .. ";target_match=" .. tostring(record_matches(target)),
    }, "\t"))
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tregistered\thits\tdetail")
append(reads_path, "frame\tlabel\tcpu_addr\tvalue\tactive_expected_match\trecord_snapshot")

local targets = assert(dofile(TARGETS_LUA), "target definition could not be loaded")
local target = assert(targets[1], "opening target definition is empty")
for addr = target.start, target.stop do
    if register_read(addr, on_read_for(target)) then
        registered_count = registered_count + 1
    end
end

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)
append(summary_path, table.concat({
    0,
    "lua_start",
    registered_count,
    0,
    "advance=" .. tostring(FIRST_ADVANCE_START) .. "-" .. tostring(FIRST_ADVANCE_END) .. "," .. tostring(SECOND_ADVANCE_START) .. "-" .. tostring(SECOND_ADVANCE_END) .. ";target=" .. target.label,
}, "\t"))

while emu.framecount() < MAX_FRAMES and not captured and not stopped_for_limit do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "Opening pointer 184 probe frame " .. tostring(frame))
    gui.text(2, 17, "target reads=" .. tostring(hit_count))
    emu.frameadvance()
    if complete_frame ~= nil and emu.framecount() >= complete_frame + SETTLE_FRAMES then
        capture(target)
        captured = true
    end
end

local final_reason = "target_not_seen"
if captured then final_reason = "lua_done" end
if stopped_for_limit then final_reason = "hit_limit" end
append(summary_path, table.concat({
    emu.framecount(),
    final_reason,
    registered_count,
    hit_count,
    "captured=" .. tostring(captured) .. ";complete_frame=" .. tostring(complete_frame),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
