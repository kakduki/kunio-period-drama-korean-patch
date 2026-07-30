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

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line)
    local f = assert(io.open(path, "a")); f:write(line .. "\n"); f:close()
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
        mapper_snapshot(),
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
    return {}
end

-- The combat route alternates attack cadence and direction so a single held
-- input cannot pin the player against the first obstacle forever.
local function combat_input(frame)
    local rel = frame - 900
    if rel < 0 then return {} end
    local cycle = rel % 240
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
append(OUT_DIR .. "/captures.tsv", "frame\treason\tfingerprint\tscreenshot\t0720\t0721\t0722\t0723\t04F1\t04FA\t04FB\t04FC\tr0\tr1\tr2\tr3\tr4\tr5\tr6\tr7\tppu_ctrl")
append(OUT_DIR .. "/heartbeat.tsv", "frame\tphase\tbuttons\tfingerprint")
register_write(0x8000, 1, on_mapper_select)
register_write(0x8001, 1, on_mapper_data)
register_write(0x2000, 1, on_ppu_control)
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

local last_fp = nil
local last_capture = -999999
local unique = 0
local last_heartbeat = -1

while emu.framecount() < MAX_FRAMES and unique < UNIQUE_LIMIT do
    local frame = emu.framecount()
    local buttons = frame < 900 and entry_input(frame) or combat_input(frame)
    joypad.set(1, buttons)
    local phase = frame < 900 and "entry" or "combat"
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
append(OUT_DIR .. "/captures.tsv", table.concat({tostring(emu.framecount()), reason, fingerprint(), "false", "", "", "", "", "", "", "", "", mapper_snapshot()}, "\t"))
append(OUT_DIR .. "/summary.tsv", table.concat({tostring(emu.framecount()), reason, tostring(unique), fingerprint()}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
