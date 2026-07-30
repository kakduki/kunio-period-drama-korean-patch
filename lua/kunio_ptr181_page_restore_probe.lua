-- Bounded PTR-181 page activation and dismissal/restore probe.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/ptr181_page_restore_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES")) or 1200
local summary_path = OUT_DIR .. "/summary.tsv"
local mapper_select = nil
local mapper_registers = {}
local saw_target = false
local saw_restore = false

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local file = assert(io.open(path, "a"))
    file:write(line .. "\n")
    file:close()
end

local function byte_at(address)
    local ok, value = pcall(function() return memory.readbyte(address) end)
    return ok and value or 0
end

local function hex2(value)
    return string.format("%02X", (value or 0) % 0x100)
end

local function register_write(address, callback)
    local ok = pcall(function() memory.registerwrite(address, 1, callback) end)
    if ok then return true end
    return pcall(function() memory.registerwrite(address, callback) end)
end

local function on_mapper_select(address, size, value)
    mapper_select = (value or 0) % 8
end

local function on_mapper_data(address, size, value)
    if mapper_select ~= nil then mapper_registers[mapper_select] = value or 0 end
end

local function route_input(frame)
    if frame >= 40 and frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame >= 360 and frame < 370 then return { A = true } end
    if frame >= 430 and frame < 445 then return { A = true } end
    if frame >= 500 and frame < 515 then return { B = true } end
    if frame >= 580 and frame < 595 then return { A = true } end
    return {}
end

local function sample(frame, reason)
    local state = byte_at(0x07FF)
    local r1 = mapper_registers[1] or 0
    if state == 4 and r1 == 0x86 then saw_target = true end
    if saw_target and state == 0 and r1 == 0x3E then saw_restore = true end
    append(summary_path, table.concat({
        frame, reason, hex2(byte_at(0x51)), hex2(byte_at(0x07FD)),
        hex2(byte_at(0x07FE)), hex2(state), hex2(r1),
        tostring(saw_target), tostring(saw_restore),
    }, "\t"))
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tram51\tram07fd\tram07fe\tram07ff\tr1\tsaw_target\tsaw_restore")
register_write(0x8000, on_mapper_select)
register_write(0x8001, on_mapper_data)
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and not saw_restore do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    if frame % 30 == 0 then sample(frame, "sample") end
    gui.text(2, 8, "PTR181 page restore " .. tostring(frame))
    gui.text(2, 17, "target=" .. tostring(saw_target) .. " restore=" .. tostring(saw_restore))
    emu.frameadvance()
end

sample(emu.framecount(), saw_restore and "lua_done" or "target_not_seen")
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
