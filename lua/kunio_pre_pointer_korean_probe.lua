-- Bounded comparison probe for ten fixed Bank 1 pre-pointer labels.
--
-- Run this script once against the English reference and once against the
-- Korean candidate. It follows the short title/menu route used by the
-- existing pre-pointer scan, then records CPU matches plus a bounded PPU
-- nametable/screenshot snapshot for each first match.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pre_pointer_korean_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "900")
local MAX_CAPTURES = 10
local SCAN_START = 0x9600
local SCAN_END = 0x9DFF
local PPU_WRITE_LIMIT = 40000
local PPU_TAIL_LIMIT = 1600

local TARGETS = {
    { id = "EN-PRE-112", offset = "05AEB", english = {0x82,0x8D,0x90,0x8B,0x8E,0x81,0x92,0x94,0xFF}, korean = {0x81,0x82,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-118", offset = "05B1B", english = {0x97,0x81,0x92,0x90,0x93,0x88,0x8F,0x94,0xFF}, korean = {0x83,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-119", offset = "05B24", english = {0x84,0x85,0x86,0x8C,0x85,0x83,0x94,0xFF}, korean = {0x84,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-125", offset = "05B4E", english = {0x95,0x84,0x8F,0x8E,0xFF}, korean = {0x85,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-129", offset = "05B61", english = {0x94,0x85,0x8E,0x90,0x95,0x92,0x81,0xFF}, korean = {0x86,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-130", offset = "05B69", english = {0x84,0x81,0x8E,0x87,0x8F,0xFF}, korean = {0x87,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-134", offset = "05B85", english = {0x93,0x81,0x8C,0x96,0x85,0xFF}, korean = {0x87,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-135", offset = "05B8B", english = {0x90,0x8F,0x95,0x8C,0x94,0x89,0x83,0x85,0xFF}, korean = {0x88,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-138", offset = "05BA2", english = {0x85,0x8C,0x89,0x98,0x89,0x92,0xFF}, korean = {0x88,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF} },
    { id = "EN-PRE-185", offset = "05CE0", english = {0x8B,0x89,0x83,0x8B,0xFF}, korean = {0x89,0xFF,0xFF,0xFF,0xFF} },
}

local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function hex2(value)
    return string.format("%02X", (value or 0) % 0x100)
end

local function hex4(value)
    return string.format("%04X", (value or 0) % 0x10000)
end

local function read_byte(addr)
    local ok, value = pcall(function() return memory.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return 0
end

local function ppu_byte(addr)
    local ok, value = pcall(function() return ppu.readbyte(addr) end)
    if ok and value ~= nil then return value end
    return nil
end

local function bytes_text(bytes)
    local values = {}
    for _, value in ipairs(bytes) do values[#values + 1] = hex2(value) end
    return table.concat(values, " ")
end

local function pattern_at(addr, bytes)
    for index, expected in ipairs(bytes) do
        if read_byte(addr + index - 1) ~= expected then return false end
    end
    return true
end

local function source_cpu_address(target)
    -- Bank 1 is mapped from ROM PRG offset 0x4010 into CPU $8000.
    return 0x8000 + (tonumber(target.offset, 16) - 0x4010)
end

local ppu_addr_high = nil
local ppu_addr = 0
local ppu_increment = 1
local ppu_write_count = 0
local ppu_hash = 0
local ppu_value_counts = {}
local recent_ppu_writes = {}
local ppu_writes_path = OUT_DIR .. "/ppu_writes.tsv"

local function read_pc()
    local ok, value = pcall(function() return memory.getregister("pc") end)
    if ok and value ~= nil then return value end
    return 0
end

local function on_ppu_control(addr, size, value)
    ppu_increment = (math.floor((value or 0) / 4) % 2 == 1) and 32 or 1
end

local function on_ppu_status_read(addr, size, value)
    ppu_addr_high = nil
end

local function on_ppu_scroll_write(addr, size, value)
    ppu_addr_high = nil
end

local function on_ppu_address_write(addr, size, value)
    local byte = value or 0
    if ppu_addr_high == nil then
        ppu_addr_high = byte % 0x40
    else
        ppu_addr = ppu_addr_high * 0x100 + byte
        ppu_addr_high = nil
    end
end

local function on_ppu_data_write(addr, size, value)
    local target = ppu_addr % 0x4000
    if target >= 0x2000 and target < 0x3000 then
        local byte = value or 0
        ppu_hash = (ppu_hash * 131 + target + byte + emu.framecount()) % 0x100000000
        ppu_value_counts[byte] = (ppu_value_counts[byte] or 0) + 1
        if ppu_write_count < PPU_WRITE_LIMIT then
            local line = table.concat({
                emu.framecount(),
                hex4(target),
                hex2(byte),
                hex4(read_pc()),
            }, "\t")
            append(ppu_writes_path, line)
            ppu_write_count = ppu_write_count + 1
            if #recent_ppu_writes >= PPU_TAIL_LIMIT then table.remove(recent_ppu_writes, 1) end
            recent_ppu_writes[#recent_ppu_writes + 1] = line
        end
    end
    ppu_addr = (ppu_addr + ppu_increment) % 0x4000
end

local function register_write(address, size, callback)
    local ok = pcall(function() memory.registerwrite(address, size, callback) end)
    if ok then return true end
    if size == 1 then
        ok = pcall(function() memory.registerwrite(address, callback) end)
    end
    return ok
end

local function register_read(address, callback)
    local ok = pcall(function() memory.registerread(address, 1, callback) end)
    if ok then return true end
    return pcall(function() memory.registerread(address, callback) end)
end
local function ppu_fingerprint()
    return string.format("%08X", ppu_hash), ppu_write_count
end

local function ppu_code_count(bytes)
    local counts = {}
    for _, code in ipairs(bytes) do
        if code ~= 0x00 and code ~= 0xFF then
            counts[hex2(code)] = ppu_value_counts[code] or 0
        end
    end
    local parts = {}
    for key, value in pairs(counts) do parts[#parts + 1] = key .. ":" .. tostring(value) end
    table.sort(parts)
    return table.concat(parts, ",")
end

local function dump_ppu(path)
    local f = assert(io.open(path, "wb"))
    for offset = 0, 0x3BF do
        local value = ppu_byte(0x2000 + offset)
        if value == nil then
            f:close()
            return false
        end
        f:write(string.char(value))
    end
    f:close()
    return true
end

local function capture_target(target, representation, cpu_addr, frame)
    local fingerprint, write_count = ppu_fingerprint()
    local stem = OUT_DIR .. "/" .. target.id .. "_" .. representation
    local screenshot_ok, screenshot = pcall(function() return gui.gdscreenshot() end)
    if screenshot_ok and screenshot ~= nil then
        local f = assert(io.open(stem .. "_screen.gd", "wb"))
        f:write(screenshot)
        f:close()
    end
    local ppu_read_ok = dump_ppu(stem .. "_nametable.bin")
    local tail = assert(io.open(stem .. "_ppu_tail.tsv", "w"))
    tail:write("frame\tppu_address\tvalue\tpc\n")
    for _, line in ipairs(recent_ppu_writes) do tail:write(line .. "\n") end
    tail:close()
    append(OUT_DIR .. "/captures.tsv", table.concat({
        frame,
        target.id,
        target.offset,
        representation,
        "$" .. hex4(cpu_addr),
        tostring(screenshot_ok and screenshot ~= nil),
        fingerprint,
        write_count,
        tostring(ppu_read_ok),
        ppu_code_count(representation == "english" and target.english or target.korean),
    }, "\t"))
end

-- This is deliberately short and mirrors the proven pre-pointer scan route.
local function joy_for_frame(frame)
    if frame < 90 then
        return {}
    elseif frame < 105 then
        return { start = true }
    elseif frame < 150 then
        return {}
    elseif frame < 165 then
        return { start = true }
    elseif frame < 230 then
        return {}
    elseif frame < 245 then
        return { A = true }
    elseif frame < 320 then
        return {}
    elseif frame < 335 then
        return { start = true }
    elseif frame % 180 < 10 then
        return { A = true }
    elseif frame % 240 > 120 and frame % 240 < 134 then
        return { right = true }
    end
    return {}
end

mkdir(OUT_DIR)
local summary_path = OUT_DIR .. "/summary.tsv"
local matches_path = OUT_DIR .. "/matches.tsv"
local captures_path = OUT_DIR .. "/captures.tsv"
append(summary_path, "frame\treason\tmatched_targets\tfirst_target\tppu_fingerprint")
append(matches_path, "frame\ttarget\toffset\trepresentation\tcpu_addr\tbytes\tppu_fingerprint\tppu_write_count")
append(captures_path, "frame\ttarget\toffset\trepresentation\tcpu_addr\tscreenshot_ok\tppu_fingerprint\tppu_write_count\tppu_read_ok\tppu_code_counts")
append(ppu_writes_path, "frame\tppu_address\tvalue\tpc")
local ppu_callbacks = {
    control = register_write(0x2000, 1, on_ppu_control),
    status = register_read(0x2002, on_ppu_status_read),
    scroll = register_write(0x2005, 1, on_ppu_scroll_write),
    address = register_write(0x2006, 1, on_ppu_address_write),
    data = register_write(0x2007, 1, on_ppu_data_write),
}
append(summary_path, "0\tcallbacks\t" .. tostring(ppu_callbacks.control and ppu_callbacks.status and ppu_callbacks.scroll and ppu_callbacks.address and ppu_callbacks.data) .. "\t\t")

local seen = {}
local captured = {}
local pending = {}
local matched_count = 0
local last_summary_frame = -1
append(summary_path, "0\tlua_start\t0\t\t")

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
    local frame = emu.framecount()
    joypad.set(1, joy_for_frame(frame))
    for target_id, item in pairs(pending) do
        if frame >= item.capture_frame and captured[target_id] == nil then
            captured[target_id] = true
            capture_target(item.target, item.representation, item.cpu_addr, frame)
            pending[target_id] = nil
        end
    end
    local first_target = ""
    for _, target in ipairs(TARGETS) do
        local addr = source_cpu_address(target)
        for _, representation in ipairs({"english", "korean"}) do
            local bytes = representation == "english" and target.english or target.korean
            local key = target.id .. ":" .. representation
            if pattern_at(addr, bytes) and seen[key] == nil then
                seen[key] = true
                matched_count = matched_count + 1
                local fingerprint, write_count = ppu_fingerprint()
                append(matches_path, table.concat({
                    frame,
                    target.id,
                    target.offset,
                    representation,
                    "$" .. hex4(addr),
                    bytes_text(bytes),
                    fingerprint,
                    write_count,
                }, "\t"))
                if first_target == "" then
                    first_target = target.id .. ":" .. representation
                end
                if captured[target.id] == nil and pending[target.id] == nil and MAX_CAPTURES > 0 then
                    pending[target.id] = {
                        target = target,
                        representation = representation,
                        cpu_addr = addr,
                        capture_frame = frame + 5,
                    }
                end
            end
        end
    end
    if frame % 60 == 0 and last_summary_frame ~= frame then
        local fingerprint = ppu_fingerprint()
        append(summary_path, table.concat({frame, "periodic", matched_count, first_target, fingerprint}, "\t"))
        last_summary_frame = frame
    end
    gui.text(2, 8, "Pre-pointer compare " .. tostring(frame))
    gui.text(2, 17, "matches=" .. tostring(matched_count))
    emu.frameadvance()
end

local missing = {}
for _, target in ipairs(TARGETS) do
    if captured[target.id] == nil then missing[#missing + 1] = target.id end
end
append(summary_path, table.concat({
    emu.framecount(),
    "lua_done",
    matched_count,
    table.concat(missing, ","),
    ppu_fingerprint(),
}, "\t"))
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
