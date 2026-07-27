-- Bounded probe for the first non-opening pointer-dialogue batch.
-- It follows only the known opening route, then terminates with
-- target_not_seen if the early-boss records are not reached.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pointer_dialogue_batch_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1200")
local HIT_LIMIT = tonumber(os.getenv("KUNIO_HIT_LIMIT") or "5000")

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function byte_at(addr)
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

local function capture(target)
    local frame = emu.framecount()
    local screenshot_ok = false
    local ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if ok and screenshot ~= nil then
        local f = assert(io.open(OUT_DIR .. "/pointer_batch_frame_" .. string.format("%06d", frame) .. ".gd", "wb"))
        f:write(screenshot)
        f:close()
        screenshot_ok = true
    end
    append(OUT_DIR .. "/summary.tsv", table.concat({
        frame, "target_capture", target.label, tostring(screenshot_ok), tostring(matches(target))
    }, "\t"))
end

local function register_read(addr, callback)
    if memory.registerread == nil then return false end
    local ok = pcall(function() memory.registerread(addr, callback) end)
    if ok then return true end
    ok = pcall(function() memory.registerread(addr, 1, callback) end)
    return ok
end

mkdir(OUT_DIR)
append(OUT_DIR .. "/summary.tsv", "frame\treason\ttarget\tscreenshot\ttarget_match")
local targets = {
    {
        label = "pointer_002_korean_early_boss",
        start = 0xA004,
        stop = 0xA010,
        bytes = "F0 BB 00 81 82 83 84 85 86 87 88 CA FF"
    },
    {
        label = "pointer_003_korean_early_boss",
        start = 0xA011,
        stop = 0xA042,
        bytes = "F0 BB 00 89 8A 8B 8C 8D 8E 8F 90 00 91 92 93 94 95 96 CA F8 97 98 99 9A 8F 90 C0 C1 C2 C3 CA 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF"
    }
}
append(OUT_DIR .. "/summary.tsv", table.concat({0, "target_loaded", tostring(#targets), tostring(false), tostring(false)}, "\t"))
local captured = false
local hits = 0
local registered = 0
for _, target in ipairs(targets) do
    for addr = target.start, target.stop do
        local callback = function()
            if hits < HIT_LIMIT then hits = hits + 1 end
            if not captured and matches(target) then
                captured = true
                capture(target)
            end
        end
        if register_read(addr, callback) then
            registered = registered + 1
        end
    end
end

append(OUT_DIR .. "/summary.tsv", table.concat({0, "watchers_registered", tostring(registered), tostring(false), tostring(false)}, "\t"))
append(OUT_DIR .. "/summary.tsv", table.concat({0, "lua_start", "pointer_002_003", tostring(false), tostring(false)}, "\t"))
while emu.framecount() < MAX_FRAMES and not captured do
    local frame = emu.framecount()
    joypad.set(1, route_input(frame))
    gui.text(2, 8, "Pointer dialogue batch probe")
    gui.text(2, 17, "bounded opening route; no blind autoplay")
    gui.text(2, 26, "targets reached=" .. tostring(captured) .. " hits=" .. tostring(hits))
    emu.frameadvance()
end

local reason = captured and "target_capture" or "target_not_seen"
append(OUT_DIR .. "/summary.tsv", table.concat({emu.framecount(), reason, "pointer_002_003", tostring(false), tostring(captured)}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
