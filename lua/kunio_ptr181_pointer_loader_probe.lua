-- Bounded trace of the PTR-181 pointer-table reads.
-- This identifies the loader PC/register contract without playing past the
-- already reproducible opening-to-field route.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/ptr181_pointer_loader_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES")) or 450
local POINTER_LOW = 0x9F2E
local POINTER_HIGH = 0x9F2F
local TRACE_LIMIT = 128

local summary_path = OUT_DIR .. "/summary.tsv"
local reads_path = OUT_DIR .. "/pointer_table_reads.tsv"
local trace_count = 0

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local file = assert(io.open(path, "a"))
    file:write(line .. "\n")
    file:close()
end

local function read_byte(address)
    local ok, value = pcall(function() return memory.readbyte(address) end)
    if ok and value ~= nil then return value end
    return 0
end

local function reg(name)
    local ok, value = pcall(function() return memory.getregister(name) end)
    if ok and value ~= nil then return value end
    return 0
end

local function hex2(value)
    return string.format("%02X", (value or 0) % 0x100)
end

local function hex4(value)
    return string.format("%04X", (value or 0) % 0x10000)
end

local function register_read(address, callback)
    local ok = pcall(function() memory.registerread(address, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(address, 1, callback) end)
end

local function on_pointer_read(address, size, value)
    if trace_count >= TRACE_LIMIT then return end
    trace_count = trace_count + 1
    local sp = reg("s")
    append(reads_path, table.concat({
        emu.framecount(), hex4(address), hex2(value or read_byte(address)),
        hex4(reg("pc")), hex2(reg("a")), hex2(reg("x")), hex2(reg("y")),
        hex2(sp), hex2(read_byte(0x100 + ((sp + 1) % 0x100))),
        hex2(read_byte(0x100 + ((sp + 2) % 0x100))),
        hex2(read_byte(0x18)), hex2(read_byte(0x19)),
        hex2(read_byte(0x1A)), hex2(read_byte(0x1B)),
    }, "\t"))
end

local function route_input(frame)
    if frame >= 40 and frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    return {}
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tlow_registered\thigh_registered\ttrace_count")
append(reads_path, "frame\taddress\tvalue\tpc\ta\tx\ty\tsp\tstack1\tstack2\tram18\tram19\tram1A\tram1B")

local low_registered = register_read(POINTER_LOW, on_pointer_read)
local high_registered = register_read(POINTER_HIGH, on_pointer_read)
append(summary_path, table.concat({
    0, "lua_start", tostring(low_registered), tostring(high_registered), trace_count
}, "\t"))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "PTR181 pointer loader " .. tostring(frame))
    gui.text(2, 17, "reads=" .. tostring(trace_count))
    emu.frameadvance()
end

append(summary_path, table.concat({
    emu.framecount(), "lua_done", tostring(low_registered),
    tostring(high_registered), trace_count
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
