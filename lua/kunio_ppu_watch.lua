-- kunio_ppu_watch.lua
-- Captures PPU $2006/$2007 writes to track nametable text transfer.
--
--   Phase 1 (0-199):    load wait
--   Phase 2 (200-3000): START + menu navigation (primary capture window)
--   Phase 3 (3001-5000): stage advance
--
-- Output files (KUNIO_ANALYSIS_OUTPUT or rom_analysis/fceux_ppu_watch):
--   ppu_writes.tsv   -- every $2007 write to nametable range
--   summary.tsv      -- periodic status
--
-- Launch via run_fceux_lua_analysis.py:
--   python scripts/run_fceux_lua_analysis.py \
--     --lua-script lua/kunio_ppu_watch.lua \
--     --frames 3000 --timeout 120 \
--     --final-output rom_analysis/fceux_ppu_watch \
--     --clean-output --no-dump-hex --no-dump-bin

local OUT_DIR     = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/fceux_ppu_watch"
local MAX_FRAMES  = tonumber(os.getenv("KUNIO_MAX_FRAMES")   or "3000")
local WRITE_LIMIT = tonumber(os.getenv("KUNIO_WRITE_LIMIT")  or "200000")

local writes_path  = OUT_DIR .. "/ppu_writes.tsv"
local summary_path = OUT_DIR .. "/summary.tsv"

local write_count   = 0
local stopped_limit = false
local current_phase = 1

-- PPU state machine --------------------------------------------------
local addr_latch    = false   -- false=hi-byte pending, true=lo-byte pending
local vram_addr     = 0       -- 14-bit VRAM address
local vram_inc      = 1       -- 1 or 32 (PPUCTRL bit 2)

-- Helpers ------------------------------------------------------------
local function mkdir(path)
    os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end
local function hex2(v) return string.format("%02X", v % 0x100) end

local function append(path, line)
    local f = assert(io.open(path, "a"))
    f:write(line .. "\n")
    f:close()
end

-- Phase --------------------------------------------------------------
local function get_phase(frame)
    if frame < 200   then return 1 end
    if frame <= 3000 then return 2 end
    return 3
end

-- PPU register callbacks ---------------------------------------------
-- $2000 PPUCTRL: bit2 = VRAM increment (0→+1, 1→+32)
local function on_2000_write(addr, size, value)
    vram_inc = (math.floor(value / 4) % 2 == 1) and 32 or 1
end

-- $2002 PPUSTATUS read: resets address latch
local function on_2002_read(addr, size, value)
    addr_latch = false
end

-- $2005 PPUSCROLL write: also toggles the shared latch
local function on_2005_write(addr, size, value)
    addr_latch = not addr_latch
end

-- $2006 PPUADDR write: sets VRAM target address (two writes)
local function on_2006_write(addr, size, value)
    if not addr_latch then
        -- first write: high 6 bits → bits[13:8]
        vram_addr = (value % 0x40) * 0x100
        addr_latch = true
    else
        -- second write: low 8 bits → bits[7:0]
        vram_addr = vram_addr + (value % 0x100)
        addr_latch = false
    end
end

-- $2007 PPUDATA write: actual nametable/palette data
local function on_2007_write(addr, size, value)
    if stopped_limit then return end
    if write_count >= WRITE_LIMIT then stopped_limit = true; return end

    -- nametable range: $2000-$2FFF (masked to 14-bit)
    local masked = vram_addr % 0x4000
    if masked >= 0x2000 and masked < 0x3000 then
        write_count = write_count + 1
        local nt_offset = masked - 0x2000  -- 0x000..0xFFF
        -- nametable quadrant (0-3) and tile x,y
        local nt  = math.floor(nt_offset / 0x400)
        local off = nt_offset % 0x400
        local tile_row = math.floor(off / 32)
        local tile_col = off % 32
        append(writes_path, table.concat({
            emu.framecount(),
            string.format("$%04X", vram_addr % 0x4000),
            hex2(value),
            current_phase,
            nt,
            tile_row,
            tile_col,
        }, "\t"))
    end

    -- auto-increment VRAM address
    vram_addr = (vram_addr + vram_inc) % 0x4000
end

-- Autoplay joypad ----------------------------------------------------
local function joy_for_frame(frame)
    local phase = get_phase(frame)
    if phase == 1 then
        return {}
    elseif phase == 2 then
        local rel = frame - 200
        if rel < 15 then return { start = true } end
        if rel >= 150 and rel < 165 then return { start = true } end
        if rel >= 600 and rel < 615 then return { start = true } end
        if rel >= 220 then
            local nav = (rel - 220) % 60
            if nav < 10  then return { down = true } end
            if nav >= 30 and nav < 40 then return { up = true } end
        end
    else
        local rel = frame - 3001
        if rel < 5  then return { start = true } end
        if rel < 10 then return {} end
        if rel < 1500 then return { right = true, B = true } end
        return { right = true, A = true, B = true }
    end
    return {}
end

-- Setup --------------------------------------------------------------
mkdir(OUT_DIR)
append(summary_path, "frame\treason\twrites\tdetail")
append(writes_path, "frame\tvram_addr\tbyte\tphase\tnt\ttile_row\ttile_col")

-- Register PPU callbacks (pcall in case FCEUX version differs)
local ok = {}
ok["2000w"] = pcall(function() memory.registerwrite(0x2000, on_2000_write) end)
ok["2002r"] = pcall(function() memory.registerread (0x2002, on_2002_read ) end)
ok["2005w"] = pcall(function() memory.registerwrite(0x2005, on_2005_write) end)
ok["2006w"] = pcall(function() memory.registerwrite(0x2006, on_2006_write) end)
ok["2007w"] = pcall(function() memory.registerwrite(0x2007, on_2007_write) end)

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

local cb_status = ""
for k, v in pairs(ok) do cb_status = cb_status .. k .. "=" .. tostring(v) .. ";" end

append(summary_path, table.concat({ 0, "lua_start", 0, cb_status }, "\t"))
print("=== PPU Watch started ===")
print("max_frames=" .. MAX_FRAMES .. "  write_limit=" .. WRITE_LIMIT)
print("callbacks: " .. cb_status)

-- Main loop ----------------------------------------------------------
while emu.framecount() < MAX_FRAMES and not stopped_limit do
    local frame = emu.framecount()
    current_phase = get_phase(frame)

    joypad.set(1, joy_for_frame(frame))
    gui.text(2, 8,  "PPU Watch  frame=" .. frame .. "  phase=" .. current_phase)
    gui.text(2, 17, "nt_writes=" .. write_count)
    emu.frameadvance()

    if frame % 300 == 0 then
        append(summary_path, table.concat({
            frame, "periodic", write_count, "phase=" .. current_phase,
        }, "\t"))
    end
end

local final_reason = stopped_limit and "write_limit" or "lua_done"
append(summary_path, table.concat({
    emu.framecount(), final_reason, write_count, "out=" .. OUT_DIR,
}, "\t"))

print("=== PPU Watch done ===")
print("nt_writes=" .. write_count .. "  reason=" .. final_reason)
pcall(function() FCEU.pause() end)
pcall(function() emu.pause() end)
