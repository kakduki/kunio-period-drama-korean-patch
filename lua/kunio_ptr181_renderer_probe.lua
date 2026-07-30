-- Bounded renderer probe for the English-reference PTR-181 dialogue record.
-- The route is finite and stops after the observed frame-392 field dialogue.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/ptr181_renderer_probe"
local TARGET_POINTER = tonumber(os.getenv("KUNIO_TARGET_POINTER") or "B188", 16)
local CAPTURE_FRAME = 392
local MAX_FRAMES = 450
local TRACE_LIMIT = 5000

local summary_path = OUT_DIR .. "/summary.tsv"
local pointer_path = OUT_DIR .. "/pointer_samples.tsv"
local source_path = OUT_DIR .. "/source_reads.tsv"
local parser_path = OUT_DIR .. "/parser_exec.tsv"
local ppu_path = OUT_DIR .. "/ppu_writes.tsv"
local nametable_path = OUT_DIR .. "/nametable_rows.tsv"
local mapper_path = OUT_DIR .. "/mapper_state.tsv"
local mapper_wrapper_path = OUT_DIR .. "/mapper_wrapper_exec.tsv"
local trace_count = 0
local target_seen = false
local captured = false
local last_pointer = nil
local ppu_addr_high = nil
local ppu_addr = 0
local ppu_control = nil
local mapper_control = nil
local mapper_select = nil
local mapper_registers = {}

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

local function optional_hex2(value)
    if value == nil then return "" end
    return hex2(value)
end

local function read_byte(addr)
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return 0
end

local function read_register(name)
    local ok, value = pcall(function() return memory.getregister(name) end)
    if ok and value ~= nil then return value end
    return 0
end

local function text_pointer()
    return read_byte(0x1A) + read_byte(0x1B) * 0x100
end

local function stream_pointer()
    return read_byte(0x05) + read_byte(0x06) * 0x100
end

local function target_source_byte()
    local pointer = text_pointer()
    local y = read_register("y")
    return read_byte((pointer + y) % 0x10000)
end

local function trace_row(label, address, value)
    if trace_count >= TRACE_LIMIT then return end
    trace_count = trace_count + 1
    append(parser_path, table.concat({
        emu.framecount(), label, hex4(address), hex2(value),
        hex4(read_register("pc")), hex2(read_register("a")),
        hex2(read_register("x")), hex2(read_register("y")),
        hex4(text_pointer()), hex4(stream_pointer()),
        hex2(target_source_byte()),
    }, "\t"))
end

local function register_exec(addr, callback)
    local ok = pcall(function() memory.registerexec(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerexecute(addr, callback) end)
end

local function register_read(addr, callback)
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(addr, 1, callback) end)
end

local function register_write(addr, size, callback)
    local ok = pcall(function() memory.registerwrite(addr, size, callback) end)
    if ok then return true end
    if size == 1 then
        return pcall(function() memory.registerwrite(addr, callback) end)
    end
    return false
end

local function on_source_read(addr, size, value)
    if text_pointer() ~= TARGET_POINTER or trace_count >= TRACE_LIMIT then return end
    target_seen = true
    trace_count = trace_count + 1
    append(source_path, table.concat({
        emu.framecount(), hex4(addr), hex2(value or read_byte(addr)),
        hex4(read_register("pc")), hex2(read_register("a")),
        hex2(read_register("x")), hex2(read_register("y")),
        hex4(stream_pointer()), hex2(target_source_byte()),
    }, "\t"))
end

local function on_parser(label)
    return function()
        if text_pointer() == TARGET_POINTER then
            target_seen = true
            trace_row(label, read_register("pc"), read_register("a"))
        end
    end
end

local function on_mapper_select(addr, size, value)
    mapper_control = value or 0
    mapper_select = mapper_control % 8
end

local function on_mapper_data(addr, size, value)
    if mapper_select ~= nil then mapper_registers[mapper_select] = value or 0 end
end

local function on_mapper_wrapper()
    append(mapper_wrapper_path, table.concat({
        emu.framecount(), hex4(text_pointer()), hex4(stream_pointer()),
        hex2(read_byte(0x00)), hex2(read_byte(0x10)), hex2(read_byte(0x20)),
        hex2(read_byte(0x51)), hex2(read_byte(0x69)), hex2(read_byte(0x6A)),
        hex2(read_byte(0x708)), hex2(read_byte(0x710)), hex2(read_byte(0x71E)),
        hex2(read_byte(0x720)), hex2(read_byte(0x721)), hex2(read_byte(0x722)),
        hex2(read_byte(0x723)), hex2(read_byte(0x735)), hex2(read_byte(0x7A8)),
        hex2(read_byte(0x7A9)),
    }, "\t"))
end

local function on_ppu_control(addr, size, value)
    ppu_control = value or 0
end

local function is_target_row(addr)
    return (addr >= 0x2320 and addr < 0x2340) or (addr >= 0x2360 and addr < 0x2380)
end

local function on_ppuaddr_write(addr, size, value)
    local byte = value or 0
    if ppu_addr_high == nil then
        ppu_addr_high = byte % 0x40
    else
        ppu_addr = ppu_addr_high * 0x100 + byte
        ppu_addr_high = nil
    end
