-- Task 3: one-shot mapper-aware source trace. Static leads remain unproven until a qualified source hit.
local frame = 0
local selected = nil
local prg_mode = nil
local regs = {}
local source_observations = 0
local qualified_source_hits = 0
local target_hits = 0
local mapper_values = 0
local held = {start=false, a=false}

local function hex(value, width)
  return string.format("%0" .. width .. "X", value)
end

local function bank(reg)
  return regs[reg] and ("$" .. hex(regs[reg], 2)) or "unknown"
end

local function mapper_write(address, value)
  if address == 0x8000 then
    selected = value % 8
    prg_mode = math.floor(value / 64) % 2
    print("MMC3_SELECT frame=" .. frame .. " raw=$" .. hex(value, 2) .. " reg=" .. selected .. " prg_mode=" .. prg_mode)
  elseif address == 0x8001 then
    mapper_values = mapper_values + 1
    if selected == nil then
      print("MMC3_VALUE_WITHOUT_SELECT frame=" .. frame .. " raw=$" .. hex(value, 2))
    else
      regs[selected] = value
      print("MMC3_VALUE frame=" .. frame .. " reg=" .. selected .. " value=$" .. hex(value, 2))
    end
  end
end

local function source_exec(address, value)
  source_observations = source_observations + 1
  local mode = prg_mode == nil and "unknown" or tostring(prg_mode)
  local r6 = bank(6)
  local r7 = bank(7)
  local physical_bank13 = (address == 0xB23C and regs[7] == 13) or
                          (address == 0xC23C and prg_mode == 1 and regs[6] == 13)
  print("SOURCE_SITE_EXEC frame=" .. frame .. " cpu=$" .. hex(address, 4) ..
        " observed=" .. source_observations .. " prg_mode=" .. mode ..
        " reg6=" .. r6 .. " reg7=" .. r7 ..
        " physical_raw_1B24C=" .. tostring(physical_bank13))
  if physical_bank13 then
    qualified_source_hits = qualified_source_hits + 1
    local target_bank = r7
    print("SOURCE_PHYS13_EXEC frame=" .. frame .. " cpu=$" .. hex(address, 4) ..
          " prg_mode=" .. mode .. " reg6=" .. r6 .. " reg7=" .. r7 ..
          " B295_physical_bank=" .. target_bank)
    emu.stop(0)
  end
end

local function target_exec(address, value)
  target_hits = target_hits + 1
  print("B295_EXEC frame=" .. frame .. " hit=" .. target_hits ..
        " prg_mode=" .. (prg_mode == nil and "unknown" or tostring(prg_mode)) ..
        " reg6=" .. bank(6) .. " reg7=" .. bank(7))
end

emu.addMemoryCallback(mapper_write, emu.callbackType.write, 0x8000, 0x8001)
emu.addMemoryCallback(source_exec, emu.callbackType.exec, 0xB23C, 0xB23C)
emu.addMemoryCallback(source_exec, emu.callbackType.exec, 0xC23C, 0xC23C)
emu.addMemoryCallback(target_exec, emu.callbackType.exec, 0xB295, 0xB295)

emu.addEventCallback(function()
  emu.setInput(held, 0, 0)
end, emu.eventType.inputPolled)

local function tap(button, start_frame)
  if frame == start_frame then
    held[button] = true
    print("INPUT_" .. string.upper(button) .. "_DOWN frame=" .. frame)
  elseif frame == start_frame + 5 then
    held[button] = false
    print("INPUT_" .. string.upper(button) .. "_UP frame=" .. frame)
  end
end

emu.addEventCallback(function()
  frame = frame + 1
  tap("start", 90)
  -- Single-pass confirmations: distinct intervals, no reset/replay loop.
  tap("a", 330)
  tap("a", 510)
  tap("a", 690)
  tap("a", 900)
  tap("a", 1140)
  tap("a", 1380)
  tap("a", 1680)
  tap("a", 2040)
  tap("a", 2460)
  tap("a", 2940)
  tap("a", 3420)
  if frame >= 3600 then
    print("TASK3_PROBE_END frame=" .. frame .. " source_observations=" .. source_observations ..
          " qualified_source_hits=" .. qualified_source_hits .. " target_hits=" .. target_hits ..
          " mapper_values=" .. mapper_values)
    emu.stop(0)
  end
end, emu.eventType.endFrame)

print("TASK3_SOURCE_MAPPER_PROBE_START")
