-- Bounded stage progression probe.
--
-- The old explorer chained unrelated menu routes after entering the field,
-- which made long runs look like an opening-screen loop. This probe keeps the
-- known-good entry sequence, then spends the remaining budget on one combat
-- route while saving every meaningful nametable change and RAM checkpoint.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."
local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/stage_progression_probe")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "7200")
local SNAPSHOT_GAP = tonumber(os.getenv("KUNIO_STAGE_SNAPSHOT_GAP") or "90")
local UNIQUE_LIMIT = tonumber(os.getenv("KUNIO_STAGE_UNIQUE_LIMIT") or "72")
local EXTRA_DIALOGUE_START = os.getenv("KUNIO_EXTRA_DIALOGUE_START") ~= "0"
local COMBAT_NO_B = os.getenv("KUNIO_COMBAT_NO_B") == "1"
local COMBAT_SWEEP = os.getenv("KUNIO_COMBAT_SWEEP") == "1"
local COMBAT_MIXED = os.getenv("KUNIO_COMBAT_MIXED") == "1"
local COMBAT_STATIONARY = os.getenv("KUNIO_COMBAT_STATIONARY") == "1"
local COMBAT_GRID = os.getenv("KUNIO_COMBAT_GRID") == "1"
local ADVANCE_AFTER_COMBAT = os.getenv("KUNIO_ADVANCE_AFTER_COMBAT") == "1"
local MAP_SOURCE_ROUTE = os.getenv("KUNIO_MAP_SOURCE_ROUTE") == "1"
local MAP_DIRECTION = os.getenv("KUNIO_MAP_DIRECTION") or "right"
local MAP_SWEEP = os.getenv("KUNIO_MAP_SWEEP") == "1"
local STATE_WRITES_TEXT = os.getenv("KUNIO_STATE_WRITES") or ""
local STATE_WRITE_START = tonumber(os.getenv("KUNIO_STATE_WRITE_START") or "900")
local STATE_WRITE_END = tonumber(os.getenv("KUNIO_STATE_WRITE_END") or "1300")
local RAM_TRACE = os.getenv("KUNIO_RAM_TRACE") == "1"
local RAM_TRACE_LIMIT = tonumber(os.getenv("KUNIO_RAM_TRACE_LIMIT") or "20000")
local RAM_TRACE_PC = os.getenv("KUNIO_RAM_TRACE_PC") == "1"
local RAM_TRACE_OBJECT_PC = os.getenv("KUNIO_RAM_TRACE_OBJECT_PC") == "1"
local RAM_STATE_TRACE_LIMIT = tonumber(os.getenv("KUNIO_RAM_STATE_TRACE_LIMIT") or "20000")
local RAM_TRACE_OBJECTS = os.getenv("KUNIO_RAM_TRACE_OBJECTS") == "1"
local DIALOGUE_TRACE = os.getenv("KUNIO_DIALOGUE_TRACE") == "1"
local DIALOGUE_TRACE_LIMIT = tonumber(os.getenv("KUNIO_DIALOGUE_TRACE_LIMIT") or "12000")
local PPU_TRACE = os.getenv("KUNIO_PPU_TRACE") == "1"
local PPU_TRACE_LIMIT = tonumber(os.getenv("KUNIO_PPU_TRACE_LIMIT") or "24000")
local PPU_TRACE_START = tonumber(os.getenv("KUNIO_PPU_TRACE_START") or "0")
local NAME_SOURCE_TRACE = os.getenv("KUNIO_NAME_SOURCE_TRACE") == "1"
local NAME_SOURCE_TRACE_LIMIT = tonumber(os.getenv("KUNIO_NAME_SOURCE_TRACE_LIMIT") or "24000")
local STATE_MACHINE_TRACE = os.getenv("KUNIO_STATE_MACHINE_TRACE") == "1"
local SRAM_ROUTE_TRACE = os.getenv("KUNIO_SRAM_ROUTE_TRACE") == "1"
local SRAM_ROUTE_TRACE_LIMIT = tonumber(os.getenv("KUNIO_SRAM_ROUTE_TRACE_LIMIT") or "4000")
local COUNTER_READ_TRACE = os.getenv("KUNIO_COUNTER_READ_TRACE") == "1"
local COUNTER_READ_TRACE_LIMIT = tonumber(os.getenv("KUNIO_COUNTER_READ_TRACE_LIMIT") or "4000")
local STATE_READ_TRACE = os.getenv("KUNIO_STATE_READ_TRACE") == "1"
local STATE_READ_TRACE_LIMIT = tonumber(os.getenv("KUNIO_STATE_READ_TRACE_LIMIT") or "12000")
local COMBAT_BRANCH_TRACE = os.getenv("KUNIO_COMBAT_BRANCH_TRACE") == "1"
local COMBAT_BRANCH_TRACE_LIMIT = tonumber(os.getenv("KUNIO_COMBAT_BRANCH_TRACE_LIMIT") or "12000")
local COMBAT_OBJECT_TRACE = os.getenv("KUNIO_COMBAT_OBJECT_TRACE") == "1"
local COMBAT_OBJECT_TRACE_LIMIT = tonumber(os.getenv("KUNIO_COMBAT_OBJECT_TRACE_LIMIT") or "12000")

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line)
    local f = assert(io.open(path, "a")); f:write(line .. "\n"); f:close()
