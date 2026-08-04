-- Bounded loader trace for a manifest candidate and the Japanese base.
--
-- This follows the known opening acknowledgement route, but records the
-- loader hook, dialogue ID, pointer-table reads, and selected record reads so
-- a zero target hit can be separated into route, hook, or mapping evidence.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/manifest_loader_trace"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1900")
local FIRST_ADVANCE_START = tonumber(os.getenv("KUNIO_FIRST_ADVANCE_START") or "900")
local FIRST_ADVANCE_END = tonumber(os.getenv("KUNIO_FIRST_ADVANCE_END") or "910")
local SECOND_ADVANCE_START = tonumber(os.getenv("KUNIO_SECOND_ADVANCE_START") or "1110")
local SECOND_ADVANCE_END = tonumber(os.getenv("KUNIO_SECOND_ADVANCE_END") or "1120")
local THIRD_ADVANCE_START = tonumber(os.getenv("KUNIO_THIRD_ADVANCE_START") or "1520")
local THIRD_ADVANCE_END = tonumber(os.getenv("KUNIO_THIRD_ADVANCE_END") or "1530")
local TRACE_LIMIT = tonumber(os.getenv("KUNIO_TRACE_LIMIT") or "2000")

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local file = assert(io.open(path, "a"))
    file:write(line .. "\n")
    file:close()
end

local function hex2(value)
    return string.format("%02X", (value or 0) % 0x100)
end

local function hex4(value)
    return string.format("%04X", (value or 0) % 0x10000)
end

local function byte_at(address, domain)
    if domain ~= nil then
        local ok, value = pcall(function() return memory.readbyte(address, domain) end)
        if ok and value ~= nil then return value end
    end
    local ok, value = pcall(function() return memory.readbyte(address) end)
    return ok and value or 0
end

local function register_read(address, callback)
    local ok = pcall(function() memory.registerread(address, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(address, 1, callback) end)
end

local function register_exec(address, callback)
    local ok = pcall(function() memory.registerexec(address, callback) end)
    if ok then return true end
    return pcall(function() memory.registerexecute(address, callback) end)
end

local function register_event(path, label, address, size, value)
    append(path, table.concat({
        emu.framecount(), label, "$" .. hex4(address), hex2(value),
        "$" .. hex4(byte_at(0x708B)), "$" .. hex4(byte_at(0x07FD)),
        hex2(byte_at(0x07FE)), hex2(byte_at(0x07FF)),
    }, "\t"))
end

local function trace_exec(path, label)
    return function()
        if emu.framecount() <= MAX_FRAMES then
            register_event(path, label, 0, 0, 0)
        end
    end
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
    if frame >= FIRST_ADVANCE_START and frame < FIRST_ADVANCE_END then return { B = true } end
    if frame >= SECOND_ADVANCE_START and frame < SECOND_ADVANCE_END then return { B = true } end
    if frame >= THIRD_ADVANCE_START and frame < THIRD_ADVANCE_END then return { B = true } end
    return {}
end

mkdir(OUT_DIR)
local summary_path = OUT_DIR .. "/summary.tsv"
local exec_path = OUT_DIR .. "/loader_exec.tsv"
local read_path = OUT_DIR .. "/loader_reads.tsv"
local record_path = OUT_DIR .. "/record_reads.tsv"
append(summary_path, "frame\treason\thook_execs\tloader_reads\trecord_reads\tdialogue_id\tpage_state")
append(exec_path, "frame\tlabel\taddress\tvalue\tdialogue_id\ttemp_high\ttemp_id\tpage_state")
append(read_path, "frame\tlabel\taddress\tvalue\tdialogue_id\ttemp_high\ttemp_id\tpage_state")
append(record_path, "frame\tlabel\taddress\tvalue\tdialogue_id\ttemp_high\ttemp_id\tpage_state")

local hook_execs = 0
local loader_reads = 0
local record_reads = 0
local trace_rows = 0

local function bounded_log(path, label, address, value)
    if trace_rows >= TRACE_LIMIT then return end
    trace_rows = trace_rows + 1
    register_event(path, label, address, 1, value)
end

local function on_loader_exec(label)
    return function()
        hook_execs = hook_execs + 1
        bounded_log(exec_path, label, 0x9137, 0)
    end
end

local function on_loader_read(label)
    return function(address, size, value)
        loader_reads = loader_reads + 1
        bounded_log(read_path, label, address or 0, value or byte_at(address or 0))
    end
end

local function on_record_read(label)
    return function(address, size, value)
        record_reads = record_reads + 1
        bounded_log(record_path, label, address or 0, value or byte_at(address or 0))
    end
end

register_exec(0x9137, on_loader_exec("loader_hook"))
register_exec(0xAFF0, on_loader_exec("loader_cave"))
register_read(0x708B, on_loader_read("dialogue_id"))
register_read(0x9F40, on_loader_read("pointer_182_lo"))
register_read(0x9F41, on_loader_read("pointer_182_hi"))
register_read(0x9F46, on_loader_read("pointer_185_lo"))
register_read(0x9F47, on_loader_read("pointer_185_hi"))
for address = 0x9FB4, 0x9FD8 do
    register_read(address, on_record_read("candidate_record_window"))
end
for address = 0xB1A6, 0xB206 do
    register_read(address, on_record_read("base_record_window"))
end

append(summary_path, table.concat({
    0, "lua_start", hook_execs, loader_reads, record_reads,
    hex2(byte_at(0x708B)), hex2(byte_at(0x07FF)),
}, "\t"))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)
while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "Manifest loader trace " .. tostring(frame))
    gui.text(2, 17, "hook=" .. tostring(hook_execs) .. " id=" .. hex2(byte_at(0x708B)))
    emu.frameadvance()
end

append(summary_path, table.concat({
    emu.framecount(), "lua_done", hook_execs, loader_reads, record_reads,
    hex2(byte_at(0x708B)), hex2(byte_at(0x07FF)),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
