-- Bounded name-entry probe for the Koganemushi secret.
-- This only explores the documented early-game entry point and records
-- screen/RAM evidence. It does not write ROM, SRAM, or CPU memory.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."
local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/name_entry_probe")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "900")
local SELECT_FRAME = tonumber(os.getenv("KUNIO_NAME_SELECT_FRAME") or "1000")
local SECOND_SELECT_FRAME = tonumber(os.getenv("KUNIO_NAME_SECOND_SELECT_FRAME") or "-1")
local SNAPSHOT_GAP = tonumber(os.getenv("KUNIO_NAME_SNAPSHOT_GAP") or "30")
local UNIQUE_LIMIT = tonumber(os.getenv("KUNIO_NAME_UNIQUE_LIMIT") or "24")
local FORCE_CAPTURE_FRAME = tonumber(os.getenv("KUNIO_FORCE_CAPTURE_FRAME") or "-1")
local FORCE_CAPTURE_GAP = tonumber(os.getenv("KUNIO_FORCE_CAPTURE_GAP") or "300")
local SETUP_ROUTE = os.getenv("KUNIO_NAME_SETUP_ROUTE") == "1"
local KOGANEMUSHI_ROUTE = os.getenv("KUNIO_KOGANEMUSHI") == "1"
local CHEAT_START_FRAME = tonumber(os.getenv("KUNIO_CHEAT_START_FRAME") or "2300")
local CHEAT_PULSE = tonumber(os.getenv("KUNIO_CHEAT_PULSE") or "8")
local CHEAT_GAP = tonumber(os.getenv("KUNIO_CHEAT_GAP") or "18")

local cheat_events = {}
local cheat_cursor = CHEAT_START_FRAME
local function add_cheat_button(button, count)
    for _ = 1, count do
        cheat_events[#cheat_events + 1] = { frame = cheat_cursor, button = button }
        cheat_cursor = cheat_cursor + CHEAT_GAP
    end
end
-- Koganemushi coordinates from the documented grid route, starting at the
-- first cell: (5,2), (1,2), B, (11,1), (4,5), (8,2), (2,3), END.
add_cheat_button("down", 1)
add_cheat_button("right", 4)
add_cheat_button("A", 1)
add_cheat_button("left", 4)
add_cheat_button("A", 1)
add_cheat_button("B", 1)
add_cheat_button("up", 1)
add_cheat_button("right", 10)
add_cheat_button("A", 1)
add_cheat_button("down", 4)
add_cheat_button("left", 7)
add_cheat_button("A", 1)
add_cheat_button("up", 3)
add_cheat_button("right", 4)
add_cheat_button("A", 1)
add_cheat_button("down", 1)
add_cheat_button("left", 6)
add_cheat_button("A", 1)
add_cheat_button("down", 3)
add_cheat_button("right", 10)
add_cheat_button("A", 1)
add_cheat_button("A", 1)

-- Optional one-cell calibration keeps cursor experiments separate from the full
-- Koganemushi candidate route.
local CALIBRATION_ROUTE = os.getenv("KUNIO_NAME_CALIBRATION") or ""
if CALIBRATION_ROUTE ~= "" then
    cheat_events = {}
    cheat_cursor = CHEAT_START_FRAME
    if CALIBRATION_ROUTE == "right_a" then
        add_cheat_button("right", 1)
        add_cheat_button("A", 1)
    elseif CALIBRATION_ROUTE == "down_a" then
        add_cheat_button("down", 1)
        add_cheat_button("A", 1)
    elseif CALIBRATION_ROUTE == "right2_a" then
        add_cheat_button("right", 2)
        add_cheat_button("A", 1)
    else
        error("unknown KUNIO_NAME_CALIBRATION route: " .. CALIBRATION_ROUTE)
    end
end
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
local function hex4(value) return string.format("%04X", (value or 0) % 0x10000) end
local cursor_trace_path = nil
local function register_cursor_write(address)
    local callback = function(write_address, size, value)
        local pc = 0
        pcall(function() pc = memory.getregister("pc") end)
        append(cursor_trace_path, table.concat({
            emu.framecount(), hex4(write_address), hex2(value), hex4(pc),
        }, "\t"))
    end
    pcall(function() memory.registerwrite(address, 1, callback) end)
end
local function dump_range(path, start_address, length, domain)
    local f = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        f:write(string.char(byte_at(start_address + offset, domain)))
    end
    f:close()
end
local function fingerprint()
    local hash = 0
    for address = 0x2000, 0x23BF, 8 do
        hash = (hash * 131 + byte_at(address, "ppu") + address) % 1000000007
    end
    return tostring(hash)
end
local function dump_screen(frame, phase)
    local stem = string.format("%s/frame_%06d", OUT_DIR, frame)
    dump_range(stem .. "_nametable_2000_23ff.bin", 0x2000, 0x400, "ppu")
    dump_range(stem .. "_cpu_ram.bin", 0x0000, 0x800, nil)
    dump_range(stem .. "_sram_6000_7fff.bin", 0x6000, 0x2000, nil)
    local ok, shot = pcall(function() return gui.gdscreenshot() end)
    if ok and shot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb")); f:write(shot); f:close()
    end
    append(OUT_DIR .. "/captures.tsv", table.concat({
        frame, phase, fingerprint(), ok and "true" or "false",
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)),
        hex2(byte_at(0x04FC)), hex2(byte_at(0x0502)), hex2(byte_at(0x0503)),
        hex2(byte_at(0x0700)), hex2(byte_at(0x0701)), hex2(byte_at(0x0702)),
    }, "\t"))
end