end

local function parse_writes(text)
    local writes = {}
    for part in string.gmatch(text, "([^,]+)") do
        local addr_text, value_text = string.match(part, "^%s*([^=]+)%s*=%s*([^=]+)%s*$")
        local addr, value = tonumber(addr_text), tonumber(value_text)
        if addr ~= nil and value ~= nil then
            writes[#writes + 1] = { addr = addr, value = value }
        end
    end
    return writes
end
local STATE_WRITES = parse_writes(STATE_WRITES_TEXT)
local function write_state_bytes()
    for _, item in ipairs(STATE_WRITES) do
        pcall(function() memory.writebyte(item.addr, item.value) end)
    end
end
local function state_writes_label()
    local parts = {}
    for _, item in ipairs(STATE_WRITES) do
        parts[#parts + 1] = string.format("0x%04X=0x%02X", item.addr, item.value)
    end
    return table.concat(parts, ",")
end
local function hex2(value) return string.format("%02X", (value or 0) % 0x100) end
local function byte_at(addr, domain)
    local ok, value
    if domain ~= nil then
        ok, value = pcall(function() return memory.readbyte(addr, domain) end)
        if ok and value ~= nil then return value end
    end
    ok, value = pcall(function() return memory.readbyte(addr) end)
    return ok and value or 0
end
local function ppu_byte(addr)
    local ok, value = pcall(function() return ppu.readbyte(addr) end)
    return ok and value or 0
end
local function fingerprint()
    local hash, sum = 0, 0
    for addr = 0x2000, 0x23BF, 4 do
        local value = ppu_byte(addr)
        hash = (hash * 131 + value + addr) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end
local function dump_ram(prefix)
    local f = assert(io.open(prefix .. "_cpu_ram.bin", "wb"))
    for addr = 0, 0x7FF do f:write(string.char(byte_at(addr))) end
    f:close()
end
local function dump_ppu(prefix)
    local f = assert(io.open(prefix .. "_nametable.bin", "wb"))
    for addr = 0x2000, 0x23FF do f:write(string.char(ppu_byte(addr))) end
    f:close()
end
local mapper_select = nil
local mapper_registers = {}
local ppu_control = nil
local function register_write(addr, size, callback)
    local ok = pcall(function() memory.registerwrite(addr, size, callback) end)
    if ok then return true end
    if size == 1 then return pcall(function() memory.registerwrite(addr, callback) end) end
    return false
end
local ram_trace_count = 0
local ram_trace_path = OUT_DIR .. "/ram_writes.tsv"
local ram_state_trace_count = 0
local ram_state_trace_path = OUT_DIR .. "/ram_state_writes.tsv"
local dialogue_trace_count = 0
local dialogue_pointer_path = OUT_DIR .. "/dialogue_pointers.tsv"
local dialogue_source_path = OUT_DIR .. "/dialogue_source_reads.tsv"
local dialogue_parser_path = OUT_DIR .. "/dialogue_parser_exec.tsv"
local dialogue_ppu_path = OUT_DIR .. "/dialogue_ppu_writes.tsv"
local dialogue_last_pointer = nil
local dialogue_ppu_addr_high = nil
local dialogue_ppu_addr = 0
local ppu_trace_count = 0
local ppu_trace_path = OUT_DIR .. "/ppu_writes.tsv"
local ppu_trace_addr_high = nil
local ppu_trace_addr = 0
local name_source_trace_count = 0
local name_source_trace_path = OUT_DIR .. "/name_source_reads.tsv"
local state_machine_trace_path = OUT_DIR .. "/state_machine_exec.tsv"
local sram_route_trace_count = 0
local sram_route_trace_path = OUT_DIR .. "/sram_route_exec.tsv"
local counter_read_trace_count = 0
local counter_read_trace_path = OUT_DIR .. "/counter_reads.tsv"
local function read_register(name)
    local ok, value = pcall(function() return memory.getregister(name) end)
    return ok and value or 0
end
local function trace_state_machine(label)
    append(state_machine_trace_path, table.concat({
        tostring(emu.framecount()), label, string.format("%04X", read_register("pc")),
        string.format("%02X", read_register("a")), string.format("%02X", read_register("x")), string.format("%02X", read_register("y")),
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)),
        hex2(byte_at(0x002C)), hex2(byte_at(0x002D)), hex2(byte_at(0x0028)), hex2(byte_at(0x0029)),
        hex2(byte_at(0x002A)), hex2(byte_at(0x002B)), hex2(byte_at(0x001A)), hex2(byte_at(0x001B))
    }, "\t"))
