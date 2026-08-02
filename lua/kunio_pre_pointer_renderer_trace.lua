-- Bounded trace of the shared pre-pointer text renderer.
-- The English patch keeps these renderer entry points while replacing the
-- fixed records.  Capture the active mapper/register state and CPU context
-- so a Korean page selector can be attached to the same ownership path.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pre_pointer_renderer_trace"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1200")

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end
local function byte_at(addr)
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    return ok and value or 0
end
local function reg(name)
    local ok, value = pcall(function() return memory.getregister(name) end)
    return ok and value or 0
end
local function hex2(value) return string.format("%02X", (value or 0) % 0x100) end
local function hex4(value) return string.format("%04X", (value or 0) % 0x10000) end

local function entry_input(frame)
    if frame < 40 then return {} end
    if frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    if frame >= 480 and frame < 490 then return { down = true } end
    if frame >= 540 and frame < 550 then return { A = true } end
    if frame >= 650 and frame < 665 then return { start = true } end
    if frame >= 700 and frame < 712 then return { B = true } end
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

local function register_exec(addr, callback)
    if debug.registerexec ~= nil then
        local ok = pcall(function() debug.registerexec(addr, callback) end)
        if ok then return true end
    end
    if memory.registerexec ~= nil then
        local ok = pcall(function() memory.registerexec(addr, callback) end)
        if ok then return true end
    end
    return false
end

local mapper_select = 0
local mapper = {0, 0, 0, 0, 0, 0, 0, 0}
local ppu_control = 0
local ppu_address = 0
local ppu_data = 0
local ppu_latch = false
local trace_count = 0
local trace_limit = tonumber(os.getenv("KUNIO_TRACE_LIMIT") or "20000")
local trace_path = OUT_DIR .. "/renderer_exec.tsv"
local summary_path = OUT_DIR .. "/summary.tsv"

local function on_mapper_select(addr, size, value)
    mapper_select = (value or 0) % 8
end
local function on_mapper_data(addr, size, value)
    mapper[mapper_select + 1] = value or 0
end
local function mapper_text()
    local values = {}
    for i = 1, 8 do values[#values + 1] = hex2(mapper[i]) end
    return table.concat(values, ",")
end
local function on_ppu_addr(addr, size, value)
    if not ppu_latch then
        ppu_address = ((value or 0) % 0x100) * 0x100 + (ppu_address % 0x100)
    else
        ppu_address = (ppu_address - (ppu_address % 0x100)) + ((value or 0) % 0x100)
    end
    ppu_latch = not ppu_latch
end
local function on_ppu_data(addr, size, value)
    ppu_data = value or 0
end
local function trace(label)
    if trace_count >= trace_limit then return end
    trace_count = trace_count + 1
    local parts = {
        tostring(emu.framecount()), label, "$" .. hex4(reg("pc")),
        hex2(reg("a")), hex2(reg("x")), hex2(reg("y")),
        hex2(byte_at(0x8205)), hex2(byte_at(0x8206)), hex2(byte_at(0x8207)), hex2(byte_at(0x8208)),
        hex2(byte_at(0x8209)), hex2(byte_at(0x820A)), hex2(byte_at(0x820B)), hex2(byte_at(0x820C)),
        string.format("%04X", ppu_address), hex2(ppu_data),
        "$" .. hex4(mapper[1]), "$" .. hex4(mapper[2]), "$" .. hex4(mapper[3]),
        "$" .. hex4(mapper[4]), "$" .. hex4(mapper[5]), "$" .. hex4(mapper[6]),
        "$" .. hex4(mapper[7]), "$" .. hex4(mapper[8]), hex2(ppu_control),
    }
    for _, addr in ipairs({0x0005, 0x0006, 0x0007, 0x0008, 0x0009, 0x000A, 0x000B, 0x000C, 0x0010, 0x0011, 0x0012, 0x001C, 0x001D, 0x001E, 0x001F, 0x002A, 0x002B, 0x002C, 0x002D, 0x00E7, 0x04F1, 0x04FA, 0x04FB, 0x04FC}) do
        parts[#parts + 1] = string.format("%04X=%02X", addr, byte_at(addr))
    end
    append(trace_path, table.concat(parts, "\t"))
end

mkdir(OUT_DIR)
append(trace_path, "frame\tentry\tpc\ta\tx\ty\tcode8205\tcode8206\tcode8207\tcode8208\tcode8209\tcode820A\tcode820B\tcode820C\tppu_addr\tppu_data\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tppu_ctrl\t0005\t0006\t0007\t0008\t0009\t000A\t000B\t000C\t0010\t0011\t0012\t001C\t001D\t001E\t001F\t002A\t002B\t002C\t002D\t00E7\t04F1\t04FA\t04FB\t04FC")
append(summary_path, "frame\treason\ttrace_count\texec8205\texec8209")
pcall(function() memory.registerwrite(0x8000, 1, on_mapper_select) end)
pcall(function() memory.registerwrite(0x8001, 1, on_mapper_data) end)
pcall(function() memory.registerwrite(0x2000, 1, function(addr, size, value) ppu_control = value or 0 end) end)
pcall(function() memory.registerwrite(0x2006, on_ppu_addr) end)
pcall(function() memory.registerwrite(0x2007, on_ppu_data) end)
local exec8205 = register_exec(0x8205, function() trace("8205") end)
local exec8209 = register_exec(0x8209, function() trace("8209") end)
append(trace_path, table.concat({"0", "registered", tostring(exec8205), tostring(exec8209)}, "\t"))
append(summary_path, table.concat({"0", "start", "0", tostring(exec8205), tostring(exec8209)}, "\t"))
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    joypad.set(1, frame < 900 and entry_input(frame) or combat_input(frame))
    gui.text(2, 8, "Pre-pointer renderer trace")
    gui.text(2, 17, "exec8205=" .. tostring(exec8205) .. " exec8209=" .. tostring(exec8209))
    emu.frameadvance()
end

append(trace_path, table.concat({tostring(emu.framecount()), "lua_done", tostring(trace_count)}, "\t"))
append(summary_path, table.concat({tostring(emu.framecount()), "done", tostring(trace_count), tostring(exec8205), tostring(exec8209)}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
