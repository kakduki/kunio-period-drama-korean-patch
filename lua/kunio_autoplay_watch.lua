-- kunio_autoplay_watch.lua
-- 3-phase autoplay (5000 frames) + Bank1 CPU read watch.
--   Phase 1 (0-199):    game load wait
--   Phase 2 (200-3000): menu entry (START) + direction-key navigation to collect read hits
--                       focuses on カタナ(0x07227), そうび(0x06FA1), やり, ちから etc.
--                       logs expected-bytes vs actual-bytes diff per hit
--   Phase 3 (3001-5000): close menu, advance through stage
-- Targets are loaded from kunio_bank1_targets.lua (must be in the same directory).
-- Output: KUNIO_ANALYSIS_OUTPUT env var, or rom_analysis/fceux_bank1_watch_test/ by default.
--
-- Launch via:
--   python scripts/run_fceux_lua_analysis.py \
--     --lua-script lua/kunio_autoplay_watch.lua \
--     --frames 5000 --timeout 150 \
--     --final-output rom_analysis/fceux_bank1_watch_test \
--     --clean-output --no-dump-hex --no-dump-bin

local OUT_DIR   = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/fceux_bank1_watch_test"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "5000")
local HIT_LIMIT  = tonumber(os.getenv("KUNIO_HIT_LIMIT")  or "50000")
-- per-phase hit budget: phase 2 (menu) gets 30000, phase 3 (stage) gets 20000
local PHASE2_LIMIT = tonumber(os.getenv("KUNIO_PHASE2_LIMIT") or "30000")
local PHASE3_LIMIT = tonumber(os.getenv("KUNIO_PHASE3_LIMIT") or "20000")
local STAGNATION_ABORT = os.getenv("KUNIO_STAGNATION_ABORT") ~= "0"
local STAGNATION_MIN_FRAMES = tonumber(os.getenv("KUNIO_STAGNATION_MIN_FRAMES") or "1800")
local STAGNATION_SAMPLES = tonumber(os.getenv("KUNIO_STAGNATION_SAMPLES") or "4")

local summary_path = OUT_DIR .. "/summary.tsv"
local reads_path   = OUT_DIR .. "/bank1_reads.tsv"

local hit_count        = 0
local phase2_hits      = 0
local phase3_hits      = 0
local current_phase    = 1   -- updated each frame in main loop; safe to read from callbacks
local registered_count = 0
local callback_mode    = false
local stopped_for_limit = false
local stopped_for_stagnation = false
local last_screen_fingerprint = nil
local same_screen_samples = 0

-- Load targets ----------------------------------------------------------
local targets      = {}
local target_source = "fallback"

local ok, generated = pcall(function() return dofile("kunio_bank1_targets.lua") end)
if ok and type(generated) == "table" and #generated > 0 then
    targets = generated
    target_source = "generated"
else
    -- minimal built-in set so the script still runs if the file is missing
    targets = {
        { label = "katana_watch_weapon", category = "무기",  rom = 0x05644, start = 0x9633, stop = 0x9637, bytes = "82 8C 91" },
        { label = "kusuri_recovery",     category = "회복",  rom = 0x05BDF, start = 0x9BCD, stop = 0x9BD3, bytes = "82 87 A3" },
        { label = "soubi_ui_a",          category = "UI",    rom = 0x0602E, start = 0xA01A, stop = 0xA02B, bytes = "9C 90 A8" },
        { label = "chikara_stat_a",      category = "능력치", rom = 0x06605, start = 0xA5EE, stop = 0xA5F8, bytes = "93 88 AA" },
        { label = "okane_ui",            category = "UI",    rom = 0x06DE3, start = 0xADD1, stop = 0xADD7, bytes = "85 86 98" },
    }
end

-- Helpers ---------------------------------------------------------------
local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function hex2(v) return string.format("%02X", v % 0x100) end
local function hex4(v) return string.format("%04X", v % 0x10000) end
local function hex5(v) return string.format("%05X", v % 0x100000) end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

local function byte_at(addr)
    local ok2, v = pcall(function() return memory.readbyte(addr) end)
    if ok2 and v ~= nil then return v end
    return 0
end

local function byte_at_domain(addr, domain)
    local ok2, v = pcall(function() return memory.readbyte(addr, domain) end)
    if ok2 and v ~= nil then return v end
    return byte_at(addr)
