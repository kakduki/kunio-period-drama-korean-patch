-- Bounded route probe for the first non-opening pointer-dialogue batch.
--
-- This reuses the project's previously bounded menu/stage route, but watches
-- only pointer records 2 and 3. It is a route probe, not free-form autoplay:
-- it has a hard frame ceiling and records the final reason explicitly.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pointer_dialogue_route_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "5000")
local HIT_LIMIT = tonumber(os.getenv("KUNIO_HIT_LIMIT") or "5000")
local READ_LOG_LIMIT = tonumber(os.getenv("KUNIO_READ_LOG_LIMIT") or "200")
local TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or ""

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function byte_at(addr, domain)
    if domain ~= nil then
        local ok, value = pcall(function() return memory.readbyte(addr, domain) end)
        if ok and value ~= nil then return value end
    end
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return 0
end

local function hex2(value)
    return string.format("%02X", value % 0x100)
end

local function parse_bytes(text)
    local values = {}
    for token in string.gmatch(text or "", "%x%x") do
        values[#values + 1] = tonumber(token, 16)
    end
    return values
end

local mapper_index = 0
local mapper_registers = {}
local prg_mode = 0
local function register_write(addr, callback)
    local ok = pcall(function() memory.registerwrite(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerwrite(addr, 1, callback) end)
end
local function on_mapper_select(addr, size, value)
    local byte = value or byte_at(addr or 0)
    mapper_index = byte % 8
    prg_mode = math.floor(byte / 64) % 2
end
local function on_mapper_data(addr, size, value)
    mapper_registers[mapper_index] = value or byte_at(addr or 0)
end
local function mapped_prg_bank(address)
    local bank
    if address >= 0x8000 and address < 0xA000 then
        bank = prg_mode == 0 and (mapper_registers[6] or -1) or 14
    elseif address >= 0xA000 and address < 0xC000 then
        bank = mapper_registers[7] or -1
    elseif address >= 0xC000 and address < 0xE000 then
        bank = prg_mode == 0 and 14 or (mapper_registers[6] or -1)
    elseif address >= 0xE000 then
        bank = 15
    else
        bank = -1
    end
    return bank
end
local function mapper_snapshot()
    local values = {}
    for index = 0, 7 do values[#values + 1] = hex2(mapper_registers[index] or 0) end
    values[#values + 1] = hex2(prg_mode)
    return table.concat(values, " ")
end

local function matches(target)
    local expected_bank = target.prg_bank
    if expected_bank == nil and target.rom ~= nil then
        expected_bank = math.floor((target.rom - 0x10) / 0x2000)
    end
    if expected_bank ~= nil and mapped_prg_bank(target.start) ~= expected_bank then return false end
    local expected = parse_bytes(target.bytes)
    if #expected ~= target.stop - target.start + 1 then return false end
    for index, value in ipairs(expected) do
        if byte_at(target.start + index - 1) ~= value then return false end
    end
    return true
end

local function screen_fingerprint()
    local hash = 0
    local sum = 0
    for addr = 0x2000, 0x23BF, 8 do
        local value = byte_at(addr, "ppu")
        hash = (hash * 131 + value + addr) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end

local function register_read(addr, callback)
    if memory.registerread == nil then return false end
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(addr, 1, callback) end)
end

local function joy_for_frame(frame)
    if frame < 200 then
        return {}
    end
    if frame <= 3000 then
        local rel = frame - 200
        if rel < 15 then return { start = true } end
        if rel >= 150 and rel < 165 then return { start = true } end
        if rel >= 600 and rel < 615 then return { start = true } end
        if rel >= 220 then
            local nav = (rel - 220) % 60
            if nav < 10 then return { down = true } end
            if nav >= 30 and nav < 40 then return { up = true } end
        end
        return {}
    end

    local rel = frame - 3001
    if rel < 5 then return { start = true } end
    if rel < 10 then return {} end
    if rel < 1500 then return { right = true, B = true } end
    return { right = true, A = true, B = true }
end

local targets = {}
if TARGETS_LUA ~= "" then
    local ok, loaded = pcall(dofile, TARGETS_LUA)
    if ok and type(loaded) == "table" then targets = loaded end
end
if #targets == 0 then targets = {
    {
        label = "pointer_002_korean_relocated",
        start = 0x9FD6,
        stop = 0x9FE0,
        rom = 0x05FE6,
        bytes = "F0 BB 97 71 8C CA 8F 85 82 BA FF",
    },
    {
        label = "pointer_003_korean_relocated",
        start = 0x9FE1,
        stop = 0x9FF5,
        rom = 0x05FF1,
        bytes = "F0 BB 84 00 89 95 8C 00 85 99 86 CC F8 C0 B6 8A 8C 9A 98 CA FF",
    },
} end

local summary_path = OUT_DIR .. "/summary.tsv"
local read_log_path = OUT_DIR .. "/target_reads.tsv"
mkdir(OUT_DIR)
append(summary_path, "frame\treason\ttarget\tscreenshot\ttarget_match\tphase\thits\tscreen_fingerprint")
append(summary_path, table.concat({"0", "target_loaded", tostring(#targets), "false", "false", "1", "0", ""}, "\t"))
append(read_log_path, "frame\ttarget\tstart\tvalues\tmatch\tmapped_bank\tmapper")

local hits = 0
local read_logs = 0
local captured = false
local captured_target = ""
local function target_values(target)
    local values = {}
    for addr = target.start, target.stop do
        values[#values + 1] = hex2(byte_at(addr))
    end
    return table.concat(values, " ")
end


local function capture(target)
    local frame = emu.framecount()
    local screenshot_ok = false
    local ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if ok and screenshot ~= nil then
        local f = assert(io.open(OUT_DIR .. "/route_frame_" .. string.format("%06d", frame) .. ".gd", "wb"))
        f:write(screenshot)
        f:close()
        screenshot_ok = true
    end
    append(summary_path, table.concat({
        tostring(frame),
        "target_capture",
        target.label,
        tostring(screenshot_ok),
        tostring(matches(target)),
        tostring(frame < 200 and 1 or (frame <= 3000 and 2 or 3)),
        tostring(hits),
        screen_fingerprint(),
    }, "\t"))
end

register_write(0x8000, on_mapper_select)
register_write(0x8001, on_mapper_data)

for _, target in ipairs(targets) do
    for addr = target.start, target.stop do
        register_read(addr, function()
            if hits < HIT_LIMIT then hits = hits + 1 end
            local is_match = matches(target)
            if read_logs < READ_LOG_LIMIT then
                read_logs = read_logs + 1
                append(read_log_path, table.concat({
                    tostring(emu.framecount()),
                    target.label,
                    string.format("$%04X", target.start),
                    target_values(target),
                    tostring(is_match),
                    tostring(mapped_prg_bank(target.start)),
                    mapper_snapshot(),
                }, "\t"))
            end
            if not captured and is_match then
                captured = true
                captured_target = target.label
                capture(target)
            end
        end)
    end
end

append(summary_path, table.concat({"0", "lua_start", "pointer_targets", "false", "false", "1", tostring(hits), ""}, "\t"))
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and not captured do
    local frame = emu.framecount()
    joypad.set(1, joy_for_frame(frame))
    gui.text(2, 8, "Pointer dialogue route probe")
    gui.text(2, 17, "bounded menu/stage route")
    gui.text(2, 26, "frame=" .. tostring(frame) .. " hits=" .. tostring(hits) .. " bank=" .. tostring(mapped_prg_bank(0x9FD6)))
    emu.frameadvance()
    if frame > 0 and frame % 600 == 0 then
        append(summary_path, table.concat({
            tostring(frame),
            "periodic",
            "pointer_targets",
            "false",
            "false",
            tostring(frame < 200 and 1 or (frame <= 3000 and 2 or 3)),
            tostring(hits),
            screen_fingerprint(),
        }, "\t"))
    end
end

local reason = captured and "target_capture" or "target_not_seen"
append(summary_path, table.concat({
    tostring(emu.framecount()),
    reason,
    captured_target ~= "" and captured_target or "pointer_targets",
    "false",
    tostring(captured),
    tostring(emu.framecount() < 200 and 1 or (emu.framecount() <= 3000 and 2 or 3)),
    tostring(hits),
    screen_fingerprint(),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