end

local function on_ppudata_write(addr, size, value)
    if is_target_row(ppu_addr) then
        append(ppu_path, table.concat({
            emu.framecount(), hex4(ppu_addr), hex2(value),
            hex4(read_register("pc")), hex4(text_pointer()),
            hex2(read_register("y")), optional_hex2(mapper_control),
            mapper_select == nil and "" or tostring(mapper_select),
            optional_hex2(ppu_control),
        }, "\t"))
    end
    ppu_addr = (ppu_addr + 1) % 0x4000
end

local function ppu_byte(addr)
    local ok, value = pcall(function() return ppu.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return 0
end

local function dump_nametable()
    local f = assert(io.open(nametable_path, "a"))
    for row = 0, 29 do
        local values = {}
        for column = 0, 31 do
            values[#values + 1] = hex2(ppu_byte(0x2000 + row * 32 + column))
        end
        f:write(table.concat({emu.framecount(), row, table.concat(values, " ")}, "\t") .. "\n")
    end
    f:close()
end

local function dump_cpu(path, start_addr, length)
    local f = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        f:write(string.char(read_byte(start_addr + offset)))
    end
    f:close()
end

local function write_mapper_state()
    local values = {emu.framecount(), optional_hex2(mapper_control), mapper_select == nil and "" or tostring(mapper_select), optional_hex2(ppu_control)}
    for index = 0, 7 do values[#values + 1] = optional_hex2(mapper_registers[index]) end
    append(mapper_path, table.concat(values, "\t"))
end

local function capture()
    local frame = emu.framecount()
    local stem = OUT_DIR .. "/frame_" .. string.format("%06d", frame)
    local ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if ok and screenshot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb"))
        f:write(screenshot)
        f:close()
    end
    dump_cpu(stem .. "_cpu_ram.bin", 0x0000, 0x0800)
    dump_nametable()
    write_mapper_state()
    append(summary_path, table.concat({frame, "capture", tostring(ok), tostring(target_seen), tostring(trace_count)}, "\t"))
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
    return {}
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tscreenshot\ttarget_seen\ttrace_count")
append(pointer_path, "frame\ttext_pointer\tstream_pointer\tsource_byte")
append(source_path, "frame\taddress\tvalue\tpc\ta\tx\ty\tstream_pointer\tsource_byte")
append(parser_path, "frame\tlabel\taddress\tvalue\tpc\ta\tx\ty\ttext_pointer\tstream_pointer\tsource_byte")
append(ppu_path, "frame\tppu_address\tvalue\tpc\ttext_pointer\ty\tmapper_control\tmapper_select\tppu_control")
append(nametable_path, "frame\trow\tvalues")
append(mapper_path, "frame\tmapper_control\tmapper_select\tppu_control\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7")
append(mapper_wrapper_path, "frame\ttext_pointer\tstream_pointer\tram00\tram10\tram20\tram51\tram69\tram6A\tram708\tram710\tram71E\tram720\tram721\tram722\tram723\tram735\tram7A8\tram7A9")

local parser_registered = register_exec(0x915A, on_parser("parser"))
local prep_registered = register_exec(0x955F, on_parser("emit_prep"))
local dispatch_registered = register_exec(0x9593, on_parser("emit_dispatch"))
local source_registered = true
for address = TARGET_POINTER, TARGET_POINTER + 0x30 do
    source_registered = register_read(address, on_source_read) and source_registered
end
local ppuaddr_registered = register_write(0x2006, 1, on_ppuaddr_write)
local ppudata_registered = register_write(0x2007, 1, on_ppudata_write)
local mapper_select_registered = register_write(0x8000, 1, on_mapper_select)
local mapper_data_registered = register_write(0x8001, 1, on_mapper_data)
local ppu_control_registered = register_write(0x2000, 1, on_ppu_control)
local mapper_wrapper_registered = register_exec(0xEE3F, on_mapper_wrapper)

append(summary_path, table.concat({0, "lua_start", tostring(parser_registered and prep_registered and dispatch_registered), tostring(source_registered), tostring(ppuaddr_registered and ppudata_registered and mapper_select_registered and mapper_data_registered and ppu_control_registered and mapper_wrapper_registered), hex4(TARGET_POINTER)}, "\t"))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and not captured do
    local frame = emu.framecount()
    local pointer = text_pointer()
    if pointer == TARGET_POINTER then target_seen = true end
    if pointer ~= last_pointer or pointer == TARGET_POINTER then
        append(pointer_path, table.concat({frame, hex4(pointer), hex4(stream_pointer()), hex2(target_source_byte())}, "\t"))
        last_pointer = pointer
    end
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "PTR181 renderer probe " .. tostring(frame))
    gui.text(2, 17, "target=" .. tostring(target_seen) .. " trace=" .. tostring(trace_count))
    emu.frameadvance()
    if emu.framecount() >= CAPTURE_FRAME then
        capture()
        captured = true
    end
end

append(summary_path, table.concat({emu.framecount(), "lua_done", tostring(captured), tostring(target_seen), tostring(trace_count)}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
