-- Bounded controller probe for the full pointer Korean candidate.
--
-- The known entry route reaches the first full-pointer dialogue around frame
-- 330. After that point, test one controller input at a time so a stuck
-- dialogue cannot be mistaken for an autoplay/title-screen loop.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or
    "rom_analysis/full_pointer_dialogue_input_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1900")
local summary_path = OUT_DIR .. "/summary.tsv"

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local file = assert(io.open(path, "a"))
    file:write(line .. "\n")
    file:close()
end

local function byte_at(address, domain)
    local ok, value
    if domain ~= nil then
        ok, value = pcall(function() return memory.readbyte(address, domain) end)
        if ok and value ~= nil then return value end
    end
    ok, value = pcall(function() return memory.readbyte(address) end)
    return ok and value or 0
end

local function hex2(value)
    return string.format("%02X", (value or 0) % 0x100)
end

local function fingerprint()
    local hash, sum = 0, 0
    for address = 0x2000, 0x23BF, 8 do
        local value = byte_at(address, "ppu")
        hash = (hash * 131 + value + address) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end

local function buttons_label(buttons)
    local names = {}
    for name, pressed in pairs(buttons or {}) do
        if pressed then names[#names + 1] = name end
    end
    table.sort(names)
    return table.concat(names, "+")
end

local function input_for(frame)
    if frame >= 40 and frame < 50 then return { start = true } end
    if frame >= 130 and frame < 140 then return { A = true } end
    if frame >= 220 and frame < 230 then return { start = true } end
    if frame >= 300 and frame < 310 then return { down = true } end
    if frame < 330 then return {} end

    -- Each button gets a separate 15-frame press, surrounded by idle time.
    local probes = {
        { 350, "A", { A = true } },
        { 500, "B", { B = true } },
        { 650, "Start", { start = true } },
        { 800, "Select", { select = true } },
        { 950, "Up", { up = true } },
        { 1100, "Down", { down = true } },
        { 1250, "Left", { left = true } },
        { 1400, "Right", { right = true } },
        { 1550, "A+B", { A = true, B = true } },
    }
    for _, probe in ipairs(probes) do
        if frame >= probe[1] and frame < probe[1] + 15 then
            return probe[3]
        end
    end
    return {}
end

local function capture(frame, label, buttons)
    append(summary_path, table.concat({
        tostring(frame), label, buttons_label(buttons), fingerprint(),
        hex2(byte_at(0x0051)), hex2(byte_at(0x0720)), hex2(byte_at(0x0721)),
        hex2(byte_at(0x0722)), hex2(byte_at(0x0723)), hex2(byte_at(0x07FD)),
        hex2(byte_at(0x07FE)), hex2(byte_at(0x07FF)),
    }, "\t"))
end

local function probe_label(frame)
    local starts = {
        {350, "A"}, {500, "B"}, {650, "Start"}, {800, "Select"},
        {950, "Up"}, {1100, "Down"}, {1250, "Left"}, {1400, "Right"},
        {1550, "A+B"},
    }
    for _, probe in ipairs(starts) do
        if frame == probe[1] or frame == probe[1] + 15 then
            return probe[2] .. (frame == probe[1] and "_before" or "_after")
        end
    end
    return nil
end

mkdir(OUT_DIR)
append(summary_path, "frame\tlabel\tbuttons\tfingerprint\tram51\tram0720\tram0721\tram0722\tram0723\tram07fd\tram07fe\tram07ff")
append(summary_path, "0\tstart\t\t" .. fingerprint() .. "\t" ..
    hex2(byte_at(0x0051)) .. "\t" .. hex2(byte_at(0x0720)) .. "\t" ..
    hex2(byte_at(0x0721)) .. "\t" .. hex2(byte_at(0x0722)) .. "\t" ..
    hex2(byte_at(0x0723)) .. "\t" .. hex2(byte_at(0x07FD)) .. "\t" ..
    hex2(byte_at(0x07FE)) .. "\t" .. hex2(byte_at(0x07FF)))

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

local last_fingerprint = nil
while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    local buttons = input_for(frame)
    joypad.set(1, buttons)
    gui.text(2, 8, "Full pointer input probe")
    gui.text(2, 17, "frame=" .. tostring(frame) .. " page=" .. hex2(byte_at(0x07FF)))
    emu.frameadvance()

    local current = fingerprint()
    local label = probe_label(frame)
    if label ~= nil then
        capture(frame, label, buttons)
    elseif current ~= last_fingerprint and frame >= 300 then
        capture(frame, "screen_change", buttons)
    end
    last_fingerprint = current
end

capture(emu.framecount(), "lua_done", {})
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
