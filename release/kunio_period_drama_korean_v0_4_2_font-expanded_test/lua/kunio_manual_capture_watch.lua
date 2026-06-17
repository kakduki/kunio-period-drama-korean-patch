-- kunio_manual_capture_watch.lua
--
-- Keep this Lua script running while manually playing. Press D on an exact
-- text/menu/status screen to write a manual dump without reopening Lua.
-- Press Q to stop the watcher. It does not autoplay.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then
        source = string.sub(source, 2)
    end
    local dir = string.match(source, "^(.*)[/\\][^/\\]+$")
    return dir or "."
end

local LUA_DIR = script_dir()

KUNIO_MANUAL_DUMP_DEFINE_ONLY = true
local manual = dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = nil

local last_dump_frame = -999
local last_message = "Manual capture watcher ready"
local last_message_frame = 0
local watcher_title = KUNIO_WATCHER_TITLE or "Kunio manual capture watch"
local watcher_hint = KUNIO_WATCHER_HINT or ""

local function key_pressed(keys, ...)
    for _, name in ipairs({...}) do
        if keys[name] then
            return true
        end
    end
    return false
end

local function current_keys()
    local ok, keys = pcall(function() return input.get() end)
    if ok and type(keys) == "table" then
        return keys
    end
    return {}
end

while true do
    local frame = emu.framecount()
    local keys = current_keys()
    local dump_now = key_pressed(keys, "D", "d")
    local stop_now = key_pressed(keys, "Q", "q", "Escape", "ESC")

    if dump_now and frame - last_dump_frame > 20 then
        local ok, prefix = pcall(function() return manual.dump_current_screen() end)
        last_dump_frame = frame
        last_message_frame = frame
        if ok then
            last_message = "Dump saved: " .. tostring(prefix)
        else
            last_message = "Dump failed: " .. tostring(prefix)
        end
    end

    gui.text(2, 8, watcher_title)
    gui.text(2, 17, "D=dump current screen  Q=stop")
    gui.text(2, 26, manual.output_dir or "")
    if watcher_hint ~= "" then
        gui.text(2, 35, watcher_hint)
    end
    if frame - last_message_frame < 180 then
        gui.text(2, watcher_hint ~= "" and 44 or 35, last_message)
    end

    if stop_now then
        print("Kunio manual capture watcher stopped")
        break
    end

    emu.frameadvance()
end
