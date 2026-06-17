-- kunio_manual_v04_screen_dump.lua
--
-- Run this on the v0.4 equal-length static experiment ROM after manually
-- reaching a target screen. It captures the current screen using patched-byte
-- expectations from lua/kunio_v04_equal_length_targets.lua.

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

KUNIO_TARGETS_LUA = LUA_DIR .. "/kunio_v04_equal_length_targets.lua"
KUNIO_MANUAL_DUMP_OUTPUT = ROOT_DIR .. "/rom_analysis/manual_screen_dump_v04"

dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
