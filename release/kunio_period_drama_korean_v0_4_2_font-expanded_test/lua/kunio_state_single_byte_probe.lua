-- Single-byte state probe for route/scene cheat discovery.
--
-- Set KUNIO_STATE_ADDR and KUNIO_STATE_VALUE to test one suspected state byte.
-- This script intentionally avoids broad writes: one address, one value, one run.

local function script_dir()
    local source = debug.getinfo(1, "S").source or ""
    if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
    return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."

KUNIO_TARGETS_LUA = LUA_DIR .. "/kunio_broad_scan_candidate_targets.lua"
KUNIO_MANUAL_DUMP_OUTPUT = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/state_single_byte_probe")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = true
local manual = dofile(LUA_DIR .. "/kunio_manual_screen_dump.lua")
KUNIO_MANUAL_DUMP_DEFINE_ONLY = nil

local STATE_ADDR = tonumber(os.getenv("KUNIO_STATE_ADDR") or "0x0720")
local STATE_VALUE = tonumber(os.getenv("KUNIO_STATE_VALUE") or "0xB1")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "2400")
local INJECT_START = tonumber(os.getenv("KUNIO_INJECT_START") or "520")
local INJECT_END = tonumber(os.getenv("KUNIO_INJECT_END") or "1900")
local SNAPSHOT_GAP = tonumber(os.getenv("KUNIO_STATE_SNAPSHOT_GAP") or "120")

local summary_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/state_single_byte_probe_summary.tsv"
local watch_path = KUNIO_MANUAL_DUMP_OUTPUT .. "/state_single_byte_probe_watch.tsv"
local last_fingerprint = nil
local last_dump_frame = -999999

local WATCH_ADDRS = {
    0x00E7, 0x002A, 0x002C, 0x001F, 0x002D, 0x001C, 0x0020,
    0x0720, 0x0721, 0x0722, 0x0723, 0x0708, 0x07A8, 0x07A9,
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

local function press_for(frame, start_frame, duration, buttons)
    if frame >= start_frame and frame < start_frame + duration then return buttons end
    return nil
end

local function input_for(frame)
    if frame < 40 then return {} end
    return press_for(frame, 40, 10, { start = true })
        or press_for(frame, 130, 10, { A = true })
        or press_for(frame, 220, 10, { start = true })
        or press_for(frame, 300, 10, { down = true })
        or press_for(frame, 360, 10, { A = true })
        or press_for(frame, 480, 10, { down = true })
        or press_for(frame, 540, 10, { A = true })
        or press_for(frame, 700, 12, { B = true })
        or press_for(frame, 820, 12, { right = true, B = true })
        or press_for(frame, 980, 12, { right = true, B = true })
        or press_for(frame, 1140, 12, { A = true })
        or press_for(frame, 1320, 12, { start = true })
        or press_for(frame, 1440, 12, { down = true })
        or press_for(frame, 1500, 12, { A = true })
        or {}
end

local function watch_values()
    local parts = {}
    for _, addr in ipairs(WATCH_ADDRS) do
        parts[#parts + 1] = string.format("%04X=%02X", addr, byte_at(addr))
    end
    return table.concat(parts, " ")
end

mkdir(KUNIO_MANUAL_DUMP_OUTPUT)
append(summary_path, "frame\tphase\tstate_addr\tstate_value\tfingerprint\tdump_prefix")
append(watch_path, "frame\tphase\twatch_values")
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    local phase = "route"
    if frame >= INJECT_START and frame <= INJECT_END then
        write_byte(STATE_ADDR, STATE_VALUE)
        phase = "inject"
    end
    joypad.set(1, input_for(frame))
    if frame % 60 == 0 then
        append(watch_path, table.concat({ tostring(frame), phase, watch_values() }, "\t"))
    end
    gui.text(2, 8, "Kunio state single-byte probe")
    gui.text(2, 17, string.format("addr=$%04X value=$%02X frame=%d", STATE_ADDR, STATE_VALUE, frame))
    emu.frameadvance()

    if frame > 120 and frame - last_dump_frame >= SNAPSHOT_GAP then
        local fingerprint = screen_fingerprint()
        if fingerprint ~= last_fingerprint then
            last_fingerprint = fingerprint
            last_dump_frame = frame
            local ok, prefix = pcall(function() return manual.dump_current_screen() end)
            append(summary_path, table.concat({
                tostring(frame),
                phase,
                string.format("0x%04X", STATE_ADDR),
                string.format("0x%02X", STATE_VALUE),
                fingerprint,
                ok and tostring(prefix) or ("ERROR:" .. tostring(prefix)),
            }, "\t"))
        end
    end
end

append(summary_path, table.concat({
    tostring(emu.framecount()),
    "done",
    string.format("0x%04X", STATE_ADDR),
    string.format("0x%02X", STATE_VALUE),
    tostring(last_fingerprint or ""),
    "",
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
