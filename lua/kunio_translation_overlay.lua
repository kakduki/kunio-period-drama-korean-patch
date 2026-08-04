-- Bounded FCEUX event emitter for the real-time translation overlay MVP.
--
-- This is intentionally target-driven. It emits an event only when a known,
-- previously verified source record is read. It does not attempt blind
-- gameplay or infer text from arbitrary bytes.

local OUT_DIR = os.getenv("KUNIO_OVERLAY_OUTPUT") or "rom_analysis/realtime_overlay"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1200")
local COOLDOWN = tonumber(os.getenv("KUNIO_OVERLAY_COOLDOWN") or "90")
local TARGETS_LUA = os.getenv("KUNIO_OVERLAY_TARGETS_LUA") or "kunio_translation_overlay_targets.lua"
local DRIVE_ROUTE = os.getenv("KUNIO_OVERLAY_DRIVE") ~= "0"

local events_path = OUT_DIR .. "/events.tsv"
local summary_path = OUT_DIR .. "/summary.tsv"
local targets = {}
local registered = 0
local hits = 0
local last_event_frame = {}

local function mkdir(path)
  os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function hex2(value)
  return string.format("%02X", (value or 0) % 0x100)
end

local function append(path, line)
  local file = assert(io.open(path, "a"))
  file:write(line .. "\n")
  file:close()
end

local function byte_at(address)
  local ok, value = pcall(function() return memory.readbyte(address) end)
  if ok and value ~= nil then
    return value
  end
  return 0
end

local function split_bytes(value)
  local result = {}
  for token in string.gmatch(value or "", "%S+") do
    result[#result + 1] = tonumber(token, 16) or -1
  end
  return result
end

local function record_bytes(target)
  local result = {}
  for address = target.start, target.stop do
    result[#result + 1] = byte_at(address)
  end
  return result
end

local function contains_expected(target)
  local expected = split_bytes(target.old_bytes)
  local record = record_bytes(target)
  if #expected == 0 or #record < #expected then
    return false
  end
  for start_index = 1, #record - #expected + 1 do
    local matched = true
    for offset = 1, #expected do
      if record[start_index + offset - 1] ~= expected[offset] then
        matched = false
        break
      end
    end
    if matched then
      return true
    end
  end
  return false
end

local function record_hex(target)
  local bytes = record_bytes(target)
  local result = {}
  for index = 1, #bytes do
    result[index] = hex2(bytes[index])
  end
  return table.concat(result, " ")
end

local function emit(target)
  local frame = emu.framecount()
  local previous = last_event_frame[target.id] or -1000000
  if frame - previous < COOLDOWN then
    return
  end
  last_event_frame[target.id] = frame
  hits = hits + 1
  append(events_path, table.concat({
    "text",
    frame,
    target.id,
    target.category or "unknown",
    target.context or "unknown",
    target.old_bytes or "",
    record_hex(target),
  }, "\t"))
end

local function on_read(target)
  return function()
    if contains_expected(target) then
      emit(target)
    end
  end
end

local function register_read(address, callback)
  if memory.registerread == nil then
    return false
  end
  local ok = pcall(function() memory.registerread(address, callback) end)
  if ok then
    return true
  end
  return pcall(function() memory.registerread(address, 1, callback) end)
end

local ok_targets, loaded_targets = pcall(function() return dofile(TARGETS_LUA) end)
if ok_targets and type(loaded_targets) == "table" then
  targets = loaded_targets
end

mkdir(OUT_DIR)
append(events_path, "event\tframe\tid\tcategory\tcontext\texpected_bytes\trecord_snapshot")
append(summary_path, "frame\treason\tregistered\thits\ttargets")

for _, target in ipairs(targets) do
  for address = target.start, target.stop do
    if register_read(address, on_read(target)) then
      registered = registered + 1
    end
  end
end

append(summary_path, table.concat({0, "lua_start", registered, 0, #targets}, "\t"))
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

local function joy_for_frame(frame)
  if not DRIVE_ROUTE then
    return {}
  elseif frame < 90 then
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

while emu.framecount() < MAX_FRAMES do
  local frame = emu.framecount()
  joypad.set(1, joy_for_frame(frame))
  gui.text(2, 8, "Kunio overlay emitter " .. tostring(frame))
  gui.text(2, 17, "events: " .. tostring(hits))
  emu.frameadvance()
end

append(summary_path, table.concat({emu.framecount(), "lua_done", registered, hits, #targets}, "\t"))
pcall(function() FCEU.pause() end)
