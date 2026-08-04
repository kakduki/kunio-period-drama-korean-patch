-- Bounded Map CRSR source-read probe.
--
-- EN-PRE-167 is a pre-pointer record with control byte 0x38. This probe only
-- observes its Bank 1 CPU window and never writes state or ROM data.

local function script_dir()
  local source = debug.getinfo(1, "S").source or ""
  if string.sub(source, 1, 1) == "@" then source = string.sub(source, 2) end
  return string.match(source, "^(.*)[/\\][^/\\]+$") or "."
end

local LUA_DIR = script_dir()
local ROOT_DIR = string.match(LUA_DIR, "^(.*)[/\\]lua$") or "."
local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or (ROOT_DIR .. "/rom_analysis/map_crsr_source_probe")
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "3600")
local ADVANCE_AFTER_COMBAT = os.getenv("KUNIO_ADVANCE_AFTER_COMBAT") == "1"
local MAP_SOURCE_ROUTE = os.getenv("KUNIO_MAP_SOURCE_ROUTE") == "1"
local MAP_DIRECTION = os.getenv("KUNIO_MAP_DIRECTION") or "right"
local SOURCE_START = 0x9C59
local SOURCE_END = 0x9C61
local EXPECTED = { 0x8D, 0x81, 0x90, 0x38, 0x83, 0x92, 0x93, 0x92, 0xFF }

local reads = 0
local registered = 0
local last_fingerprint = ""
local unique_screens = 0
local seen_fingerprints = {}

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line)
  local file = assert(io.open(path, "a"))
  file:write(line .. "\n")
  file:close()
end
local function hex2(value) return string.format("%02X", (value or 0) % 0x100) end
local function hex4(value) return string.format("%04X", (value or 0) % 0x10000) end
local function byte_at(address, domain)
  local ok, value
  if domain ~= nil then
    ok, value = pcall(function() return memory.readbyte(address, domain) end)
    if ok and value ~= nil then return value end
  end
  ok, value = pcall(function() return memory.readbyte(address) end)
  return ok and value or 0
end
local function read_pc()
  local ok, value = pcall(function() return memory.getregister("pc") end)
  return ok and value or 0
end
local function fingerprint()
  local hash, sum = 0, 0
  for address = 0x2000, 0x23BF, 8 do
    local value = byte_at(address, "ppu")
    hash = (hash * 131 + value + address) % 1000000007
    sum = (sum + value) % 65536
  end
  return tostring(hash) .. ":" .. tostring(sum)
end
local function expected_present()
  for index, value in ipairs(EXPECTED) do
    if byte_at(SOURCE_START + index - 1) ~= value then return false end
  end
  return true
end
local function record_snapshot()
  local values = {}
  for address = SOURCE_START, SOURCE_END do values[#values + 1] = hex2(byte_at(address)) end
  return table.concat(values, " ")
end
local function register_read(address, callback)
  if memory.registerread == nil then return false end
  local ok = pcall(function() memory.registerread(address, callback) end)
  if ok then return true end
  return pcall(function() memory.registerread(address, 1, callback) end)
end
local function map_input(frame)
  local cycle = frame % 192
  local direction = {}
  if MAP_DIRECTION == "left" then direction.left = true
  elseif MAP_DIRECTION == "up" then direction.up = true
  elseif MAP_DIRECTION == "down" then direction.down = true
  else direction.right = true end
  if cycle < 8 then return { start = true } end
  if cycle < 24 then return { B = true } end
  if cycle < 96 then direction.A = true; return direction end
  if cycle < 168 then direction.B = true; return direction end
  return {}
end
local function entry_input(frame)
  if frame >= 40 and frame < 50 then return { start = true } end
  if frame >= 130 and frame < 140 then return { A = true } end
  if frame >= 220 and frame < 230 then return { start = true } end
  if frame >= 300 and frame < 310 then return { down = true } end
  if frame >= 360 and frame < 370 then return { A = true } end
  if frame >= 480 and frame < 490 then return { down = true } end
  if frame >= 540 and frame < 550 then return { A = true } end
  if frame >= 700 and frame < 712 then return { B = true } end
  return {}
end
local function combat_input(frame)
  if ADVANCE_AFTER_COMBAT and (byte_at(0x04F1) == 0x06 or byte_at(0x04F1) == 0x12) and MAP_SOURCE_ROUTE then
    return map_input(frame)
  end
  local cycle = (frame - 900) % 240
  if cycle < 72 then return { right = true, A = true, B = true } end
  if cycle < 96 then return { right = true, B = true } end
  if cycle < 144 then return { left = true, A = true, B = true } end
  if cycle < 168 then return { left = true, A = true } end
  if cycle < 216 then return { right = true, A = true } end
  return { up = true, A = true, B = true }
end

mkdir(OUT_DIR)
local summary_path = OUT_DIR .. "/summary.tsv"
local reads_path = OUT_DIR .. "/source_reads.tsv"
local screens_path = OUT_DIR .. "/screens.tsv"
append(summary_path, "frame\treason\tregistered\treads\tunique_screens\tlast_fingerprint\tmap_route\tdirection")
append(reads_path, "frame\tcpu_addr\tvalue\tpc\t04F1\t04FA\t04FB\t04FC\tmap_route\tdirection\tpresent\trecord_snapshot")
append(screens_path, "frame\tfingerprint\t04F1\t04FA\t04FB\t04FC\tmap_route\tdirection")

local function on_source_read(addr, size, value)
  reads = reads + 1
  append(reads_path, table.concat({
    emu.framecount(), "$" .. hex4(addr or 0), hex2(value), "$" .. hex4(read_pc()),
    hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)),
    tostring(MAP_SOURCE_ROUTE), MAP_DIRECTION, tostring(expected_present()), record_snapshot()
  }, "\t"))
end

for address = SOURCE_START, SOURCE_END do
  if register_read(address, on_source_read) then registered = registered + 1 end
end
append(summary_path, table.concat({0, "lua_start", registered, 0, 0, "", tostring(MAP_SOURCE_ROUTE), MAP_DIRECTION}, "\t"))
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

while emu.framecount() < MAX_FRAMES do
  local frame = emu.framecount()
  joypad.set(1, frame < 900 and entry_input(frame) or combat_input(frame))
  local current = fingerprint()
  if current ~= last_fingerprint then
    last_fingerprint = current
    if not seen_fingerprints[current] then
      seen_fingerprints[current] = true
      unique_screens = unique_screens + 1
      append(screens_path, table.concat({
        frame, current, hex2(byte_at(0x04F1)), hex2(byte_at(0x04FA)), hex2(byte_at(0x04FB)), hex2(byte_at(0x04FC)),
        tostring(MAP_SOURCE_ROUTE), MAP_DIRECTION
      }, "\t"))
    end
  end
  gui.text(2, 8, "Map CRSR source probe " .. tostring(frame))
  gui.text(2, 17, "reads=" .. tostring(reads) .. " screens=" .. tostring(unique_screens))
  emu.frameadvance()
end

append(summary_path, table.concat({emu.framecount(), "lua_done", registered, reads, unique_screens, last_fingerprint, tostring(MAP_SOURCE_ROUTE), MAP_DIRECTION}, "\t"))
pcall(function() FCEU.pause() end)
