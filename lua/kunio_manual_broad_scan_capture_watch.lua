-- kunio_manual_broad_scan_capture_watch.lua
--
-- Watcher for base-ROM broad-scan proof tasks. Open the base Japanese ROM, run
-- this script once, then press D on a candidate screen.

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

KUNIO_TARGETS_LUA = LUA_DIR .. "/kunio_broad_scan_candidate_targets.lua"
KUNIO_MANUAL_DUMP_OUTPUT = ROOT_DIR .. "/rom_analysis/manual_screen_dump_broad_scan"

dofile(LUA_DIR .. "/kunio_manual_capture_watch.lua")
