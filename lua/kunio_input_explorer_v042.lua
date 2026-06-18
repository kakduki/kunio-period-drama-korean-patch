-- Automated input explorer for the v0.4.2 primary patch.
--
-- This is not a final proof script. It replaces blind waiting with a bounded
-- set of menu/gameplay input patterns and saves a manual-style dump whenever
-- the visible nametable fingerprint changes. Use its output to find reachable
-- screens without requiring a person to navigate FCEUX.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then
        source = string.sub(source, 2)
    end
    local dir = string.match(source, "^(.*)[/\\][^/\\]+$")
    return dir or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."

KUNIO_TARGETS_LUA = LUA_DIR .. "/kunio_v041_conflict_safe_targets.lua"
KUNIO_MANUAL_DUMP_OUTPUT = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/auto_input_explorer_v042")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = true
local manual = dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = nil

local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "7200")
local SNAPSHOT_GAP = tonumber(os.getenv("KUNIO_EXPLORER_SNAPSHOT_GAP") or "240")
local UNIQUE_LIMIT = tonumber(os.getenv("KUNIO_EXPLORER_UNIQUE_LIMIT") or "36")

local summary_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/explorer_summary.tsv"
local heartbeat_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/explorer_heartbeat.tsv"
local last_fingerprint = nil
local last_dump_frame = -999999
local unique_count = 0

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
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

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
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

local function press_for(rel, start_frame, duration, buttons)
    if rel >= start_frame and rel < start_frame + duration then
        return buttons
    end
    return nil
end

local routes = {
    {
        name = "start_a_menu",
        length = 960,
        input = function(rel)
            return press_for(rel, 40, 10, { start = true })
                or press_for(rel, 130, 10, { A = true })
                or press_for(rel, 220, 10, { start = true })
                or press_for(rel, 300, 10, { down = true })
                or press_for(rel, 360, 10, { A = true })
                or press_for(rel, 480, 10, { down = true })
                or press_for(rel, 540, 10, { A = true })
                or press_for(rel, 700, 12, { B = true })
                or {}
        end,
    },
    {
        name = "start_select_inventory",
        length = 960,
        input = function(rel)
            return press_for(rel, 40, 10, { start = true })
                or press_for(rel, 130, 10, { select = true })
                or press_for(rel, 220, 10, { start = true })
                or press_for(rel, 300, 10, { right = true })
                or press_for(rel, 360, 10, { A = true })
                or press_for(rel, 480, 10, { down = true })
                or press_for(rel, 540, 10, { A = true })
                or press_for(rel, 700, 12, { B = true })
                or {}
        end,
    },
    {
        name = "field_right_menu_cycle",
        length = 1200,
        input = function(rel)
            if rel < 40 then return {} end
            if rel < 55 then return { start = true } end
            if rel < 400 then return { right = true, B = true } end
            return press_for(rel, 430, 10, { start = true })
                or press_for(rel, 520, 10, { down = true })
                or press_for(rel, 580, 10, { A = true })
                or press_for(rel, 700, 10, { down = true })
                or press_for(rel, 760, 10, { A = true })
                or {}
        end,
    },
    {
        name = "field_left_select_cycle",
        length = 1200,
        input = function(rel)
            if rel < 40 then return {} end
            if rel < 55 then return { start = true } end
            if rel < 400 then return { left = true, B = true } end
            return press_for(rel, 430, 10, { select = true })
                or press_for(rel, 520, 10, { down = true })
                or press_for(rel, 580, 10, { A = true })
                or press_for(rel, 700, 10, { right = true })
                or press_for(rel, 760, 10, { A = true })
                or {}
        end,
    },
}

local function route_for_frame(frame)
    local cursor = 0
    for _, route in ipairs(routes) do
        if frame < cursor + route.length then
            return route, frame - cursor
        end
        cursor = cursor + route.length
    end
    local loop_frame = (frame - cursor) % 480
    return {
        name = "fallback_cycle",
        input = function(rel)
            if rel < 15 then return { start = true } end
            if rel >= 80 and rel < 92 then return { select = true } end
            if rel >= 160 and rel < 172 then return { down = true } end
            if rel >= 220 and rel < 232 then return { A = true } end
            if rel >= 320 and rel < 332 then return { B = true } end
            return {}
        end,
    }, loop_frame
end

mkdir(KUNIO_MANUAL_DUMP_OUTPUT)
append(summary_path, "frame\troute\tfingerprint\tdump_prefix")
append(heartbeat_path, "frame\troute\trel\tbuttons")
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES and unique_count < UNIQUE_LIMIT do
    local frame = emu.framecount()
    local route, rel = route_for_frame(frame)
    local buttons = route.input(rel)
    joypad.set(1, buttons)
    if frame % 60 == 0 then
        local pressed = {}
        for key, value in pairs(buttons) do
            if value then pressed[#pressed + 1] = key end
        end
        append(heartbeat_path, table.concat({
            tostring(frame),
            route.name,
            tostring(rel),
            table.concat(pressed, "+"),
        }, "\t"))
    end
    gui.text(2, 8, "Kunio auto input explorer")
    gui.text(2, 17, "route=" .. route.name .. " frame=" .. tostring(frame))
    gui.text(2, 26, "unique=" .. tostring(unique_count))
    emu.frameadvance()

    if frame > 120 and frame - last_dump_frame >= SNAPSHOT_GAP then
        local fingerprint = screen_fingerprint()
        if fingerprint ~= last_fingerprint then
            unique_count = unique_count + 1
            last_dump_frame = frame
            last_fingerprint = fingerprint
            local ok, prefix = pcall(function() return manual.dump_current_screen() end)
            append(summary_path, table.concat({
                tostring(frame),
                route.name,
                fingerprint,
                ok and tostring(prefix) or ("ERROR:" .. tostring(prefix)),
            }, "\t"))
        end
    end
end

append(summary_path, table.concat({
    tostring(emu.framecount()),
    "done",
    tostring(last_fingerprint or ""),
    "unique=" .. tostring(unique_count),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
