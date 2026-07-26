-- Bounded MMC3/PPU mapping trace for the known opening-dialogue route.
--
-- This records mapper writes and the PPU background-pattern-table selector
-- only until the fixed opening capture frame. It does not enter free gameplay.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/opening_mapper_trace_capture"
local CAPTURE_FRAME = tonumber(os.getenv("KUNIO_CAPTURE_FRAME") or "883")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "920")

local summary_path = OUT_DIR .. "/summary.tsv"
local writes_path = OUT_DIR .. "/mapper_writes.tsv"
local snapshot_path = OUT_DIR .. "/mapper_snapshot.tsv"
local mapper_control = nil
local mapper_select = nil
local ppu_control = nil
local mapper_registers = {}
local callback_counts = { mapper_select = 0, mapper_data = 0, ppu_control = 0 }
local registered = { mapper_select = false, mapper_data = false, ppu_control = false }
local captured = false

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function hex2(value)
    if value == nil then return "" end
    return string.format("%02X", value % 0x100)
end

local function hex4(value)
    if value == nil then return "" end
    return string.format("%04X", value % 0x10000)
end

local function read_register(name)
    local ok, value = pcall(function() return memory.getregister(name) end)
    if ok and value ~= nil then return value end
    return nil
end

local function route_input(frame)
    -- The successful start_a_menu route, bounded to the opening dialogue.
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

local function register_write(addr, callback)
    if memory.registerwrite == nil then return false end
    local ok = pcall(function() memory.registerwrite(addr, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerwrite(addr, 1, callback) end)
    return ok
end

local function on_mapper_select(addr, size, value)
    mapper_control = value
    mapper_select = value % 8
    callback_counts.mapper_select = callback_counts.mapper_select + 1
    append(writes_path, table.concat({
        emu.framecount(), "MMC3_SELECT", hex2(value), tostring(mapper_select),
        hex4(read_register("pc"))
    }, "\t"))
end

local function on_mapper_data(addr, size, value)
    if mapper_select ~= nil and mapper_select >= 0 and mapper_select <= 7 then
        mapper_registers[mapper_select] = value
    end
    callback_counts.mapper_data = callback_counts.mapper_data + 1
    append(writes_path, table.concat({
        emu.framecount(), "MMC3_DATA", hex2(value),
        mapper_select == nil and "" or tostring(mapper_select),
        hex4(read_register("pc"))
    }, "\t"))
end

local function on_ppu_control(addr, size, value)
    ppu_control = value
    callback_counts.ppu_control = callback_counts.ppu_control + 1
    append(writes_path, table.concat({
        emu.framecount(), "PPUCTRL", hex2(value), "", hex4(read_register("pc"))
    }, "\t"))
end

local function capture()
    append(snapshot_path,
        "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tmapper_select_callbacks\tmapper_data_callbacks\tppu_control_callbacks")
    local values = {
        emu.framecount(),
        hex2(mapper_control),
        mapper_select == nil and "" or tostring(mapper_select),
        hex2(ppu_control),
    }
    for index = 0, 7 do
        values[#values + 1] = hex2(mapper_registers[index])
    end
    values[#values + 1] = tostring(callback_counts.mapper_select)
    values[#values + 1] = tostring(callback_counts.mapper_data)
    values[#values + 1] = tostring(callback_counts.ppu_control)
    append(snapshot_path, table.concat(values, "\t"))
    append(summary_path, table.concat({
        emu.framecount(),
        "capture",
        "registered_select=" .. tostring(registered.mapper_select),
        "registered_data=" .. tostring(registered.mapper_data),
        "registered_ppu_control=" .. tostring(registered.ppu_control),
    }, "\t"))
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tdetail_a\tdetail_b\tdetail_c")
append(writes_path, "frame\tkind\tvalue\tselected_register\tpc")
registered.mapper_select = register_write(0x8000, on_mapper_select)
registered.mapper_data = register_write(0x8001, on_mapper_data)
registered.ppu_control = register_write(0x2000, on_ppu_control)

append(summary_path, table.concat({
    0,
    "lua_start",
    "capture_frame=" .. tostring(CAPTURE_FRAME),
    "max_frames=" .. tostring(MAX_FRAMES),
    "mapper_callbacks=" .. tostring(registered.mapper_select and registered.mapper_data),
}, "\t"))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and not captured do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "Opening MMC3 trace frame " .. tostring(frame))
    gui.text(2, 17, "mapper writes=" .. tostring(callback_counts.mapper_data))
    emu.frameadvance()
    if emu.framecount() >= CAPTURE_FRAME then
        capture()
        captured = true
    end
end

append(summary_path, table.concat({
    emu.framecount(),
    captured and "lua_done" or "frame_limit",
    "captured=" .. tostring(captured),
    "mapper_data_callbacks=" .. tostring(callback_counts.mapper_data),
    "ppu_control_callbacks=" .. tostring(callback_counts.ppu_control),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