local function input_for(frame)
    -- Reuse the bounded opening/menu route already proven against the English
    -- reference. The SELECT timing is an experiment parameter after the
    -- character setup has been reached.
    if frame >= 40 and frame < 50 then return { start = true }, "title_start" end
    if frame >= 130 and frame < 140 then return { A = true }, "title" end
    if frame >= 220 and frame < 230 then return { start = true }, "opening_setup" end
    if frame >= 300 and frame < 310 then return { down = true }, "opening_setup" end
    if frame >= 360 and frame < 370 then return { A = true }, "opening_setup" end
    if frame >= 480 and frame < 490 then return { down = true }, "opening_setup" end
    if frame >= 540 and frame < 550 then return { A = true }, "opening_setup" end
    if frame >= 700 and frame < 712 then return { B = true }, "opening_setup" end
    if frame >= 880 and frame < 892 then return { A = true }, "character_setup" end
    if frame >= 940 and frame < 952 then return { A = true }, "character_setup" end
    if KOGANEMUSHI_ROUTE and frame >= CHEAT_START_FRAME then
        for _, event in ipairs(cheat_events) do
            if frame >= event.frame and frame < event.frame + CHEAT_PULSE then
                return { [event.button] = true }, "koganemushi_" .. event.button
            end
        end
    end
    if SETUP_ROUTE then
        -- Finish the proven initial character/mode setup first. The first
        -- SETUP screen seen here is not the Start menu.
        if frame >= 1040 and frame < 1052 then return { start = true }, "initial_setup" end
        if frame >= 1082 and frame < 1094 then return { down = true }, "initial_setup" end
        if frame >= 1124 and frame < 1136 then return { A = true }, "initial_setup" end
        if frame >= 1166 and frame < 1178 then return { down = true }, "initial_setup" end
        if frame >= 1208 and frame < 1220 then return { A = true }, "initial_setup" end
        if frame >= 1250 and frame < 1262 then return { B = true }, "initial_setup" end
        if frame >= 1340 and frame < 1352 then return { select = true }, "initial_setup" end
        if frame >= 1382 and frame < 1394 then return { down = true }, "initial_setup" end
        if frame >= 1424 and frame < 1436 then return { A = true }, "initial_setup" end
        if frame >= 1466 and frame < 1478 then return { right = true }, "initial_setup" end
        if frame >= 1508 and frame < 1520 then return { A = true }, "initial_setup" end
        if frame >= 1550 and frame < 1562 then return { B = true }, "initial_setup" end
        -- Now use Method 2: open the Start menu, move ITEMS -> SETUP,
        -- confirm, and press SELECT on the Setup screen.
        if frame >= 1640 and frame < 1652 then return { start = true }, "menu_open" end
        if frame >= 1700 and frame < 1712 then return { right = true }, "menu_setup" end
        if frame >= 1760 and frame < 1772 then return { right = true }, "menu_setup" end
        if frame >= 1820 and frame < 1832 then return { right = true }, "menu_setup" end
        if frame >= 1880 and frame < 1892 then return { down = true }, "menu_setup" end
        if frame >= 1960 and frame < 1972 then return { A = true }, "menu_setup" end
        if frame >= 2100 and frame < 2112 then return { select = true }, "name_entry" end
        if (not KOGANEMUSHI_ROUTE) and frame >= 2240 and frame < 2252 then return { select = true }, "name_entry_retry" end

    elseif frame >= SELECT_FRAME and frame < SELECT_FRAME + 10 then
        return { select = true }, "select_probe"
    end
    if SECOND_SELECT_FRAME >= 0 and frame >= SECOND_SELECT_FRAME and frame < SECOND_SELECT_FRAME + 10 then
        return { select = true }, "second_select_probe"
    end
    return {}, "wait"
end

mkdir(OUT_DIR)
append(OUT_DIR .. "/captures.tsv", "frame\tphase\tfingerprint\tscreenshot\t04F1\t04FA\t04FB\t04FC\t0502\t0503\t0700\t0701\t0702")
append(OUT_DIR .. "/route.tsv", table.concat({
    "select_frame=" .. tostring(SELECT_FRAME),
    "second_select_frame=" .. tostring(SECOND_SELECT_FRAME),
    "max_frames=" .. tostring(MAX_FRAMES),
}, "\t"))

cursor_trace_path = OUT_DIR .. "/cursor_write_trace.tsv"
append(cursor_trace_path, "frame\taddress\tvalue\tpc")
for _, address in ipairs({0x04FA, 0x04FB, 0x04FC, 0x0502, 0x0503, 0x0700, 0x0701, 0x0702}) do
    register_cursor_write(address)
end
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)
local last_fingerprint = nil
local last_capture = -999999
local last_forced_capture = -999999
local unique = 0

while emu.framecount() < MAX_FRAMES and unique < UNIQUE_LIMIT do
    local frame = emu.framecount()
    local buttons, phase = input_for(frame)
    joypad.set(1, buttons)
    emu.frameadvance()
    if FORCE_CAPTURE_FRAME >= 0 and frame >= FORCE_CAPTURE_FRAME and frame - last_forced_capture >= FORCE_CAPTURE_GAP then
        last_forced_capture = frame
        dump_screen(frame, "forced")
    end
    if frame >= 90 and frame - last_capture >= SNAPSHOT_GAP then
        local current = fingerprint()
        if current ~= last_fingerprint then
            last_fingerprint = current
            last_capture = frame
            unique = unique + 1
            dump_screen(frame, phase)
        end
    end
end

append(OUT_DIR .. "/route.tsv", table.concat({ "end", emu.framecount(), "unique=" .. tostring(unique) }, "\t"))
append(OUT_DIR .. "/summary.tsv", table.concat({ "lua_done", emu.framecount(), "unique=" .. tostring(unique) }, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
