-- Bounded route probe for the first direct 8x16 Korean pointer batch.
-- It watches the relocated p0/p1/p2 records and stops on a complete match.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pointer_dialogue_batch_000_002_8x16_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "5000")
local HIT_LIMIT = tonumber(os.getenv("KUNIO_HIT_LIMIT") or "5000")

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

local function parse_bytes(text)
    local values = {}
    for token in string.gmatch(text or "", "%x%x") do
        values[#values + 1] = tonumber(token, 16)
    end
    return values
end

local function matches(target)
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
    if frame < 200 then return {} end
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

local targets = {
    {
        label = "pointer_000_korean_direct_8x16",
        start = 0x9FD7,
        stop = 0x9FF4,
        bytes = "F0 BB 00 81 82 00 83 84 85 86 00 87 88 00 83 89 8A 00 8B 8C 8D 00 8E 00 8A 87 8F 90 CA FF",
    },
    {
        label = "pointer_001_korean_direct_8x16",
        start = 0x9FF5,
        stop = 0x9FFC,
        bytes = "F0 BB 00 91 92 86 CA FF",
    },
    {
        label = "pointer_002_korean_direct_8x16",
        start = 0x9FFD,
        stop = 0xA00A,
        bytes = "F0 BB 00 93 94 00 95 00 96 97 98 86 CA FF",
    },
}

local summary_path = OUT_DIR .. "/summary.tsv"
mkdir(OUT_DIR)
append(summary_path, "frame\treason\ttarget\tscreenshot\ttarget_match\tphase\thits\tscreen_fingerprint")
append(summary_path, table.concat({"0", "target_loaded", tostring(#targets), "false", "false", "1", "0", ""}, "\t"))

local hits = 0
local captured = false
local captured_target = ""

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
        tostring(frame), "target_capture", target.label, tostring(screenshot_ok), tostring(matches(target)),
        tostring(frame < 200 and 1 or (frame <= 3000 and 2 or 3)), tostring(hits), screen_fingerprint()
    }, "\t"))
end

for _, target in ipairs(targets) do
    for addr = target.start, target.stop do
        register_read(addr, function()
            if hits < HIT_LIMIT then hits = hits + 1 end
            if not captured and matches(target) then
                captured = true
                captured_target = target.label
                capture(target)
            end
        end)
    end
end

append(summary_path, table.concat({"0", "lua_start", "pointer_000_002_8x16", "false", "false", "1", tostring(hits), ""}, "\t"))
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and not captured do
    local frame = emu.framecount()
    joypad.set(1, joy_for_frame(frame))
    gui.text(2, 8, "Pointer direct 8x16 route probe")
    gui.text(2, 17, "bounded menu/stage route")
    gui.text(2, 26, "frame=" .. tostring(frame) .. " hits=" .. tostring(hits))
    emu.frameadvance()
    if frame > 0 and frame % 600 == 0 then
        append(summary_path, table.concat({
            tostring(frame), "periodic", "pointer_000_002_8x16", "false", "false",
            tostring(frame < 200 and 1 or (frame <= 3000 and 2 or 3)), tostring(hits), screen_fingerprint()
        }, "\t"))
    end
end

local reason = captured and "target_capture" or "target_not_seen"
append(summary_path, table.concat({
    tostring(emu.framecount()), reason, captured_target ~= "" and captured_target or "pointer_000_002_8x16",
    "false", tostring(captured), tostring(emu.framecount() < 200 and 1 or (emu.framecount() <= 3000 and 2 or 3)),
    tostring(hits), screen_fingerprint()
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
