-- Bounded base/English context capture for the reachable main menu.
--
-- The route is fixed from the recorded menu entry sequence. It never enters
-- combat or general gameplay. It captures one known menu frame and exits.
-- PPU bytes are read through FCEUX's `ppu` API, not the CPU memory API.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/main_menu_context_capture"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1920")
local CAPTURE_FRAME = tonumber(os.getenv("KUNIO_MENU_CAPTURE_FRAME") or "1906")
local PPU_TRACE_START = tonumber(os.getenv("KUNIO_PPU_TRACE_START") or "1600")
local PPU_WRITE_LIMIT = tonumber(os.getenv("KUNIO_PPU_WRITE_LIMIT") or "120000")
local EXTRA_BUTTON = os.getenv("KUNIO_MENU_EXTRA_BUTTON") or ""
local EXTRA_START = tonumber(os.getenv("KUNIO_MENU_EXTRA_START") or "")
local EXTRA_DURATION = tonumber(os.getenv("KUNIO_MENU_EXTRA_DURATION") or "12")
-- Optional, bounded source windows for a named menu sub-screen.  This keeps
-- source proof narrow: callers provide comma-separated CPU ranges such as
-- B600-B7FF,BC00-BC3F rather than tracing gameplay or the full PRG space.
local EXTRA_SOURCE_RANGES_RAW = os.getenv("KUNIO_EXTRA_SOURCE_RANGES") or ""
local EXTRA_SOURCE_READ_LIMIT = tonumber(os.getenv("KUNIO_EXTRA_SOURCE_READ_LIMIT") or "4000")
local EXTRA_SOURCE_TRACE_START = tonumber(os.getenv("KUNIO_EXTRA_SOURCE_TRACE_START") or tostring(PPU_TRACE_START))
local DUMP_SRAM = os.getenv("KUNIO_DUMP_SRAM") == "1"
-- Queue buffers are RAM-backed and can be watched independently of the
-- switchable PRG source.  They expose the final tile bytes before PPUDATA.
local QUEUE_WRITE_RANGES_RAW = os.getenv("KUNIO_QUEUE_WRITE_RANGES") or ""
local QUEUE_WRITE_LIMIT = tonumber(os.getenv("KUNIO_QUEUE_WRITE_LIMIT") or "1000")
local QUEUE_WRITE_TRACE_START = tonumber(os.getenv("KUNIO_QUEUE_WRITE_TRACE_START") or tostring(EXTRA_SOURCE_TRACE_START))
local RELATIVE_FRAMES = os.getenv("KUNIO_RELATIVE_FRAMES") == "1"
local SCRIPT_START_FRAME = emu.framecount()

local function trace_frame()
    local frame = emu.framecount()
    if RELATIVE_FRAMES then
        return frame - SCRIPT_START_FRAME
    end
    return frame
end
-- Fixed PRG Bank 7 menu-template span: ROM 0x1F2D0-0x1F33D maps to CPU
-- $F2C0-$F32D. The English reference changes the eight visible labels here.
local MENU_SOURCE_CPU_START = 0xF2C0
local MENU_SOURCE_CPU_END = 0xF32E

local summary_path = OUT_DIR .. "/summary.tsv"
local route_path = OUT_DIR .. "/route.tsv"
local mapper_writes_path = OUT_DIR .. "/mapper_writes.tsv"
local mapper_snapshot_path = OUT_DIR .. "/mapper_snapshot.tsv"
local ppu_writes_path = OUT_DIR .. "/ppu_writes.tsv"
local ppu_rows_path = OUT_DIR .. "/ppu_rows.tsv"
local source_reads_path = OUT_DIR .. "/menu_source_reads.tsv"
local extra_source_reads_path = OUT_DIR .. "/extra_source_reads.tsv"
local queue_writes_path = OUT_DIR .. "/queue_writes.tsv"
local mapper_config_writes_path = OUT_DIR .. "/mapper_config_writes.tsv"
local mapper_loader_exec_path = OUT_DIR .. "/mapper_loader_exec.tsv"

