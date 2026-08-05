-- Targeted overlap probe: reach the known combat screen, then hold a
-- directional attack long enough to test collision and slot-clear dispatch.
local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/target_overlap_probe"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "3600")
local function mkdir(p) os.execute('mkdir "' .. p .. '" >NUL 2>NUL') end
local function append(p, line)
  local f=assert(io.open(p,"a")); f:write(line); f:write(string.char(10)); f:close()
end
local function byte_at(a)
  local ok,v=pcall(function() return memory.readbyte(a) end)
  return ok and v or 0
end
local function fp()
  local h,s=0,0
  for a=0x2000,0x23BF,8 do local v=memory.readbyte(a,"ppu"); h=(h*131+v+a)%1000000007; s=(s+v)%65536 end
  return tostring(h)..":"..tostring(s)
end
local function entry(frame)
  if frame < 40 then return {} end
  if frame < 50 then return {start=true} end
  if frame >= 130 and frame < 140 then return {A=true} end
  if frame >= 220 and frame < 230 then return {start=true} end
  if frame >= 300 and frame < 310 then return {down=true} end
  if frame >= 360 and frame < 370 then return {A=true} end
  if frame >= 480 and frame < 490 then return {down=true} end
  if frame >= 540 and frame < 550 then return {A=true} end
  if frame >= 650 and frame < 665 then return {start=true} end
  if frame >= 700 and frame < 712 then return {B=true} end
  return {}
end
local function input(frame)
  if frame < 900 then return entry(frame) end
  local rel=frame-900
  if rel < 1200 then return {right=true,A=true,B=true} end
  if rel < 1800 then return {left=true,A=true,B=true} end
  if rel < 2400 then return {right=true,A=true,B=true} end
  return {up=true,A=true,B=true}
end
mkdir(OUT_DIR)
local sum=OUT_DIR.."/summary.tsv"
local cap=OUT_DIR.."/captures.tsv"
append(sum,"frame	reason	fingerprint	fad9	fc82	fcef	04f1	04fa	04fb	04fc")
append(cap,"frame	reason	fingerprint	screenshot")
local fad9,fc82,fcef=0,0,0
local last=""
local function capture(frame,reason)
  local stem=string.format("%s/frame_%06d",OUT_DIR,frame)
  local ok,shot=pcall(function() return gui.gdscreenshot() end)
  if ok and shot then local f=assert(io.open(stem.."_screen.gd","wb")); f:write(shot); f:close() end
  local f=assert(io.open(stem.."_nametable.bin","wb"))
  for a=0x2000,0x23FF do f:write(string.char(memory.readbyte(a,"ppu"))) end
  f:close()
  append(cap,table.concat({frame,reason,fp(),tostring(ok and shot~=nil),tostring(ok and shot~=nil)},"	"))
end
local function exec(addr,fn)
  if memory.registerexec then
    local ok=pcall(function() memory.registerexec(addr,fn) end)
    if ok then return true end
  end
  if memory.registerexecute then return pcall(function() memory.registerexecute(addr,fn) end) end
  return false
end
exec(0xFAD9,function() fad9=fad9+1; append(sum,table.concat({emu.framecount(),"FAD9",fp(),fad9,fc82,fcef,byte_at(0x04F1),byte_at(0x04FA),byte_at(0x04FB),byte_at(0x04FC)},"	")); capture(emu.framecount(),"collision_dispatch") end)
exec(0xFC82,function() fc82=fc82+1; append(sum,table.concat({emu.framecount(),"FC82",fp(),fad9,fc82,fcef,byte_at(0x04F1),byte_at(0x04FA),byte_at(0x04FB),byte_at(0x04FC)},"	")) end)
exec(0xFCEF,function() fcef=fcef+1; append(sum,table.concat({emu.framecount(),"FCEF",fp(),fad9,fc82,fcef,byte_at(0x04F1),byte_at(0x04FA),byte_at(0x04FB),byte_at(0x04FC)},"	")) end)
pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)
append(sum,table.concat({0,"lua_start",fp(),fad9,fc82,fcef,byte_at(0x04F1),byte_at(0x04FA),byte_at(0x04FB),byte_at(0x04FC)},"	"))
while emu.framecount()<MAX_FRAMES do
  local frame=emu.framecount(); local buttons=input(frame); joypad.set(1,buttons); emu.frameadvance()
  local current=fp()
  if current~=last and frame>=900 then last=current; capture(frame,"screen_change") end
  gui.text(2,8,"target overlap probe frame="..frame)
  gui.text(2,17,"FAD9="..fad9.." FC82="..fc82.." FCEF="..fcef)
end
append(sum,table.concat({emu.framecount(),"lua_done",fp(),fad9,fc82,fcef,byte_at(0x04F1),byte_at(0x04FA),byte_at(0x04FB),byte_at(0x04FC)},"	"))
pcall(function() FCEU.pause() end); pcall(function() emu.pause() end)