end
local function trace_sram_route(label)
    if not SRAM_ROUTE_TRACE or sram_route_trace_count >= SRAM_ROUTE_TRACE_LIMIT then return end
    sram_route_trace_count = sram_route_trace_count + 1
    append(sram_route_trace_path, table.concat({
        tostring(emu.framecount()), label, string.format("%04X", read_register("pc")),
        hex2(read_register("a")), hex2(read_register("x")), hex2(read_register("y")),
        hex2(byte_at(0x7A00)), hex2(byte_at(0x7A01)), hex2(byte_at(0x7A02)),
        hex2(byte_at(0x7A03)), hex2(byte_at(0x7A04)), hex2(byte_at(0x7A05)),
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)),
        hex2(byte_at(0x04FC)), hex2(byte_at(0x0050)), hex2(byte_at(0x0051)),
        hex2(byte_at(0x0052)), hex2(byte_at(0x0053)),
    }, "\t"))
end
local state_read_trace_count = 0
local state_read_trace_path = OUT_DIR .. "/state_reads.tsv"
local combat_branch_trace_count = 0
local combat_branch_trace_path = OUT_DIR .. "/combat_branch_trace.tsv"
local combat_object_trace_count = 0
local combat_object_trace_path = OUT_DIR .. "/combat_object_trace.tsv"
local COMBAT_SLOT_TRACE = os.getenv("KUNIO_COMBAT_SLOT_TRACE") == "1"
local COMBAT_SLOT_TRACE_LIMIT = tonumber(os.getenv("KUNIO_COMBAT_SLOT_TRACE_LIMIT") or "20000")
local combat_slot_trace_count = 0
local combat_slot_trace_path = OUT_DIR .. "/combat_slot_trace.tsv"
local function trace_combat_branch(label)
    if not COMBAT_BRANCH_TRACE or combat_branch_trace_count >= COMBAT_BRANCH_TRACE_LIMIT then return end
    combat_branch_trace_count = combat_branch_trace_count + 1
    append(combat_branch_trace_path, table.concat({
        tostring(emu.framecount()), label, string.format("%04X", read_register("pc")),
        hex2(read_register("a")), hex2(read_register("x")), hex2(read_register("y")), hex2(read_register("p")),
        hex2(byte_at(0x7A00)), hex2(byte_at(0x7A01)), hex2(byte_at(0x7A02)), hex2(byte_at(0x04F1))
    }, "\t"))
end
local function trace_combat_object(label)
    if not COMBAT_OBJECT_TRACE or combat_object_trace_count >= COMBAT_OBJECT_TRACE_LIMIT then return end
    combat_object_trace_count = combat_object_trace_count + 1
    append(combat_object_trace_path, table.concat({
        tostring(emu.framecount()), label, string.format("%04X", read_register("pc")),
        hex2(read_register("a")), hex2(read_register("x")), hex2(read_register("y")),
        hex2(byte_at(0x0430)), hex2(byte_at(0x0431)), hex2(byte_at(0x0432)), hex2(byte_at(0x0433)),
        hex2(byte_at(0x0434)), hex2(byte_at(0x0435)), hex2(byte_at(0x0436)), hex2(byte_at(0x0437)),
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)),
        hex2(byte_at(0x0706)), hex2(byte_at(0x07BC)), hex2(byte_at(0x07E4)),
    }, "\t"))
end

local function trace_combat_slot(label)
    if not COMBAT_SLOT_TRACE or combat_slot_trace_count >= COMBAT_SLOT_TRACE_LIMIT then return end
    combat_slot_trace_count = combat_slot_trace_count + 1
    local x = read_register("x")
    append(combat_slot_trace_path, table.concat({
        tostring(emu.framecount()), label, string.format("%04X", read_register("pc")),
        hex2(read_register("a")), hex2(x), hex2(read_register("y")),
        hex2(byte_at(0x0049 + x)), hex2(byte_at(0x0050 + x)), hex2(byte_at(0x0057 + x)),
        hex2(byte_at(0x00BA + x)), hex2(byte_at(0x00C3 + x)),
        hex2(byte_at(0x0496 + x)), hex2(byte_at(0x04AC + x)), hex2(byte_at(0x04B4 + x)),
        hex2(byte_at(0x76AF + x)), hex2(byte_at(0x76B4 + x)),
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)),
        hex2(byte_at(0x04FC)), hex2(byte_at(0x7A00)), hex2(byte_at(0x7A01)),
        hex2(byte_at(0x7A02)), hex2(byte_at(0x7A03)),
    }, "\t"))