local captured = false
local mapper_control = nil
local mapper_select = nil
local ppu_control = nil
local mapper_registers = {}
local callback_counts = {
    mapper_select = 0,
    mapper_data = 0,
    ppu_control = 0,
    ppu_status = 0,
    ppu_addr = 0,
    ppu_data = 0,
    menu_source = 0,
    extra_source = 0,
    queue_write = 0,
    mapper_config = 0,
    mapper_loader = 0,
}
local registered = {
    mapper_select = false,
    mapper_data = false,
    ppu_control = false,
    ppu_status = false,
    ppu_addr = false,
    ppu_data = false,
    menu_source = false,
    extra_source = false,
    queue_write = false,
    mapper_config = false,
    mapper_loader = false,
}
local ppu_addr_high = nil
local ppu_addr = 0
local ppu_increment = 1
local ppu_write_count = 0
local ppu_write_limit_reached = false
local extra_source_read_count = 0
local extra_source_read_limit_reached = false
local queue_write_count = 0
local queue_write_limit_reached = false
local valid_buttons = {
    A = true,
    B = true,
    start = true,
    select = true,
    up = true,
    down = true,
    left = true,
    right = true,
}

if EXTRA_BUTTON ~= "" and not valid_buttons[EXTRA_BUTTON] then
    error("KUNIO_MENU_EXTRA_BUTTON must name one controller button")
end
if EXTRA_BUTTON ~= "" and (EXTRA_START == nil or EXTRA_DURATION == nil or EXTRA_DURATION <= 0) then
    error("KUNIO_MENU_EXTRA_BUTTON requires a positive start and duration")
end
if EXTRA_SOURCE_READ_LIMIT == nil or EXTRA_SOURCE_READ_LIMIT <= 0 then
    error("KUNIO_EXTRA_SOURCE_READ_LIMIT must be positive")
end
if EXTRA_SOURCE_TRACE_START == nil or EXTRA_SOURCE_TRACE_START < 0 then
    error("KUNIO_EXTRA_SOURCE_TRACE_START must be non-negative")
end
if QUEUE_WRITE_LIMIT == nil or QUEUE_WRITE_LIMIT <= 0 then
    error("KUNIO_QUEUE_WRITE_LIMIT must be positive")
end
if QUEUE_WRITE_TRACE_START == nil or QUEUE_WRITE_TRACE_START < 0 then
    error("KUNIO_QUEUE_WRITE_TRACE_START must be non-negative")
end

