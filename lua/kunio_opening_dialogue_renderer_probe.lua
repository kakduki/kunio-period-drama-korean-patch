-- Bounded renderer trace for the known opening-dialogue route.
--
-- This is not an autoplay script. It follows the one proven title/menu route,
-- records only a bounded time window, captures at frame 883, and stops. The
-- trace maps the existing vertical tile pair used by dialogue so the Korean
-- 8x16 proof can be validated without changing the dialogue layout.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/opening_dialogue_renderer_probe"
local CAPTURE_FRAME = tonumber(os.getenv("KUNIO_CAPTURE_FRAME") or "883")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "920")
local TRACE_START = tonumber(os.getenv("KUNIO_TRACE_START") or "600")
local TARGET_POINTER = 0xB1A6
local PARSER_CPU = 0x915A
local EMIT_PREP_CPU = 0x955F
local EMIT_DISPATCH_CPU = 0x9593
local TRACE_LIMIT = 4000

local summary_path = OUT_DIR .. "/summary.tsv"
local parser_path = OUT_DIR .. "/parser_exec.tsv"
local source_reads_path = OUT_DIR .. "/source_reads.tsv"
local buffer_path = OUT_DIR .. "/buffer_writes.tsv"
local queue_path = OUT_DIR .. "/queue_writes.tsv"
local dma_path = OUT_DIR .. "/dma.tsv"
local oam_path = OUT_DIR .. "/oam_writes.tsv"
local ppu_writes_path = OUT_DIR .. "/ppu_writes.tsv"
local ppu_path = OUT_DIR .. "/ppu_rows.tsv"
local trace_count = 0
local captured = false
local last_dma_page = nil
local ppu_addr_high = nil
local ppu_addr = 0

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

local function stream_pointer()
    return read_byte(0x05) + read_byte(0x06) * 0x100
end

local function text_pointer()
    return read_byte(0x1A) + read_byte(0x1B) * 0x100
end

local function target_source_byte()
    local pointer = text_pointer()
    local y = read_register("y")
    return read_byte((pointer + y) % 0x10000)
end

local function trace_exec(label)
    return function()
        if trace_count >= TRACE_LIMIT or text_pointer() ~= TARGET_POINTER then return end
        trace_count = trace_count + 1
        append(parser_path, table.concat({
            emu.framecount(),
            label,
            hex4(read_register("pc")),
            hex2(read_register("a")),
            hex2(read_register("x")),
            hex2(read_register("y")),
            hex4(text_pointer()),
            hex4(stream_pointer()),
            hex4(read_byte(0x07) + read_byte(0x08) * 0x100),
            hex2(target_source_byte()),
            hex2(read_byte(0x7000)),
            hex2(read_byte(0x7001)),
            hex2(read_byte(0x7002)),
            hex2(read_byte(0x7003)),
            hex2(read_byte(0x7004)),
            hex2(read_byte(0x7005)),
            hex2(read_byte(0x7006)),
        }, "\t"))
    end
end

local function register_exec(addr, callback)
    local ok = pcall(function() memory.registerexec(addr, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerexecute(addr, callback) end)
    return ok
end

local function register_write(addr, size, callback)
    local ok = pcall(function() memory.registerwrite(addr, size, callback) end)
    if ok then return true end
    if size == 1 then
        ok = pcall(function() memory.registerwrite(addr, callback) end)
    end
    return ok
end

local function register_read(addr, callback)
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerread(addr, 1, callback) end)
    return ok
end