end

local function trace_state_read(addr, size, value)
    if not STATE_READ_TRACE or state_read_trace_count >= STATE_READ_TRACE_LIMIT then return end
    state_read_trace_count = state_read_trace_count + 1
    append(state_read_trace_path, table.concat({
        tostring(emu.framecount()), string.format("%04X", addr or 0), hex2(value or byte_at(addr or 0)),
        string.format("%04X", read_register("pc")), hex2(read_register("a")), hex2(read_register("x")),
        hex2(read_register("y")), hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)),
        hex2(byte_at(0x04FC)), hex2(byte_at(0x04F3)), hex2(byte_at(0x04F4)), hex2(byte_at(0x0706)), hex2(byte_at(0x7A01)), hex2(byte_at(0x7A02)),
    }, "\t"))
end
local function trace_counter_read(label)
    if not COUNTER_READ_TRACE or counter_read_trace_count >= COUNTER_READ_TRACE_LIMIT then return end
    counter_read_trace_count = counter_read_trace_count + 1
    append(counter_read_trace_path, table.concat({
        tostring(emu.framecount()), label, string.format("%04X", read_register("pc")),
        hex2(read_register("a")), hex2(read_register("x")), hex2(read_register("y")),
        hex2(byte_at(0x7A00)), hex2(byte_at(0x7A01)), hex2(byte_at(0x7A02)),
        hex2(byte_at(0x7A03)), hex2(byte_at(0x7A04)), hex2(byte_at(0x7A05)),
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)),
        hex2(byte_at(0x04FC)),
    }, "\t"))
end
local function text_pointer()
    return byte_at(0x1A) + byte_at(0x1B) * 0x100
end
local function stream_pointer()
    return byte_at(0x05) + byte_at(0x06) * 0x100
end
local function register_read(addr, callback)
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(addr, 1, callback) end)
end
local function register_exec(addr, callback)
    local ok = pcall(function() memory.registerexec(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerexecute(addr, callback) end)
end
local function dialogue_log(row, path)
    if dialogue_trace_count >= DIALOGUE_TRACE_LIMIT then return end
    dialogue_trace_count = dialogue_trace_count + 1
    append(path, row)
end
local function on_dialogue_source_read(addr, size, value)
    local pointer = text_pointer()
    local pc = read_register("pc")
    if pointer < 0x8000 or pc == (addr or 0) then return end
    dialogue_log(table.concat({
        emu.framecount(), string.format("%04X", addr or 0), string.format("%02X", value or byte_at(addr or 0)),
        string.format("%04X", pc), string.format("%02X", read_register("a")),
        string.format("%02X", read_register("x")), string.format("%02X", read_register("y")),
        string.format("%04X", pointer), string.format("%04X", stream_pointer()),
    }, "\t"), dialogue_source_path)
end
local function on_dialogue_parser(label)
    return function()
        local pointer = text_pointer()
        if pointer < 0x8000 then return end
        dialogue_log(table.concat({
            emu.framecount(), label, string.format("%04X", read_register("pc")),
            string.format("%02X", read_register("a")), string.format("%02X", read_register("x")),
            string.format("%02X", read_register("y")), string.format("%04X", pointer),
            string.format("%04X", stream_pointer()),
        }, "\t"), dialogue_parser_path)
    end
end
local function is_dialogue_row(addr)
    return (addr >= 0x2320 and addr < 0x2340) or (addr >= 0x2360 and addr < 0x2380)
end
local function on_dialogue_ppuaddr(addr, size, value)
    local byte = value or 0
    if dialogue_ppu_addr_high == nil then
        dialogue_ppu_addr_high = byte % 0x40
    else
        dialogue_ppu_addr = dialogue_ppu_addr_high * 0x100 + byte
        dialogue_ppu_addr_high = nil
    end
end
local function on_dialogue_ppudata(addr, size, value)
    if is_dialogue_row(dialogue_ppu_addr) then
        dialogue_log(table.concat({
            emu.framecount(), string.format("%04X", dialogue_ppu_addr), string.format("%02X", value or 0),
            string.format("%04X", read_register("pc")), string.format("%04X", text_pointer()),
            string.format("%04X", stream_pointer()), string.format("%02X", read_register("y")),
        }, "\t"), dialogue_ppu_path)
    end
    dialogue_ppu_addr = (dialogue_ppu_addr + 1) % 0x4000
end
local function register_dialogue_pointer(pointer)
    if pointer < 0x8000 or pointer > 0xBFFF or pointer == dialogue_last_pointer then return end
    dialogue_last_pointer = pointer
    append(dialogue_pointer_path, table.concat({
        emu.framecount(), string.format("%04X", pointer), string.format("%04X", stream_pointer()),
    }, "\t"))
    for addr = pointer, pointer + 0x50 do register_read(addr, on_dialogue_source_read) end
end
local function on_ram_write(addr, size, value)
    if ram_trace_count < RAM_TRACE_LIMIT then
        ram_trace_count = ram_trace_count + 1
        append(ram_trace_path, table.concat({
            tostring(emu.framecount()),
            string.format("%04X", addr or 0),
            tostring(size or 1),
            string.format("%02X", (value or byte_at(addr or 0) or 0) % 0x100),
        }, "\t"))
    end
    local trace_state_range = addr ~= nil and ((addr >= 0x0430 and addr <= 0x0450) or (addr >= 0x04F0 and addr <= 0x0510) or (RAM_TRACE_OBJECTS and addr >= 0x0700 and addr <= 0x07FF) or (RAM_TRACE_OBJECT_PC and addr >= 0x02A8 and addr <= 0x02FF))
    if RAM_TRACE_PC and ram_state_trace_count < RAM_STATE_TRACE_LIMIT and trace_state_range then
        ram_state_trace_count = ram_state_trace_count + 1
        append(ram_state_trace_path, table.concat({
            tostring(emu.framecount()), string.format("%04X", addr or 0),
            string.format("%02X", (value or byte_at(addr or 0) or 0) % 0x100),
            string.format("%04X", read_register("pc")), hex2(read_register("a")),
            hex2(read_register("x")), hex2(read_register("y")), hex2(byte_at(0x04F1)),
            hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)),
            hex2(byte_at(0x0706)), hex2(byte_at(0x07BC)), hex2(byte_at(0x07E4)),
            hex2(byte_at(0x07FF)),
        }, "\t"))
    end
