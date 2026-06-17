-- kunio_manual_v042_screen_dump.lua
--
-- Run this on the v0.4.2 font-expanded candidate ROM after manually reaching
-- a target screen. It reuses the v0.4.1 PRG target expectations because v0.4.2
-- changes only the font expansion layer beyond those text edits.

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

dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
