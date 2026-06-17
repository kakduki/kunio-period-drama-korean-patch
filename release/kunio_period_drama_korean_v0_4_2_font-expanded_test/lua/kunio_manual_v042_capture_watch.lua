-- kunio_manual_v042_capture_watch.lua
--
-- Watcher for manually verifying the v0.4.2 font-expanded candidate. Open the
-- v0.4.2 ROM, run this script once, then press D on each target screen.

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
KUNIO_MANUAL_DUMP_OUTPUT = ROOT_DIR .. "/rom_analysis/manual_screen_dump_v042"

dofile(LUA_DIR .. "/kunio_manual_capture_watch.lua")