end
local function on_mapper_select(addr, size, value)
    mapper_select = (value or 0) % 8
end
local function on_mapper_data(addr, size, value)
    if mapper_select ~= nil then mapper_registers[mapper_select] = value or 0 end
end
local function on_ppu_control(addr, size, value)
    ppu_control = value or 0
end
local function mapper_snapshot()
    local values = {}
    for index = 0, 7 do values[#values + 1] = hex2(mapper_registers[index] or 0) end
    values[#values + 1] = hex2(ppu_control or 0)
    return table.concat(values, "\t")
end
local function on_name_source_read(addr, size, value)
    if name_source_trace_count >= NAME_SOURCE_TRACE_LIMIT then return end
    local pc = read_register("pc")
    if pc < 0xD700 or pc > 0xD7FF then return end
    name_source_trace_count = name_source_trace_count + 1
    append(name_source_trace_path, table.concat({
        emu.framecount(), string.format("%04X", addr or 0), string.format("%02X", value or 0),
        string.format("%04X", read_register("pc")), mapper_snapshot(),
    }, "\t"))
end
local function on_ppu_trace_addr(addr, size, value)
    local byte = value or 0
    if ppu_trace_addr_high == nil then
        ppu_trace_addr_high = byte % 0x40
    else
        ppu_trace_addr = ppu_trace_addr_high * 0x100 + byte
        ppu_trace_addr_high = nil
    end
end
local function on_ppu_trace_data(addr, size, value)
    if ppu_trace_count < PPU_TRACE_LIMIT and emu.framecount() >= PPU_TRACE_START and ppu_trace_addr >= 0x2000 and ppu_trace_addr < 0x2400 then
        ppu_trace_count = ppu_trace_count + 1
        append(ppu_trace_path, table.concat({
            emu.framecount(), string.format("%04X", ppu_trace_addr), string.format("%02X", value or 0),
            string.format("%04X", read_register("pc")), mapper_snapshot(),
        }, "\t"))
    end
    local increment = 1
    if math.floor((ppu_control or 0) / 4) % 2 == 1 then increment = 0x20 end
    ppu_trace_addr = (ppu_trace_addr + increment) % 0x4000
end
local function capture(frame, reason, fp)
    local prefix = string.format("%s/frame_%06d", OUT_DIR, frame)
    local ok, shot = pcall(function() return gui.gdscreenshot() end)
    if ok and shot ~= nil then
        local f = assert(io.open(prefix .. "_screen.gd", "wb")); f:write(shot); f:close()
    end
    dump_ram(prefix)
    dump_ppu(prefix)
    append(OUT_DIR .. "/captures.tsv", table.concat({
        tostring(frame), reason, fp, tostring(ok and shot ~= nil),
        hex2(byte_at(0x0720)), hex2(byte_at(0x0721)), hex2(byte_at(0x0722)), hex2(byte_at(0x0723)),
        hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)),
        mapper_snapshot(), state_writes_label(),
    }, "\t"))
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
    if EXTRA_DIALOGUE_START and frame >= 650 and frame < 665 then
        return { start = true }
    end
    return {}
