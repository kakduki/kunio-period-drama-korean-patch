-- Focused capture for the v0.4.2 Katana visual target.
--
-- Older PPU evidence showed the base-ROM Katana bytes being written around
-- frames 1976-1984 with this autoplay menu route. This script replays only
-- that bounded route on the patched ROM and dumps the target frames.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."

KUNIO_TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or (LUA_DIR .. "/kunio_v041_conflict_safe_targets.lua")
KUNIO_MANUAL_DUMP_OUTPUT = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/katana_autoplay_route_capture_v042")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = true
local manual = dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = nil

local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "2100")
local summary_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/katana_autoplay_route_capture_summary.tsv"
local heartbeat_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/katana_autoplay_route_capture_heartbeat.tsv"
local capture_frames = {
    [1942] = "pre_katana_ppu_burst",
    [1976] = "katana_write_start",
    [1980] = "katana_middle",
    [1984] = "katana_write_end",
    [2024] = "post_katana_menu_line",
}

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

local function screen_fingerprint()
    local hash = 0
    local sum = 0
    for addr = 0x2000, 0x23BF, 4 do
        local value = byte_at(addr, "ppu")
        hash = (hash * 131 + value + addr) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end

local function get_phase(frame)
    if frame < 200 then return 1 end
    if frame <= 3000 then return 2 end
    return 3
end

local function joy_for_frame(frame)
    local phase = get_phase(frame)
    if phase == 1 then
        return {}
    elseif phase == 2 then
        local rel = frame - 200
        if rel < 15 then return { start = true } end
        if rel >= 150 and rel < 165 then return { start = true } end
        if rel >= 600 and rel < 615 then return { start = true } end
        if rel >= 220 then
            local nav = (rel - 220) % 60
            if nav < 10 then return { down = true } end
            if nav >= 30 and nav < 40 then return { up = true } end
        end
    else
        local rel = frame - 3001
        if rel < 5 then return { start = true } end
        if rel < 10 then return {} end
        if rel < 1500 then return { right = true, B = true } end
        return { right = true, A = true, B = true }
    end
    return {}
end

local function buttons_label(buttons)
    local keys = {}
    for key, value in pairs(buttons) do
        if value then keys[#keys + 1] = key end
    end
    table.sort(keys)
    return table.concat(keys, "+")
end

mkdir(KUNIO_MANUAL_DUMP_OUTPUT)
append(summary_path, "frame\tphase\tcapture_label\tfingerprint\tdump_prefix")
append(heartbeat_path, "frame\tphase\tbuttons\tfingerprint")
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    local phase = get_phase(frame)
    local buttons = joy_for_frame(frame)
    joypad.set(1, buttons)
    gui.text(2, 8, "Kunio Katana autoplay-route capture")
    gui.text(2, 17, "frame=" .. tostring(frame) .. " phase=" .. tostring(phase))
    gui.text(2, 26, "target=ROM+0x07227")
    emu.frameadvance()

    if frame % 120 == 0 then
        append(heartbeat_path, table.concat({
            tostring(frame),
            tostring(phase),
            buttons_label(buttons),
            screen_fingerprint(),
        }, "\t"))
    end

    local capture_label = capture_frames[frame]
    if capture_label ~= nil then
        local ok, prefix = pcall(function() return manual.dump_current_screen() end)
        append(summary_path, table.concat({
            tostring(frame),
            tostring(phase),
            capture_label,
            screen_fingerprint(),
            ok and tostring(prefix) or ("ERROR:" .. tostring(prefix)),
        }, "\t"))
    end
end

append(summary_path, table.concat({ tostring(emu.framecount()), "done", "done", screen_fingerprint(), "" }, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
