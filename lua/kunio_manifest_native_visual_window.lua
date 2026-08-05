-- Capture a short post-read window for each manifest target.
-- This distinguishes a CPU-side string read from a string that reaches the dialogue renderer.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/manifest_native_visual_window"
local TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or ""
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "5000")
local DELAYS = {0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160}

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line) local f=assert(io.open(path,"a")); f:write(line.."\n"); f:close() end
local function byte_at(addr, domain)
  local ok,v=pcall(function() return memory.readbyte(addr,domain) end)
  if ok and v ~= nil then return v end
  ok,v=pcall(function() return memory.readbyte(addr) end)
  return ok and v or 0
end
local function parse_bytes(text)
  local out={}; for token in string.gmatch(text or "","%x%x") do out[#out+1]=tonumber(token,16) end; return out
end
local function matches(target)
  local expected=parse_bytes(target.bytes)
  if #expected ~= target.stop-target.start+1 then return false end
  for i,v in ipairs(expected) do if byte_at(target.start+i-1) ~= v then return false end end
  return true
end
local function dump_range(path,start_addr,length,domain)
  local f=assert(io.open(path,"wb")); for i=0,length-1 do f:write(string.char(byte_at(start_addr+i,domain))) end; f:close()
end
local function fingerprint()
  local h=0; local s=0
  for addr=0x2000,0x23BF,4 do local v=byte_at(addr,"ppu"); h=(h*131+v+addr)%1000000007; s=(s+v)%65536 end
  return tostring(h)..":"..tostring(s)
end
local targets={}
if TARGETS_LUA ~= "" then local ok,v=pcall(dofile,TARGETS_LUA); if ok and type(v)=="table" then targets=v end end
local seen={}; local armed={}; local seen_count=0; local pending={}; local read_counts={}
mkdir(OUT_DIR)
local summary=OUT_DIR.."/summary.tsv"
append(summary,"frame\tindex\tlabel\tdelay\tread_match\tcaptured\tfingerprint\tread_count\tscreenshot\tnametable")
local function capture(index,delay,frame)
  local target=targets[index]; local stem=string.format("%s/manifest_ptr_%03d_delay_%02d_frame_%06d",OUT_DIR,index,delay,frame)
  local ok,shot=pcall(function() return gui.gdscreenshot() end); local shot_path=""
  if ok and shot ~= nil then shot_path=stem.."_screen.gd"; local f=assert(io.open(shot_path,"wb")); f:write(shot); f:close() end
  local nt=stem.."_nametable_2000_2fff.bin"; dump_range(nt,0x2000,0x1000,"ppu")
  append(summary,table.concat({frame,index,target.label or ("pointer_"..index),delay,tostring(matches(target)),tostring(shot_path~=""),fingerprint(),tostring(read_counts[index] or 0),shot_path,nt},"\t"))
end
local function route_input(frame)
  if frame>=40 and frame<50 then return {start=true} end
  if frame>=130 and frame<140 then return {A=true} end
  if frame>=220 and frame<230 then return {start=true} end
  if frame>=300 and frame<310 then return {down=true} end
  if frame>=360 and frame<370 then return {A=true} end
  if frame>=480 and frame<490 then return {down=true} end
  if frame>=540 and frame<550 then return {A=true} end
  if frame>=700 and frame<712 then return {B=true} end
  if frame>=900 and frame<910 then return {B=true} end
  if frame>=1110 and frame<1120 then return {B=true} end
  if frame>=1520 and frame<1530 then return {B=true} end
  return {}
end
for index,target in ipairs(targets) do
  read_counts[index]=0
  for addr=target.start,target.stop do
    memory.registerread(addr,function()
      read_counts[index]=(read_counts[index] or 0)+1
      -- Ignore an initial coincidental match before the loader has read the span.
      if not seen[index] and not armed[index] and read_counts[index] >= (target.stop-target.start+1) and matches(target) then
        armed[index]=true; pending[index]={next=1,base=emu.framecount()}
      end
    end)
  end
end
pcall(function() FCEU.speedmode("turbo") end); pcall(function() emu.speedmode("turbo") end)
while emu.framecount()<MAX_FRAMES and seen_count<#targets do
  local frame=emu.framecount(); joypad.set(1,route_input(frame)); emu.frameadvance()
  for index,state in pairs(pending) do
    local delay=DELAYS[state.next]
    if delay and emu.framecount() >= state.base+delay then
      capture(index,delay,emu.framecount()); state.next=state.next+1
      if state.next>#DELAYS then pending[index]=nil; seen[index]=true; seen_count=seen_count+1 end
    end
  end
  gui.text(2,8,"Manifest native visual window"); gui.text(2,17,"frame="..tostring(frame))
end
append(summary,table.concat({emu.framecount(),"DONE","","","",tostring(seen_count==#targets),fingerprint(),"","",""},"\t"))
print("KUNIO_NATIVE_VISUAL_WINDOW_DONE"); pcall(function() FCEU.pause() end); pcall(function() emu.pause() end)