end

-- The combat route alternates attack cadence and direction so a single held
-- input cannot pin the player against the first obstacle forever.
local function combat_input(frame)
    local rel = frame - 900
    if rel < 0 then return {} end
    if ADVANCE_AFTER_COMBAT and (byte_at(0x04F1) == 0x06 or byte_at(0x04F1) == 0x12) then
        if MAP_SOURCE_ROUTE then
            -- Strategy references describe Start -> B to open the encounter map,
            -- then direction+A for map-cursor travel. Keep B as a later confirm
            -- phase so both documented map actions are exercised separately.
            local map_cycle = frame % 768
            local direction = {}
            local segment = math.floor(map_cycle / 192)
            local direction_name = MAP_DIRECTION
            if MAP_SWEEP then
                local sweep = { "right", "down", "left", "up" }
                direction_name = sweep[(segment % #sweep) + 1]
            end
            if direction_name == "left" then direction.left = true
            elseif direction_name == "up" then direction.up = true
            elseif direction_name == "down" then direction.down = true
            else direction.right = true end
            local phase = map_cycle % 192
            if phase < 8 then return { start = true } end
            if phase < 16 then return {} end
            if phase < 24 then return { B = true } end
            if phase < 32 then return {} end
            if phase < 96 then direction.A = true; return direction end
            if phase < 104 then return {} end
            if phase < 168 then direction.B = true; return direction end
            return {}
        end
        -- Legacy bounded route retained for comparison with earlier reports.
        local map_cycle = frame % 96
        if map_cycle < 6 then return { start = true } end
        if map_cycle < 12 then return {} end
        if map_cycle < 54 then return { right = true, B = true } end
        if map_cycle < 60 then return {} end
        if map_cycle < 84 then return { right = true, A = true, B = true } end
        return {}
    end
    local cycle = rel % 240
    if COMBAT_GRID then
        local grid = rel % 640
        local button = grid >= 320 and "B" or "A"
        local step = grid % 320
        if step < 80 then
            if button == "A" then return { right = true, A = true } end
            return { right = true, B = true }
        end
        if step < 160 then
            if button == "A" then return { down = true, A = true } end
            return { down = true, B = true }
        end
        if step < 240 then
            if button == "A" then return { left = true, A = true } end
            return { left = true, B = true }
        end
        if button == "A" then return { up = true, A = true } end
        return { up = true, B = true }
    end
    if COMBAT_MIXED then
        if COMBAT_STATIONARY then
            if cycle < 40 then return { A = true } end
            if cycle < 80 then return { B = true } end
            if cycle < 120 then return { A = true } end
            if cycle < 160 then return { B = true } end
            return {}
        end
        if cycle < 40 then return { right = true, A = true } end
        if cycle < 80 then return { left = true, A = true } end
        if cycle < 120 then return { right = true, B = true } end
        if cycle < 160 then return { left = true, B = true } end
        if cycle < 200 then return { A = true } end
        return { B = true }
    end
    if COMBAT_SWEEP then
        if cycle < 60 then return { right = true, A = true, B = true } end
        if cycle < 120 then return { down = true, A = true, B = true } end
        if cycle < 180 then return { left = true, A = true, B = true } end
        return { up = true, A = true, B = true }
    end
    if COMBAT_NO_B then
        if cycle < 120 then return { right = true, A = true } end
        if cycle < 168 then return { left = true, A = true } end
        if cycle < 216 then return { right = true, A = true } end
        return { up = true, A = true }
    end
    if cycle < 72 then return { right = true, A = true, B = true } end
    if cycle < 96 then return { right = true, B = true } end
    if cycle < 144 then return { left = true, A = true, B = true } end
    if cycle < 168 then return { left = true, A = true } end
    if cycle < 216 then return { right = true, A = true } end
    return { up = true, A = true, B = true }
end

mkdir(OUT_DIR)
append(OUT_DIR .. "/summary.tsv", "frame\treason\tunique\tlast_fingerprint")
append(OUT_DIR .. "/summary.tsv", table.concat({"0", "lua_start", "0", ""}, "\t"))
append(OUT_DIR .. "/captures.tsv", "frame\treason\tfingerprint\tscreenshot\t0720\t0721\t0722\t0723\t04F1\t04FA\t04FB\t04FC\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tppu_ctrl\tstate_writes")
append(OUT_DIR .. "/heartbeat.tsv", "frame\tphase\tbuttons\tfingerprint")
if DIALOGUE_TRACE then
    append(dialogue_pointer_path, "frame\ttext_pointer\tstream_pointer")
    append(dialogue_source_path, "frame\taddress\tvalue\tpc\ta\tx\ty\ttext_pointer\tstream_pointer")
    append(dialogue_parser_path, "frame\tlabel\tpc\ta\tx\ty\ttext_pointer\tstream_pointer")
    append(dialogue_ppu_path, "frame\tppu_address\tvalue\tpc\ttext_pointer\tstream_pointer\ty")
end

if COMBAT_SLOT_TRACE then
    append(combat_slot_trace_path, "frame\tlabel\tpc\ta\tx\ty\t0049\t0050\t0057\t00BA\t00C3\t0496\t04AC\t04B4\t76AF\t76B4\t04F1\t04FA\t04FB\t04FC\t7A00\t7A01\t7A02\t7A03")
    register_exec(0xFC65, function() trace_combat_slot("slot_scan_start") end)
    register_exec(0xFCEF, function() trace_combat_slot("slot_clear") end)
    register_exec(0xFD28, function() trace_combat_slot("slot_transition_check") end)
    register_exec(0xEF85, function() trace_combat_slot("frame_counter") end)
    register_exec(0xEF88, function() trace_combat_slot("sub_counter") end)
    register_exec(0xEFA7, function() trace_combat_slot("post_clear_dispatch") end)
end

if PPU_TRACE then
    append(ppu_trace_path, "frame\tppu_address\tvalue\tpc\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tppu_ctrl")
end
if NAME_SOURCE_TRACE then
    append(name_source_trace_path, "frame\tcpu_address\tvalue\tpc\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tppu_ctrl")
end
if RAM_TRACE then
    append(ram_trace_path, "frame\taddress\tsize\tvalue")
end
if STATE_MACHINE_TRACE then
    append(state_machine_trace_path, "frame\tlabel\tpc\ta\tx\ty\t04F1\t04FA\t04FB\t04FC\t2C\t2D\t28\t29\t2A\t2B\t1A\t1B")
end
if SRAM_ROUTE_TRACE then
    append(sram_route_trace_path, "frame\tlabel\tpc\ta\tx\ty\t7A00\t7A01\t7A02\t7A03\t7A04\t7A05\t04F1\t04FA\t04FB\t04FC\t0050\t0051\t0052\t0053")
end
if COUNTER_READ_TRACE then
    append(counter_read_trace_path, "frame\tlabel\tpc\ta\tx\ty\t7A00\t7A01\t7A02\t7A03\t7A04\t7A05\t04F1\t04FA\t04FB\t04FC")
end
if STATE_READ_TRACE then
    append(state_read_trace_path, "frame\taddress\tvalue\tpc\ta\tx\ty\t04F1\t04F2\t04F3\t04F4\t04FA\t04FB\t04FC\t0706\t7A01\t7A02")
end
if COMBAT_BRANCH_TRACE then
    append(combat_branch_trace_path, "frame\tlabel\tpc\ta\tx\ty\tp\t7A00\t7A01\t7A02\t04F1")
    for address = 0x8A80, 0x8A8F do register_exec(address, function() trace_combat_branch(string.format("8xxx_%04X", address)) end) end
    for address = 0xAA80, 0xAA8F do register_exec(address, function() trace_combat_branch(string.format("Axxx_%04X", address)) end) end
    for address = 0xCA80, 0xCA8F do register_exec(address, function() trace_combat_branch(string.format("Cxxx_%04X", address)) end) end
end
register_write(0x8000, 1, on_mapper_select)
register_write(0x8001, 1, on_mapper_data)
register_write(0x2000, 1, on_ppu_control)
if DIALOGUE_TRACE then
    register_write(0x2006, 1, on_dialogue_ppuaddr)
    register_write(0x2007, 1, on_dialogue_ppudata)
    register_exec(0x915A, on_dialogue_parser("parser"))
    register_exec(0x955F, on_dialogue_parser("emit_prep"))
    register_exec(0x9593, on_dialogue_parser("emit_dispatch"))
end
if STATE_MACHINE_TRACE then
    register_exec(0xD207, function() trace_state_machine("script_byte") end)
    register_exec(0xD20D, function() trace_state_machine("script_ptr") end)
    register_exec(0x8A87, function() trace_state_machine("dec_7a02_8xxx") end)
    register_exec(0xAA87, function() trace_state_machine("dec_7a02_axxx") end)
    register_exec(0xCA87, function() trace_state_machine("dec_7a02_cxxx") end)
end
if SRAM_ROUTE_TRACE then
    register_exec(0x8A87, function() trace_sram_route("dec_7a02_8xxx") end)
    register_exec(0xAA87, function() trace_sram_route("dec_7a02_axxx") end)
    register_exec(0xCA87, function() trace_sram_route("dec_7a02_cxxx") end)
end
if STATE_READ_TRACE then
    register_read(0x04F1, trace_state_read)
    register_read(0x04F2, trace_state_read)
    register_read(0x04F3, trace_state_read)
    register_read(0x04F4, trace_state_read)
end
if COUNTER_READ_TRACE then
    register_exec(0xA661, function() trace_counter_read("ora_7a01") end)
    register_exec(0xAD76, function() trace_counter_read("lda_7a01") end)
    register_exec(0xAD86, function() trace_counter_read("lda_7a03") end)
    register_exec(0xAD89, function() trace_counter_read("cmp_7a02") end)
end
if COMBAT_OBJECT_TRACE then
    append(combat_object_trace_path, "frame\tlabel\tpc\ta\tx\ty\t0430\t0431\t0432\t0433\t0434\t0435\t0436\t0437\t04F1\t04FA\t04FB\t04FC\t0706\t07BC\t07E4")
    for _, address in ipairs({0x8D02, 0x8D05, 0x8D31, 0x8D34, 0x8D60, 0x8D63}) do
        register_exec(address, function() trace_combat_object(string.format("8xxx_%04X", address)) end)
    end
    for _, address in ipairs({0xAD02, 0xAD05, 0xAD31, 0xAD34, 0xAD60, 0xAD63}) do
        register_exec(address, function() trace_combat_object(string.format("Axxx_%04X", address)) end)
    end
    for _, address in ipairs({0xCD02, 0xCD05, 0xCD31, 0xCD34, 0xCD60, 0xCD63}) do
        register_exec(address, function() trace_combat_object(string.format("Cxxx_%04X", address)) end)
    end
end

if PPU_TRACE then
    register_write(0x2006, 1, on_ppu_trace_addr)
    register_write(0x2007, 1, on_ppu_trace_data)
end
if NAME_SOURCE_TRACE then
    for address = 0x0000, 0x07FF do register_read(address, on_name_source_read) end
end
if RAM_TRACE then
    if RAM_TRACE_PC then
        append(ram_state_trace_path, "frame\taddress\tvalue\tpc\ta\tx\ty\t04F1\t04FA\t04FB\t04FC\t0706\t07BC\t07E4\t07FF")
    end
    register_write(0x0200, 0x0300, on_ram_write)
    register_write(0x0050, 0x0008, on_ram_write)
    register_write(0x04F0, 0x0020, on_ram_write)
    register_write(0x0700, 0x0100, on_ram_write)
end
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

local last_fp = nil
local last_capture = -999999
local unique = 0
local last_heartbeat = -1

while emu.framecount() < MAX_FRAMES and unique < UNIQUE_LIMIT do
    local frame = emu.framecount()
    if DIALOGUE_TRACE then register_dialogue_pointer(text_pointer()) end
    local buttons = frame < 900 and entry_input(frame) or combat_input(frame)
    if frame >= STATE_WRITE_START and frame <= STATE_WRITE_END and #STATE_WRITES > 0 then
        write_state_bytes()
    end
    joypad.set(1, buttons)
    local phase = frame < 900 and "entry" or "combat"
    if frame >= STATE_WRITE_START and frame <= STATE_WRITE_END and #STATE_WRITES > 0 then
        phase = "combat_inject"
    end
    if frame % 60 == 0 then
        local names = {}
        for key, value in pairs(buttons) do if value then names[#names + 1] = key end end
        append(OUT_DIR .. "/heartbeat.tsv", table.concat({tostring(frame), phase, table.concat(names, "+"), fingerprint()}, "\t"))
    end
    gui.text(2, 8, "Kunio stage progression probe")
    gui.text(2, 17, phase .. " frame=" .. tostring(frame) .. " unique=" .. tostring(unique))
    emu.frameadvance()

    if frame >= 120 and frame - last_capture >= SNAPSHOT_GAP then
        local fp = fingerprint()
        if fp ~= last_fp then
            unique = unique + 1
            last_fp = fp
            last_capture = frame
            capture(frame, phase .. "_screen_change", fp)
        end
    end
end

local reason = unique >= UNIQUE_LIMIT and "unique_limit" or "lua_done"
append(OUT_DIR .. "/captures.tsv", table.concat({tostring(emu.framecount()), reason, fingerprint(), "false", "", "", "", "", "", "", "", "", mapper_snapshot(), state_writes_label()}, "\t"))
append(OUT_DIR .. "/summary.tsv", table.concat({tostring(emu.framecount()), reason, tostring(unique), fingerprint()}, "\t"))
append(OUT_DIR .. "/summary.tsv", table.concat({tostring(emu.framecount()), "lua_done", tostring(unique), fingerprint()}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
