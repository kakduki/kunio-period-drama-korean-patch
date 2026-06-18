-- Focused Katana item-list state probe for v0.4.2.
--
-- This uses the proven Katana visual-explorer route that reaches the item-list
-- screen, then writes only explicitly listed candidate inventory/runtime bytes.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."

KUNIO_TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or (LUA_DIR .. "/kunio_v041_conflict_safe_targets.lua")
KUNIO_MANUAL_DUMP_OUTPUT = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/katana_itemlist_state_probe_v042")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = true
local manual = dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = nil

local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "3000")
local INJECT_START = tonumber(os.getenv("KUNIO_INJECT_START") or "1860")
local INJECT_END = tonumber(os.getenv("KUNIO_INJECT_END") or "2520")
local SNAPSHOT_GAP = tonumber(os.getenv("KUNIO_KATANA_ITEMLIST_SNAPSHOT_GAP") or "90")
local WRITES_TEXT = os.getenv("KUNIO_KATANA_WRITES")
    or "0x0502=0x3C,0x0503=0x3E,0x0506=0x01,0x0508=0x9C,0x0509=0x42,0x0700=0x82,0x0701=0x0C,0x0702=0x0C,0x0706=0x00,0x0707=0x6E,0x071F=0x01"

local summary_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/katana_itemlist_state_probe_summary.tsv"
local heartbeat_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/katana_itemlist_state_probe_heartbeat.tsv"
local last_fingerprint = nil
local last_dump_frame = -999999

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function parse_writes(text)
    local writes = {}
    for part in string.gmatch(text or "", "([^,]+)") do
        local addr_text, value_text = string.match(part, "^%s*([^=]+)%s*=%s*([^=]+)%s*$")
        local addr = tonumber(addr_text)
        local value = tonumber(value_text)
        if addr ~= nil and value ~= nil then
            writes[#writes + 1] = { addr = addr, value = value }
        end
    end
    return writes
end

local WRITES = parse_writes(WRITES_TEXT)

local function writes_label()
    local parts = {}
    for _, item in ipairs(WRITES) do
        parts[#parts + 1] = string.format("0x%04X=0x%02X", item.addr, item.value)
    end
    return table.concat(parts, ",")
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

local function write_byte(addr, value)
    pcall(function() memory.writebyte(addr, value) end)
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
    if rel >= start_frame and rel < start_frame + duration then return buttons end
    return nil
end

local function opening_route(frame)
    return press_for(frame, 40, 10, { start = true })
        or press_for(frame, 130, 10, { A = true })
        or press_for(frame, 220, 10, { start = true })
        or press_for(frame, 300, 10, { down = true })
        or press_for(frame, 360, 10, { A = true })
        or press_for(frame, 480, 10, { down = true })
        or press_for(frame, 540, 10, { A = true })
        or press_for(frame, 700, 12, { B = true })
        or press_for(frame, 880, 12, { A = true })
        or press_for(frame, 940, 12, { A = true })
        or {}
end

local menu_patterns = {
    { name = "start_down_a", buttons = { "start", "down", "A", "down", "A", "B" } },
    { name = "select_down_a", buttons = { "select", "down", "A", "right", "A", "B" } },
    { name = "start_right_a", buttons = { "start", "right", "A", "down", "A", "B" } },
    { name = "select_right_a", buttons = { "select", "right", "A", "down", "A", "B" } },
    { name = "menu_left_a", buttons = { "left", "A", "down", "A", "B", "left", "A" } },
    { name = "start_up_a", buttons = { "start", "up", "A", "left", "A", "B" } },
}

local function button_table(name)
    local result = {}
    result[name] = true
    return result
end

local function itemlist_route(frame)
    local rel = frame - 1020
    if rel < 0 then return opening_route(frame), "opening" end
    local pattern_span = 300
    local pattern = menu_patterns[(math.floor(rel / pattern_span) % #menu_patterns) + 1]
    local inner = rel % pattern_span
    for index, button in ipairs(pattern.buttons) do
        local start_frame = 20 + ((index - 1) * 42)
        local buttons = press_for(inner, start_frame, 12, button_table(button))
        if buttons ~= nil then return buttons, pattern.name end
    end
    return {}, pattern.name
end

mkdir(KUNIO_MANUAL_DUMP_OUTPUT)
append(summary_path, "frame\tphase\troute\tfingerprint\tdump_prefix\twrites")
append(heartbeat_path, "frame\tphase\troute\tbuttons\twrites")
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    local buttons, route_name = itemlist_route(frame)
    local phase = "route"
    if frame >= INJECT_START and frame <= INJECT_END then
        for _, item in ipairs(WRITES) do
            write_byte(item.addr, item.value)
        end
        phase = "inject"
    end
    joypad.set(1, buttons)
    if frame % 60 == 0 then
        local pressed = {}
        for key, value in pairs(buttons) do
            if value then pressed[#pressed + 1] = key end
        end
        append(heartbeat_path, table.concat({ tostring(frame), phase, route_name, table.concat(pressed, "+"), writes_label() }, "\t"))
    end
    gui.text(2, 8, "Kunio Katana item-list state probe")
    gui.text(2, 17, "route=" .. route_name .. " phase=" .. phase)
    gui.text(2, 26, "writes=" .. tostring(#WRITES))
    emu.frameadvance()

    if frame > 120 and frame - last_dump_frame >= SNAPSHOT_GAP then
        local fingerprint = screen_fingerprint()
        if fingerprint ~= last_fingerprint then
            last_dump_frame = frame
            last_fingerprint = fingerprint
            local ok, prefix = pcall(function() return manual.dump_current_screen() end)
            append(summary_path, table.concat({
                tostring(frame),
                phase,
                route_name,
                fingerprint,
                ok and tostring(prefix) or ("ERROR:" .. tostring(prefix)),
                writes_label(),
            }, "\t"))
        end
    end
end

append(summary_path, table.concat({ tostring(emu.framecount()), "done", "done", tostring(last_fingerprint or ""), "", writes_label() }, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