local function on_source_read(addr, size, value)
    if trace_count >= TRACE_LIMIT then return end
    trace_count = trace_count + 1
    local pc = read_register("pc")
    local code = {}
    for offset = 0, 7 do
        code[#code + 1] = hex2(read_byte((pc + offset) % 0x10000))
    end
    append(source_reads_path, table.concat({
        emu.framecount(),
        hex4(addr or 0),
        hex2(value or read_byte(addr or 0)),
        hex4(pc),
        hex2(read_register("a")),
        hex2(read_register("x")),
        hex2(read_register("y")),
        hex4(stream_pointer()),
        hex4(read_byte(0x07) + read_byte(0x08) * 0x100),
        table.concat(code, " "),
    }, "\t"))
end

local function on_buffer_write(addr, size, value)
    local frame = emu.framecount()
    if trace_count >= TRACE_LIMIT or frame < TRACE_START then return end
    trace_count = trace_count + 1
    append(buffer_path, table.concat({
        frame,
        hex4(addr or 0),
        hex2(value or 0),
        hex4(read_register("pc")),
        hex4(stream_pointer()),
        hex2(read_register("y")),
        hex2(target_source_byte()),
    }, "\t"))
end

local function on_queue_write(addr, size, value)
    local frame = emu.framecount()
    if trace_count >= TRACE_LIMIT or frame < TRACE_START then return end
    trace_count = trace_count + 1
    append(queue_path, table.concat({
        frame,
        hex4(addr or 0),
        hex2(value or 0),
        hex4(read_register("pc")),
        hex4(text_pointer()),
        hex2(read_register("y")),
    }, "\t"))
end

local function on_oam_write(addr, size, value)
    local frame = emu.framecount()
    if trace_count >= TRACE_LIMIT or frame < TRACE_START then return end
    local value_byte = value or 0
    if value_byte < 0x81 or value_byte > 0x9A then return end
    trace_count = trace_count + 1
    append(oam_path, table.concat({
        frame,
        hex4(addr or 0),
        hex2(value_byte),
        hex4(read_register("pc")),
        hex4(stream_pointer()),
        hex2(read_register("y")),
    }, "\t"))
end

local function on_dma_write(addr, size, value)
    last_dma_page = value or 0
    append(dma_path, table.concat({
        emu.framecount(),
        hex2(last_dma_page),
        hex4(read_register("pc")),
        hex4(stream_pointer()),
    }, "\t"))
end

local function on_oamdata_write(addr, size, value)
    local frame = emu.framecount()
    if trace_count >= TRACE_LIMIT or frame < TRACE_START then return end
    local value_byte = value or 0
    if value_byte < 0x81 or value_byte > 0x9A then return end
    trace_count = trace_count + 1
    append(oam_path, table.concat({
        frame,
        "2004",
        hex2(value_byte),
        hex4(read_register("pc")),
        hex4(stream_pointer()),
        hex2(read_register("y")),
    }, "\t"))
end

local function is_dialogue_nametable_addr(addr)
    return (addr >= 0x2320 and addr < 0x2340) or (addr >= 0x2360 and addr < 0x2380)
end

local function on_ppuaddr_write(addr, size, value)
    local byte = value or 0
    if ppu_addr_high == nil then
        ppu_addr_high = byte % 0x40
    else
        ppu_addr = ppu_addr_high * 0x100 + byte
        ppu_addr_high = nil
        if is_dialogue_nametable_addr(ppu_addr) then
            append(ppu_writes_path, table.concat({
                emu.framecount(),
                "address",
                hex4(ppu_addr),
                "--",
                hex4(read_register("pc")),
                hex4(stream_pointer()),
                hex2(read_register("y")),
            }, "\t"))
        end
    end
end

local function on_ppudata_write(addr, size, value)
    if is_dialogue_nametable_addr(ppu_addr) then
        append(ppu_writes_path, table.concat({
            emu.framecount(),
            "data",
            hex4(ppu_addr),
            hex2(value or 0),
            hex4(read_register("pc")),
            hex4(stream_pointer()),
            hex2(read_register("y")),
        }, "\t"))
    end
    ppu_addr = (ppu_addr + 1) % 0x4000
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

local function ppu_byte(addr)
    local ok, value = pcall(function() return ppu.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return 0
end

local function capture_ppu_rows()
    for row = 0, 29 do
        local values = {}
        for column = 0, 31 do
            values[#values + 1] = hex2(ppu_byte(0x2000 + row * 32 + column))
        end
        append(ppu_path, table.concat({row, table.concat(values, " ")}, "\t"))
    end
end

local function dump_range(path, start_addr, length)
    local f = assert(io.open(path, "wb"))
    for offset = 0, length - 1 do
        f:write(string.char(read_byte(start_addr + offset)))
    end
    f:close()
end

local function capture()
    local frame = emu.framecount()
    local stem = OUT_DIR .. "/renderer_probe_frame_" .. string.format("%06d", frame)
    local screenshot_ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if screenshot_ok and screenshot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb"))
        f:write(screenshot)
        f:close()
    end
    dump_range(stem .. "_cpu_ram.bin", 0x0000, 0x0800)
    if last_dma_page ~= nil then
        dump_range(stem .. "_last_dma_page_" .. hex2(last_dma_page) .. ".bin", last_dma_page * 0x100, 0x100)
    end
    capture_ppu_rows()
    append(summary_path, table.concat({
        frame,
        "capture",
        tostring(screenshot_ok),
        hex2(last_dma_page or 0),
        tostring(trace_count),
    }, "\t"))
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tscreenshot\tlast_dma_page\ttrace_count")
append(parser_path, "frame\tlabel\tpc\ta\tx\ty\ttext_1a\tstream_05\tstream_07\tsource_byte\tbuf7000\tbuf7001\tbuf7002\tbuf7003\tbuf7004\tbuf7005\tbuf7006")
append(source_reads_path, "frame\taddress\tvalue\tpc\ta\tx\ty\tstream_05\tstream_07\tcode_bytes")
append(buffer_path, "frame\taddress\tvalue\tpc\tstream_05\ty\tsource_byte")
append(queue_path, "frame\taddress\tvalue\tpc\ttext_1a\ty")
append(dma_path, "frame\tpage\tpc\tstream_05")
append(oam_path, "frame\taddress\tvalue\tpc\tstream_05\ty")
append(ppu_writes_path, "frame\ttype\tppu_address\tvalue\tpc\tstream_05\ty")
append(ppu_path, "row\tvalues")

local parser_registered = register_exec(PARSER_CPU, trace_exec("parser"))
local prep_registered = register_exec(EMIT_PREP_CPU, trace_exec("emit_prep"))
local dispatch_registered = register_exec(EMIT_DISPATCH_CPU, trace_exec("emit_dispatch"))
local buffer_registered = register_write(0x7000, 7, on_buffer_write)
local queue_registered = register_write(0x711D, 0x300, on_queue_write)
local oam_registered = register_write(0x0200, 0x100, on_oam_write)
local dma_registered = register_write(0x4014, 1, on_dma_write)
local oamdata_registered = register_write(0x2004, 1, on_oamdata_write)
local ppuaddr_registered = register_write(0x2006, 1, on_ppuaddr_write)
local ppudata_registered = register_write(0x2007, 1, on_ppudata_write)
local source_read_registered = true
for addr = TARGET_POINTER, TARGET_POINTER + 0x24 do
    source_read_registered = register_read(addr, on_source_read) and source_read_registered
end
append(summary_path, table.concat({
    0,
    "lua_start",
    tostring(parser_registered and prep_registered and dispatch_registered),
    tostring(buffer_registered) .. ";" .. tostring(queue_registered) .. ";" .. tostring(oam_registered) .. ";" .. tostring(dma_registered) .. ";" .. tostring(oamdata_registered) .. ";" .. tostring(ppuaddr_registered) .. ";" .. tostring(ppudata_registered) .. ";" .. tostring(source_read_registered),
    "target=" .. hex4(TARGET_POINTER),
}, "\t"))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and not captured do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "Opening renderer probe " .. tostring(frame))
    gui.text(2, 17, "trace=" .. tostring(trace_count))
    emu.frameadvance()
    if emu.framecount() >= CAPTURE_FRAME then
        capture()
        captured = true
    end
end

append(summary_path, table.concat({
    emu.framecount(),
    "lua_done",
    tostring(captured),
    hex2(last_dma_page or 0),
    tostring(trace_count),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
