-- kunio_manual_screen_dump.lua
--
-- Manual capture helper for real gameplay screens.
--
-- Workflow:
--   1. Open the ROM in FCEUX.
--   2. Manually play to a dialogue/menu/status screen worth analyzing.
--   3. Run this Lua script from FCEUX's Lua window.
--
-- The script does not autoplay. It captures the current screen state, CPU RAM,
-- SRAM range, and current bytes for generated Bank 1 watch targets.

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
local OUT_DIR = rawget(_G, "KUNIO_MANUAL_DUMP_OUTPUT")
    or os.getenv("KUNIO_MANUAL_DUMP_OUTPUT")
    or (ROOT_DIR .. "/rom_analysis/manual_screen_dump")
local TARGETS_LUA = rawget(_G, "KUNIO_TARGETS_LUA")
    or os.getenv("KUNIO_TARGETS_LUA")
    or (LUA_DIR .. "/kunio_bank1_targets.lua")

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function hex2(v)
    return string.format("%02X", (v or 0) % 0x100)
end

local function hex4(v)
    return string.format("%04X", (v or 0) % 0x10000)
end

local function byte_at(addr)
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    if ok and value ~= nil then
        return value
    end
    return 0
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function write_text(path, text)
    local f = assert(io.open(path, "w"))
    f:write(text)
    f:close()
end

local function dump_range(path, start_addr, length)
    local f = assert(io.open(path, "wb"))
    for i = 0, length - 1 do
        f:write(string.char(byte_at(start_addr + i)))
    end
    f:close()
end

local function dump_hex(path, start_addr, length)
    local f = assert(io.open(path, "w"))
    for row = 0, length - 1, 16 do
        f:write(hex4(start_addr + row) .. ":")
        for col = 0, 15 do
            if row + col < length then
                f:write(" " .. hex2(byte_at(start_addr + row + col)))
            end
        end
        f:write("\n")
    end
    f:close()
end

local function parse_bytes(text)
    local out = {}
    for byte in string.gmatch(text or "", "%x%x") do
        out[#out + 1] = tonumber(byte, 16)
    end
    return out
end

local function record_snapshot(start_addr, stop_addr)
    local parts = {}
    for addr = start_addr, stop_addr do
        parts[#parts + 1] = hex2(byte_at(addr))
    end
    return table.concat(parts, " ")
end

local function contains_expected(snapshot, expected)
    local record = parse_bytes(snapshot)
    local wanted = parse_bytes(expected)
    if #wanted == 0 or #record < #wanted then
        return false
    end
    for index = 1, #record - #wanted + 1 do
        local ok = true
        for offset = 1, #wanted do
            if record[index + offset - 1] ~= wanted[offset] then
                ok = false
                break
            end
        end
        if ok then return true end
    end
    return false
end

local function load_targets()
    local ok, result = pcall(dofile, TARGETS_LUA)
    if ok and type(result) == "table" then
        return result, "loaded:" .. TARGETS_LUA
    end
    return {}, "missing-or-invalid:" .. TARGETS_LUA
end

local function dump_current_screen()
    mkdir(OUT_DIR)

    local frame = emu.framecount()
    local targets, target_status = load_targets()
    local prefix = string.format("%s/manual_frame_%06d", OUT_DIR, frame)

    write_text(prefix .. "_meta.txt", table.concat({
        "frame=" .. tostring(frame),
        "output=" .. OUT_DIR,
        "targets=" .. target_status,
        "target_count=" .. tostring(#targets),
    }, "\n") .. "\n")

    dump_range(prefix .. "_cpu_ram.bin", 0x0000, 0x0800)
    dump_hex(prefix .. "_cpu_ram.txt", 0x0000, 0x0800)
    dump_range(prefix .. "_sram_6000_7fff.bin", 0x6000, 0x2000)
    dump_hex(prefix .. "_sram_6000_7fff.txt", 0x6000, 0x2000)

    local screenshot_ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if screenshot_ok and screenshot ~= nil then
        local f = assert(io.open(prefix .. "_screen.gd", "wb"))
        f:write(screenshot)
        f:close()
    end

    local records_path = prefix .. "_target_records.tsv"
    append(records_path, "frame\tlabel\tcategory\trom_hit\tcpu_range\texpected_bytes\tactive_expected_match\trecord_snapshot")
    for _, target in ipairs(targets) do
        local start_addr = target.start or 0
        local stop_addr = target.stop or start_addr
        local snapshot = record_snapshot(start_addr, stop_addr)
        local expected = target.bytes or ""
        append(records_path, table.concat({
            tostring(frame),
            target.label or "?",
            target.category or "?",
            target.rom and string.format("ROM+0x%05X", target.rom) or "?",
            "$" .. hex4(start_addr) .. "-$" .. hex4(stop_addr),
            expected,
            tostring(contains_expected(snapshot, expected)),
            snapshot,
        }, "\t"))
    end

    gui.text(2, 8, "Kunio manual dump saved")
    gui.text(2, 17, OUT_DIR)
    print("Kunio manual dump saved: " .. prefix)
    return prefix
end

if rawget(_G, "KUNIO_MANUAL_DUMP_DEFINE_ONLY") then
    return {
        dump_current_screen = dump_current_screen,
        output_dir = OUT_DIR,
        targets_lua = TARGETS_LUA,
    }
end

dump_current_screen()
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
