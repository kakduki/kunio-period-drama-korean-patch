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
local trace_path=OUT_DIR.."/overlap_exec_trace.tsv"
local trace_count=0
append(trace_path,"frame	label	pc	a	x	y	0430	0431	0432	0433	0434	0435	0436	0437	04F1	04FA	04FB	04FC	0706	7A00	7A01	7A02	0049X	0050X	0057X	0496X	04ACX	04B4X")
local function trace_exec(label)
  if trace_count>=12000 then return end
  trace_count=trace_count+1
  local function reg(a)
    local ok,v=pcall(function() return memory.getregister(a) end)
    return ok and v or 0
  end
  local x=reg("x")
  append(trace_path,table.concat({emu.framecount(),label,string.format("%04X",reg("pc")),string.format("%02X",reg("a")),string.format("%02X",reg("x")),string.format("%02X",reg("y")),string.format("%02X",byte_at(0x0430)),string.format("%02X",byte_at(0x0431)),string.format("%02X",byte_at(0x0432)),string.format("%02X",byte_at(0x0433)),string.format("%02X",byte_at(0x0434)),string.format("%02X",byte_at(0x0435)),string.format("%02X",byte_at(0x0436)),string.format("%02X",byte_at(0x0437)),string.format("%02X",byte_at(0x04F1)),string.format("%02X",byte_at(0x04FA)),string.format("%02X",byte_at(0x04FB)),string.format("%02X",byte_at(0x04FC)),string.format("%02X",byte_at(0x0706)),string.format("%02X",byte_at(0x7A00)),string.format("%02X",byte_at(0x7A01)),string.format("%02X",byte_at(0x7A02)),string.format("%02X",byte_at(0x0049+x)),string.format("%02X",byte_at(0x0050+x)),string.format("%02X",byte_at(0x0057+x)),string.format("%02X",byte_at(0x0496+x)),string.format("%02X",byte_at(0x04AC+x)),string.format("%02X",byte_at(0x04B4+x))},"	"))
end

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
exec(0x8D02,function() trace_exec("8D02") end)
exec(0x8D05,function() trace_exec("8D05") end)
exec(0x8D31,function() trace_exec("8D31") end)
exec(0x8D34,function() trace_exec("8D34") end)
exec(0x8D60,function() trace_exec("8D60") end)
exec(0x8D63,function() trace_exec("8D63") end)
exec(0xAA87,function() trace_exec("AA87") end)
exec(0xAA8C,function() trace_exec("AA8C") end)
exec(0xAA8E,function() trace_exec("AA8E") end)
exec(0xFC65,function() trace_exec("FC65") end)
exec(0xFC6B,function() trace_exec("FC6B") end)
exec(0xFC8F,function() trace_exec("FC8F") end)
exec(0xFC9E,function() trace_exec("FC9E") end)
exec(0xFD28,function() trace_exec("FD28") end)
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
