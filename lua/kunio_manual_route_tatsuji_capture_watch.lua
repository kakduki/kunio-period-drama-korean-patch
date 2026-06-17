-- Auto-generated route watcher for Tatsuji.
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

KUNIO_TARGETS_LUA = LUA_DIR .. "/kunio_route_tatsuji_targets.lua"
KUNIO_MANUAL_DUMP_OUTPUT = ROOT_DIR .. "/rom_analysis/manual_screen_dump_broad_scan"
KUNIO_WATCHER_TITLE = "Kunio route 2: Tatsuji (3 targets)"
KUNIO_WATCHER_HINT = "look for a visible Tatsuji boss/name context"

dofile(LUA_DIR .. "/kunio_manual_capture_watch.lua")