end

local function screen_fingerprint()
    local hash = 0
    local sum = 0
    for addr = 0x2000, 0x23BF, 8 do
        local value = byte_at_domain(addr, "ppu")
        hash = (hash * 131 + value + addr) % 1000000007
        sum = (sum + value) % 65536
    end
    return tostring(hash) .. ":" .. tostring(sum)
end

local function read_context(addr)
    local bytes = {}
    for offset = -2, 5 do bytes[#bytes + 1] = hex2(byte_at(addr + offset)) end
    return table.concat(bytes, " ")
end

local function split_expected_bytes(bytes_str)
    local out = {}
    for token in string.gmatch(bytes_str, "%S+") do
        out[#out + 1] = tonumber(token, 16) or -1
    end
    return out
end

local function read_record(target)
    local bytes = {}
    for addr = target.start, target.stop do bytes[#bytes + 1] = hex2(byte_at(addr)) end
    return table.concat(bytes, " ")
end

local function record_has_expected(target)
    local expected = split_expected_bytes(target.bytes)
    if #expected == 0 then return false end
    local record = {}
    for addr = target.start, target.stop do record[#record + 1] = byte_at(addr) end
    for si = 1, #record - #expected + 1 do
        local matched = true
        for offset = 1, #expected do
            if record[si + offset - 1] ~= expected[offset] then matched = false; break end
        end
        if matched then return true end
    end
    return false
end

local function compute_byte_diff(target)
    local expected = split_expected_bytes(target.bytes)
    if #expected == 0 then return "no_expected" end
    local record = {}
    for addr = target.start, target.stop do record[#record + 1] = byte_at(addr) end
    -- find best alignment of expected inside record
    local best_pos, best_matches = 1, -1
    for si = 1, #record - #expected + 1 do
        local matches = 0
        for offset = 1, #expected do
            if record[si + offset - 1] == expected[offset] then matches = matches + 1 end
        end
        if matches > best_matches then best_matches = matches; best_pos = si end
    end
    local parts = {}
    for offset = 1, #expected do
        local actual = record[best_pos + offset - 1] or 0
        local exp    = expected[offset]
        if actual == exp then
            parts[#parts + 1] = "=" .. hex2(actual)
        else
            parts[#parts + 1] = hex2(exp) .. ">" .. hex2(actual)
        end
    end
    return table.concat(parts, " ")
end

local function on_read_for(target)
    return function(addr, size, value)
        -- use global current_phase (updated each frame in main loop)
        if current_phase == 2 and phase2_hits >= PHASE2_LIMIT then return end
        if current_phase == 3 and phase3_hits >= PHASE3_LIMIT then return end
        if hit_count >= HIT_LIMIT then stopped_for_limit = true; return end
        hit_count = hit_count + 1
        if current_phase == 2 then phase2_hits = phase2_hits + 1 end
        if current_phase == 3 then phase3_hits = phase3_hits + 1 end
        local a = addr or 0
        local v = value
        if v == nil then v = byte_at(a) end
        local matched = record_has_expected(target)
        append(reads_path, table.concat({
            emu.framecount(),
            target.label,
            target.category,
            "ROM+0x" .. hex5(target.rom),
            "$" .. hex4(a),
            hex2(v),
            "$" .. hex4(target.start) .. "-$" .. hex4(target.stop),
            target.bytes,
            read_context(a),
            tostring(matched),
            read_record(target),
            compute_byte_diff(target),
        }, "\t"))
    end
end

local function register_read(addr, fn)
    if memory.registerread == nil then return false end
    local ok2 = pcall(function() memory.registerread(addr, fn) end)
    if ok2 then return true end
    ok2 = pcall(function() memory.registerread(addr, 1, fn) end)
    return ok2
end

-- 3-phase autoplay ------------------------------------------------------
-- Phase 1 (0-199):    게임 로드 대기 (no inputs)
-- Phase 2 (200-3000): START로 메뉴 진입 후 방향키 반복 탐색
--                     메뉴 항목 이동 패턴: 60프레임마다 down 10F → up 10F
--                     START 재입력(rel≈150)으로 서브메뉴 진입 시도
-- Phase 3 (3001-5000): START로 메뉴 닫기 → right+B 전진 → right+A+B 전투
local function get_phase(frame)
    if frame < 200   then return 1 end
    if frame <= 3000 then return 2 end
    return 3
end

local function joy_for_frame(frame)
    local phase = get_phase(frame)

    if phase == 1 then
        return {}

    elseif phase == 2 then
        local rel = frame - 200
        -- first START to enter main menu
        if rel < 15 then return { start = true } end
        -- second START to open sub-menu / confirm (rel≈150-164)
        if rel >= 150 and rel < 165 then return { start = true } end
        -- third START for deeper sub-menu (rel≈600-614)
        if rel >= 600 and rel < 615 then return { start = true } end
        -- direction navigation: cycle down(10f)/neutral(20f)/up(10f)/neutral(20f) per 60f
        if rel >= 220 then
            local nav = (rel - 220) % 60
            if nav < 10 then           return { down = true } end
            if nav >= 30 and nav < 40 then return { up   = true } end
        end

    else
        local rel = frame - 3001
        -- close menu
        if rel < 5  then return { start = true } end
        if rel < 10 then return {} end
        -- advance through stage
        if rel < 1500 then return { right = true, B = true } end
        return { right = true, A = true, B = true }
    end
    return {}
end

-- Setup -----------------------------------------------------------------
mkdir(OUT_DIR)
append(summary_path, "frame\treason\tregistered\thits\tdetail")
append(reads_path,   "frame\tlabel\tcategory\trom_hit\tcpu_addr\tvalue\trecord_cpu_range\texpected_bytes\tcontext\tactive_expected_match\trecord_snapshot\tbyte_diff")

for _, target in ipairs(targets) do
    for addr = target.start, target.stop do
        if register_read(addr, on_read_for(target)) then
            registered_count = registered_count + 1
            callback_mode = true
        end
    end
end

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

append(summary_path, table.concat({
    0, "lua_start", registered_count, 0,
    "callback_mode=" .. tostring(callback_mode) ..
    ";target_source=" .. target_source ..
    ";targets=" .. tostring(#targets),
}, "\t"))

print("=== AutoPlay Watch started ===")
print("targets=" .. #targets .. " (" .. target_source .. ")")
print("registered_cpu_addrs=" .. registered_count)
print("max_frames=" .. MAX_FRAMES)

-- Main loop -------------------------------------------------------------
while emu.framecount() < MAX_FRAMES and not stopped_for_limit and not stopped_for_stagnation do
    local frame = emu.framecount()
    current_phase = get_phase(frame)
    local phase = current_phase

    joypad.set(1, joy_for_frame(frame))
    gui.text(2, 8,  "AutoPlay Watch v3  frame=" .. tostring(frame) .. "  phase=" .. tostring(phase))
    gui.text(2, 17, "hits=" .. tostring(hit_count) .. "  p2=" .. tostring(phase2_hits) .. "  p3=" .. tostring(phase3_hits))
    emu.frameadvance()

    if frame % 300 == 0 then
        append(summary_path, table.concat({
            frame, "periodic", registered_count, hit_count, "phase=" .. tostring(phase),
        }, "\t"))
    end

    if STAGNATION_ABORT and frame >= STAGNATION_MIN_FRAMES and frame % 300 == 0 then
        local fingerprint = screen_fingerprint()
        if fingerprint == last_screen_fingerprint and hit_count == 0 then
            same_screen_samples = same_screen_samples + 1
        else
            same_screen_samples = 0
            last_screen_fingerprint = fingerprint
        end
        append(summary_path, table.concat({
            frame, "screen_fingerprint", registered_count, hit_count,
            "same_samples=" .. tostring(same_screen_samples) .. ";hash=" .. fingerprint,
        }, "\t"))
        if same_screen_samples >= STAGNATION_SAMPLES then
            stopped_for_stagnation = true
        end
    end
end

local final_reason = stopped_for_limit and "hit_limit" or (stopped_for_stagnation and "stagnant_screen" or "lua_done")
append(summary_path, table.concat({
    emu.framecount(), final_reason, registered_count, hit_count, "out=" .. OUT_DIR,
}, "\t"))

print("=== AutoPlay Watch done ===")
print("hits=" .. hit_count .. "  reason=" .. final_reason)

pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