local function parse_hex_ranges(raw, lower_bound, upper_bound, env_name, example)
    local ranges = {}
    if raw == "" then return ranges end
    for token in string.gmatch(raw, "[^,]+") do
        local start_text, end_text = string.match(token, "^%s*([%x]+)%s*%-%s*([%x]+)%s*$")
        if start_text == nil or end_text == nil then
            error(env_name .. " must use hex ranges such as " .. example)
        end
        local start_address = tonumber(start_text, 16)
        local end_address = tonumber(end_text, 16)
        if start_address == nil or end_address == nil or start_address > end_address then
            error(env_name .. " contains an invalid range")
        end
        if start_address < lower_bound or end_address > upper_bound then
            error(env_name .. " contains an address outside its allowed window")
        end
        ranges[#ranges + 1] = { start_address = start_address, end_address = end_address }
    end
    return ranges
end

local EXTRA_SOURCE_RANGES = parse_hex_ranges(
    EXTRA_SOURCE_RANGES_RAW, 0x8000, 0xBFFF,
    "KUNIO_EXTRA_SOURCE_RANGES", "B600-B7FF"
)
local QUEUE_WRITE_RANGES = parse_hex_ranges(
    QUEUE_WRITE_RANGES_RAW, 0x0000, 0x7FFF,
    "KUNIO_QUEUE_WRITE_RANGES", "6360-6380"
)

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local handle = assert(io.open(path, "a"))
    handle:write(line .. "\n")
    handle:close()
end

local function hex2(value)
    if value == nil then return "" end
    return string.format("%02X", value % 0x100)
end

local function hex4(value)
    if value == nil then return "" end
    return string.format("%04X", value % 0x10000)
end

local function read_cpu_byte(address)
    local ok, value = pcall(function() return memory.readbyte(address) end)
    if ok and value ~= nil then return value end
    return 0
end

local function read_ppu_byte(address)
    local ok, value = pcall(function() return ppu.readbyte(address) end)
    if ok and value ~= nil then return value end
    return nil
end

local function read_register(name)
    local ok, value = pcall(function() return memory.getregister(name) end)
    if ok and value ~= nil then return value end
    return nil
end

local function dump_cpu_range(path, start_addr, length)
    local handle = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        handle:write(string.char(read_cpu_byte(start_addr + offset)))
    end
    handle:close()
end

local function dump_ppu_range(path, start_addr, length)
    local handle = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        local value = read_ppu_byte(start_addr + offset)
        if value == nil then
            handle:close()
            return false
        end
        handle:write(string.char(value))
    end
    handle:close()
    return true
end

local function nametable_fingerprint(start_addr, length)
    local hash = 0
    local sum = 0
    for address = start_addr, start_addr + length - 1 do
        local value = read_ppu_byte(address)
        if value == nil then return "unavailable" end
        hash = (hash * 131 + value + address) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end

local function capture_ppu_rows()
    for nametable = 0, 3 do
        local start_addr = 0x2000 + nametable * 0x400
        for row = 0, 29 do
            local values = {}
            for column = 0, 31 do
                values[#values + 1] = hex2(read_ppu_byte(start_addr + row * 32 + column))
            end
            append(ppu_rows_path, table.concat({ nametable, row, table.concat(values, " ") }, "\t"))
        end
    end
end

local function register_write(address, size, callback)
    local ok = pcall(function() memory.registerwrite(address, size, callback) end)
    if ok then return true end
    if size == 1 then
        ok = pcall(function() memory.registerwrite(address, callback) end)
    end
    return ok
end

local function register_read(address, callback)
    local ok = pcall(function() memory.registerread(address, 1, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerread(address, callback) end)
    return ok
end

local function register_exec(address, callback)
    local ok = pcall(function() memory.registerexec(address, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerexecute(address, callback) end)
    return ok
end

local function append_mapper_write(kind, value, selected_register)
    -- The MMC3 registers can be updated many times during the opening. Keep
    -- their current state from frame zero, but persist only the final menu
    -- window so trace I/O cannot slow the bounded route into a pseudo-stall.
    if trace_frame() < PPU_TRACE_START then return end
    append(mapper_writes_path, table.concat({
        trace_frame(), kind, hex2(value), selected_register or "",
        hex4(read_register("pc")),
    }, "\t"))
end

local function on_mapper_select(addr, size, value)
    mapper_control = value
    mapper_select = value % 8
    callback_counts.mapper_select = callback_counts.mapper_select + 1
    append_mapper_write("MMC3_SELECT", value, tostring(mapper_select))
end

local function on_mapper_data(addr, size, value)
    if mapper_select ~= nil and mapper_select >= 0 and mapper_select <= 7 then
        mapper_registers[mapper_select] = value
    end
    callback_counts.mapper_data = callback_counts.mapper_data + 1
    append_mapper_write(
        "MMC3_DATA",
        value,
        mapper_select == nil and "" or tostring(mapper_select)
    )
end

local function on_ppu_control(addr, size, value)
    ppu_control = value
    ppu_increment = (math.floor(value / 4) % 2 == 1) and 32 or 1
    callback_counts.ppu_control = callback_counts.ppu_control + 1
    append_mapper_write("PPUCTRL", value, "")
end

local function on_ppu_status_read(addr, size, value)
    ppu_addr_high = nil
    callback_counts.ppu_status = callback_counts.ppu_status + 1
end

local function on_ppuaddr_write(addr, size, value)
    local byte = value or 0
    if ppu_addr_high == nil then
        ppu_addr_high = byte % 0x40
    else
        ppu_addr = ppu_addr_high * 0x100 + byte
        ppu_addr_high = nil
    end
    callback_counts.ppu_addr = callback_counts.ppu_addr + 1
end

local function on_ppudata_write(addr, size, value)
    local frame = trace_frame()
    local target = ppu_addr % 0x4000
    if frame >= PPU_TRACE_START and target >= 0x2000 and target < 0x23C0 and not ppu_write_limit_reached then
        if ppu_write_count >= PPU_WRITE_LIMIT then
            ppu_write_limit_reached = true
        else
            append(ppu_writes_path, table.concat({
                frame,
                hex4(target),
                hex2(value or 0),
                hex4(read_register("pc")),
            }, "\t"))
            ppu_write_count = ppu_write_count + 1
        end
    end
    ppu_addr = (ppu_addr + ppu_increment) % 0x4000
    callback_counts.ppu_data = callback_counts.ppu_data + 1
end

local function on_menu_source_read(addr, size, value)
    callback_counts.menu_source = callback_counts.menu_source + 1
    if trace_frame() < PPU_TRACE_START then return end
    append(source_reads_path, table.concat({
        trace_frame(),
        hex4(addr),
        hex2(value or 0),
        hex4(read_register("pc")),
        hex2(read_register("a")),
        hex2(read_register("x")),
        hex2(read_register("y")),
    }, "\t"))
end

local function on_extra_source_read(addr, size, value)
    callback_counts.extra_source = callback_counts.extra_source + 1
    local frame = trace_frame()
    if frame < EXTRA_SOURCE_TRACE_START or extra_source_read_limit_reached then return end
    if extra_source_read_count >= EXTRA_SOURCE_READ_LIMIT then
        extra_source_read_limit_reached = true
        return
    end
    append(extra_source_reads_path, table.concat({
        frame,
        hex4(addr),
        hex2(value or 0),
        hex4(read_register("pc")),
        hex2(read_register("a")),
        hex2(read_register("x")),
        hex2(read_register("y")),
        hex2(mapper_control),
        hex2(mapper_registers[6]),
        hex2(mapper_registers[7]),
    }, "\t"))
    extra_source_read_count = extra_source_read_count + 1
end

local function on_queue_write(addr, size, value)
    callback_counts.queue_write = callback_counts.queue_write + 1
    local frame = trace_frame()
    if frame < QUEUE_WRITE_TRACE_START or queue_write_limit_reached then return end
    if queue_write_count >= QUEUE_WRITE_LIMIT then
        queue_write_limit_reached = true
        return
    end
    append(queue_writes_path, table.concat({
        frame,
        hex4(addr),
        hex2(value or 0),
        hex4(read_register("pc")),
        hex2(read_register("a")),
        hex2(read_register("x")),
        hex2(read_register("y")),
        hex2(mapper_control),
        hex2(mapper_registers[6]),
        hex2(mapper_registers[7]),
    }, "\t"))
    queue_write_count = queue_write_count + 1
end

local function on_mapper_config_write(addr, size, value)
    callback_counts.mapper_config = callback_counts.mapper_config + 1
    if trace_frame() < PPU_TRACE_START then return end
    append(mapper_config_writes_path, table.concat({
        trace_frame(),
        hex4(addr or 0),
        hex2(value or 0),
        hex4(read_register("pc")),
        hex2(read_register("a")),
        hex2(read_register("x")),
        hex2(read_register("y")),
        hex2(read_cpu_byte(0x0502)),
        hex2(read_cpu_byte(0x0503)),
    }, "\t"))
end

local function on_mapper_loader_exec()
    callback_counts.mapper_loader = callback_counts.mapper_loader + 1
    if trace_frame() < PPU_TRACE_START then return end
    local stack = read_register("s")
    local return_address = nil
    local caller_return_address = nil
    local saved_r0 = nil
    local saved_r1 = nil
    if stack ~= nil then
        local low = read_cpu_byte(0x0100 + ((stack + 1) % 0x100))
        local high = read_cpu_byte(0x0100 + ((stack + 2) % 0x100))
        return_address = (low + high * 0x100 + 1) % 0x10000
        saved_r1 = read_cpu_byte(0x0100 + ((stack + 3) % 0x100))
        saved_r0 = read_cpu_byte(0x0100 + ((stack + 4) % 0x100))
        -- $EE3F saves the prior R0/R1 values with two PHA instructions before
        -- it calls the mapper loader. Skip those two bytes to reach its caller.
        local caller_low = read_cpu_byte(0x0100 + ((stack + 5) % 0x100))
        local caller_high = read_cpu_byte(0x0100 + ((stack + 6) % 0x100))
        caller_return_address = (caller_low + caller_high * 0x100 + 1) % 0x10000
    end
    append(mapper_loader_exec_path, table.concat({
        trace_frame(),
        hex4(read_register("pc")),
        hex2(stack),
        hex4(return_address),
        hex4(caller_return_address),
        hex2(saved_r0),
        hex2(saved_r1),
        hex2(read_cpu_byte(0x0028)),
        hex2(read_cpu_byte(0x0700)),
        hex2(read_cpu_byte(0x0502)),
        hex2(read_cpu_byte(0x0503)),
        hex2(read_register("a")),
        hex2(read_register("x")),
        hex2(read_register("y")),
    }, "\t"))
end

local function route_input(frame)
    -- Title and opening setup. No input is sent after frame 1861.
    if frame >= 40 and frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    if frame >= 480 and frame < 490 then return { down = true } end
    if frame >= 540 and frame < 550 then return { A = true } end
    if frame >= 700 and frame < 712 then return { B = true } end
    if frame >= 880 and frame < 892 then return { A = true } end
    if frame >= 940 and frame < 952 then return { A = true } end

    -- First known menu-state setup route.
    if frame >= 1040 and frame < 1052 then return { start = true } end
    if frame >= 1082 and frame < 1094 then return { down = true } end
    if frame >= 1124 and frame < 1136 then return { A = true } end
    if frame >= 1166 and frame < 1178 then return { down = true } end
    if frame >= 1208 and frame < 1220 then return { A = true } end
    if frame >= 1250 and frame < 1262 then return { B = true } end

    -- Second known menu-state setup route.
    if frame >= 1340 and frame < 1352 then return { select = true } end
    if frame >= 1382 and frame < 1394 then return { down = true } end
    if frame >= 1424 and frame < 1436 then return { A = true } end
    if frame >= 1466 and frame < 1478 then return { right = true } end
    if frame >= 1508 and frame < 1520 then return { A = true } end
    if frame >= 1550 and frame < 1562 then return { B = true } end

    -- Final main-menu route. The capture happens after its B return.
    if frame >= 1640 and frame < 1652 then return { start = true } end
    if frame >= 1682 and frame < 1694 then return { right = true } end
    if frame >= 1724 and frame < 1736 then return { A = true } end
    if frame >= 1766 and frame < 1778 then return { down = true } end
    if frame >= 1808 and frame < 1820 then return { A = true } end
    if frame >= 1850 and frame < 1862 then return { B = true } end
    if EXTRA_BUTTON ~= "" and frame >= EXTRA_START and frame < EXTRA_START + EXTRA_DURATION then
        return { [EXTRA_BUTTON] = true }
    end
    return {}
end

local function capture_mapper_snapshot()
    local values = {
        trace_frame(),
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
    values[#values + 1] = tostring(callback_counts.ppu_status)
    values[#values + 1] = tostring(callback_counts.ppu_addr)
    values[#values + 1] = tostring(callback_counts.ppu_data)
    values[#values + 1] = tostring(callback_counts.menu_source)
    append(mapper_snapshot_path, table.concat(values, "\t"))
end

local function capture()
    local frame = trace_frame()
    local stem = OUT_DIR .. "/main_menu_frame_" .. string.format("%06d", frame)
    local screenshot_ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if screenshot_ok and screenshot ~= nil then
        local handle = assert(io.open(stem .. "_screen.gd", "wb"))
        handle:write(screenshot)
        handle:close()
    end
    dump_cpu_range(stem .. "_cpu_ram.bin", 0x0000, 0x0800)
    if DUMP_SRAM then
        dump_cpu_range(stem .. "_sram_6000_7fff.bin", 0x6000, 0x2000)
    end
    local nametable_ok = dump_ppu_range(stem .. "_nametable_2000_23bf.bin", 0x2000, 0x03C0)
    local all_nametables_ok = dump_ppu_range(stem .. "_nametables_2000_2fff.bin", 0x2000, 0x1000)
    local palette_ok = dump_ppu_range(stem .. "_palette_3f00_3f1f.bin", 0x3F00, 0x20)
    capture_ppu_rows()
    capture_mapper_snapshot()
    append(summary_path, table.concat({
        frame,
        "capture",
        "screen=" .. tostring(screenshot_ok and screenshot ~= nil),
        "nametable0=" .. nametable_fingerprint(0x2000, 0x03C0),
        "nametables=" .. nametable_fingerprint(0x2000, 0x1000),
        "ppu_read=" .. tostring(nametable_ok and all_nametables_ok and palette_ok),
        "ppu_writes=" .. tostring(ppu_write_count),
        "sram_dump=" .. tostring(DUMP_SRAM),
    }, "\t"))
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tdetail_a\tdetail_b\tdetail_c\tdetail_d\tdetail_e")
append(route_path, "start\tend\tbutton\tpurpose")
append(mapper_writes_path, "frame\tkind\tvalue\tselected_register\tpc")
append(mapper_snapshot_path, "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tmapper_select_callbacks\tmapper_data_callbacks\tppu_control_callbacks\tppu_status_callbacks\tppu_addr_callbacks\tppu_data_callbacks\tmenu_source_callbacks")
append(ppu_writes_path, "frame\tppu_address\tvalue\tpc")
append(ppu_rows_path, "nametable\trow\tvalues")
append(source_reads_path, "frame\tcpu_address\tvalue\tpc\ta\tx\ty")
append(extra_source_reads_path, "frame\tcpu_address\tvalue\tpc\ta\tx\ty\tmapper_control\tr6\tr7")
append(queue_writes_path, "frame\tcpu_address\tvalue\tpc\ta\tx\ty\tmapper_control\tr6\tr7")
append(mapper_config_writes_path, "frame\taddress\tvalue\tpc\ta\tx\ty\tcurrent_r0\tcurrent_r1")
append(mapper_loader_exec_path, "frame\tpc\tstack\treturn_address\tcaller_return_address\tsaved_r0\tsaved_r1\tzp28\tscreen_state\tr0_source\tr1_source\ta\tx\ty")

append(route_path, "40\t49\tstart\ttitle")
append(route_path, "130\t139\tA\ttitle")
append(route_path, "220\t229\tstart\topening setup")
append(route_path, "300\t309\tdown\topening setup")
append(route_path, "360\t369\tA\topening setup")
append(route_path, "480\t489\tdown\topening setup")
append(route_path, "540\t549\tA\topening setup")
append(route_path, "700\t711\tB\topening setup")
append(route_path, "880\t891\tA\topening setup")
append(route_path, "940\t951\tA\topening setup")
append(route_path, "1040\t1051\tstart\tmenu state setup")
append(route_path, "1082\t1093\tdown\tmenu state setup")
append(route_path, "1124\t1135\tA\tmenu state setup")
append(route_path, "1166\t1177\tdown\tmenu state setup")
append(route_path, "1208\t1219\tA\tmenu state setup")
append(route_path, "1250\t1261\tB\tmenu state setup")
append(route_path, "1340\t1351\tselect\tmenu state setup")
append(route_path, "1382\t1393\tdown\tmenu state setup")
append(route_path, "1424\t1435\tA\tmenu state setup")
append(route_path, "1466\t1477\tright\tmenu state setup")
append(route_path, "1508\t1519\tA\tmenu state setup")
append(route_path, "1550\t1561\tB\tmenu state setup")
append(route_path, "1640\t1651\tstart\tmenu open")
append(route_path, "1682\t1693\tright\tmenu select")
append(route_path, "1724\t1735\tA\tmenu confirm")
append(route_path, "1766\t1777\tdown\tmenu select")
append(route_path, "1808\t1819\tA\tmenu confirm")
append(route_path, "1850\t1861\tB\tmenu return")
if EXTRA_BUTTON ~= "" then
    append(route_path, table.concat({
        EXTRA_START,
        EXTRA_START + EXTRA_DURATION - 1,
        EXTRA_BUTTON,
        "post-template cursor probe",
    }, "\t"))
end

registered.mapper_select = register_write(0x8000, 1, on_mapper_select)
registered.mapper_data = register_write(0x8001, 1, on_mapper_data)
registered.ppu_control = register_write(0x2000, 1, on_ppu_control)
registered.ppu_status = register_read(0x2002, on_ppu_status_read)
registered.ppu_addr = register_write(0x2006, 1, on_ppuaddr_write)
registered.ppu_data = register_write(0x2007, 1, on_ppudata_write)
registered.menu_source = true
for address = MENU_SOURCE_CPU_START, MENU_SOURCE_CPU_END - 1 do
    registered.menu_source = register_read(address, on_menu_source_read) and registered.menu_source
end
registered.extra_source = true
for _, range in ipairs(EXTRA_SOURCE_RANGES) do
    for address = range.start_address, range.end_address do
        registered.extra_source = register_read(address, on_extra_source_read) and registered.extra_source
    end
end
registered.queue_write = true
for _, range in ipairs(QUEUE_WRITE_RANGES) do
    for address = range.start_address, range.end_address do
        registered.queue_write = register_write(address, 1, on_queue_write) and registered.queue_write
    end
end
registered.mapper_config = register_write(0x0502, 1, on_mapper_config_write)
registered.mapper_config = register_write(0x0503, 1, on_mapper_config_write) and registered.mapper_config
registered.mapper_loader = register_exec(0xFEDD, on_mapper_loader_exec)

append(summary_path, table.concat({
    0,
    "lua_start",
    "capture_frame=" .. tostring(CAPTURE_FRAME),
    "max_frames=" .. tostring(MAX_FRAMES),
    "ppu_trace_start=" .. tostring(PPU_TRACE_START),
    "extra_button=" .. EXTRA_BUTTON,
    "extra_source_ranges=" .. EXTRA_SOURCE_RANGES_RAW,
    "extra_source_trace_start=" .. tostring(EXTRA_SOURCE_TRACE_START),
    "queue_write_ranges=" .. QUEUE_WRITE_RANGES_RAW,
    "queue_write_trace_start=" .. tostring(QUEUE_WRITE_TRACE_START),
    "callbacks=" .. tostring(registered.mapper_select and registered.mapper_data and registered.ppu_control and registered.ppu_addr and registered.ppu_data and registered.menu_source and registered.extra_source and registered.queue_write and registered.mapper_config and registered.mapper_loader),
}, "\t"))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while trace_frame() < MAX_FRAMES and not captured do
    local frame = trace_frame()
    joypad.set(1, route_input(frame))
    emu.frameadvance()
    if trace_frame() >= CAPTURE_FRAME then
        capture()
        captured = true
    end
end

local final_reason = captured and "lua_done" or "target_not_seen"
append(summary_path, table.concat({
    emu.framecount(),
    final_reason,
    "captured=" .. tostring(captured),
    "capture_frame=" .. tostring(CAPTURE_FRAME),
    "ppu_write_limit_reached=" .. tostring(ppu_write_limit_reached),
    "mapper_callbacks=" .. tostring(callback_counts.mapper_data),
    "menu_source_callbacks=" .. tostring(callback_counts.menu_source),
    "extra_source_callbacks=" .. tostring(callback_counts.extra_source),
    "extra_source_reads=" .. tostring(extra_source_read_count),
    "extra_source_limit_reached=" .. tostring(extra_source_read_limit_reached),
    "queue_write_callbacks=" .. tostring(callback_counts.queue_write),
    "queue_writes=" .. tostring(queue_write_count),
    "queue_write_limit_reached=" .. tostring(queue_write_limit_reached),
    "mapper_config_callbacks=" .. tostring(callback_counts.mapper_config),
    "mapper_loader_callbacks=" .. tostring(callback_counts.mapper_loader),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
