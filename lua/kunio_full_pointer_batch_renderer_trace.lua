-- Trace PPU dialogue-band writes for the next bounded full-pointer batch.
-- This separates source-record reads from actual nametable renderer activity.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/manifest_renderer_context"
local TARGETS_LUA = os.getenv("KUNIO_TARGETS_LUA") or ""
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "5000")
local WINDOW = tonumber(os.getenv("KUNIO_RENDER_WINDOW") or "160")
local WRITE_LIMIT = tonumber(os.getenv("KUNIO_WRITE_LIMIT") or "200000")

local function mkdir(path) os.execute('mkdir "' .. path .. '" >NUL 2>NUL') end
local function append(path, line) local f=assert(io.open(path,"a")); f:write(line.."\n"); f:close() end
local function byte_at(addr, domain)
  local ok,v=pcall(function() return memory.readbyte(addr,domain) end)
  if ok and v ~= nil then return v end
  ok,v=pcall(function() return memory.readbyte(addr) end)
  return ok and v or 0
end
local function hex2(v) return string.format("%02X",(v or 0)%256) end
local function hex4(v) return string.format("%04X",(v or 0)%65536) end
local function parse_bytes(text)
  local out={}; for token in string.gmatch(text or "","%x%x") do out[#out+1]=tonumber(token,16) end; return out
end
local function matches(target)
  local expected=parse_bytes(target.bytes)
  if #expected ~= target.stop-target.start+1 then return false end
  for i,v in ipairs(expected) do if byte_at(target.start+i-1) ~= v then return false end end
  return true
end
local function register_read(addr, callback)
  local ok=pcall(function() memory.registerread(addr,callback) end)
  if ok then return true end
  return pcall(function() memory.registerread(addr,1,callback) end)
end
local function register_write(addr, callback)
  local ok=pcall(function() memory.registerwrite(addr,callback) end)
  if ok then return true end
  return pcall(function() memory.registerwrite(addr,1,callback) end)
end

local targets={}
if TARGETS_LUA ~= "" then local ok,v=pcall(dofile,TARGETS_LUA); if ok and type(v)=="table" then targets=v end end
local OUT=OUT_DIR; mkdir(OUT)
local summary=OUT.."/summary.tsv"; local writes=OUT.."/ppu_writes.tsv"; local dma=OUT.."/oam_dma.tsv"
append(summary,"frame\ttarget\tevent\twindow_writes\tdialogue_band_writes\tfirst_vram\tlast_vram")
append(writes,"frame\ttarget\tvram_addr\tbyte\trow\tcol")
append(dma,"frame\ttarget\tpage")

local latch=false; local vram=0; local inc=1; local active=nil; local active_until=-1
local counts={}; local band_counts={}; local first_addr={}; local last_addr={}; local write_count=0
local seen={}; local armed={}; local read_counts={}
local function target_name(index) return targets[index].label or ("pointer_"..index) end
local function ppu_2000(_,_,value) inc=(math.floor(value/4)%2==1) and 32 or 1 end
local function ppu_2002() latch=false end
local function ppu_2005() latch=not latch end
local function ppu_2006(_,_,value)
  if not latch then vram=(value%0x40)*0x100; latch=true else vram=vram+(value%0x100); latch=false end
end
local function ppu_2007(_,_,value)
  local frame=emu.framecount(); local masked=vram%0x4000
  if active and frame<=active_until and write_count<WRITE_LIMIT and masked>=0x2000 and masked<0x3000 then
    local row=math.floor(((masked-0x2000)%0x400)/32); local col=(masked-0x2000)%32
    counts[active]=(counts[active] or 0)+1; write_count=write_count+1
    first_addr[active]=first_addr[active] or masked; last_addr[active]=masked
    if row>=24 and row<=28 then band_counts[active]=(band_counts[active] or 0)+1 end
    append(writes,table.concat({frame,target_name(active),"$"..hex4(masked),hex2(value),row,col},"\t"))
  end
  vram=(vram+inc)%0x4000
end
local function on_dma(_,_,value)
  if active and emu.framecount()<=active_until then append(dma,table.concat({emu.framecount(),target_name(active),hex2(value)},"\t")) end
end
pcall(function() memory.registerwrite(0x2000,ppu_2000) end)
pcall(function() memory.registerread(0x2002,ppu_2002) end)
pcall(function() memory.registerwrite(0x2005,ppu_2005) end)
pcall(function() memory.registerwrite(0x2006,ppu_2006) end)
pcall(function() memory.registerwrite(0x2007,ppu_2007) end)
pcall(function() memory.registerwrite(0x4014,on_dma) end)
for index,target in ipairs(targets) do
  read_counts[index]=0
  for addr=target.start,target.stop do
    register_read(addr,function()
      read_counts[index]=(read_counts[index] or 0)+1
      if not armed[index] and not active and read_counts[index] == 1 then
        armed[index]=true; active=index; active_until=emu.framecount()+WINDOW+((target.stop-target.start+1)*2); counts[index]=0; band_counts[index]=0
        append(summary,table.concat({emu.framecount(),target_name(index),"first_read",0,0,"",""},"\t"))
      end
      if not seen[index] and read_counts[index] >= (target.stop-target.start+1) and matches(target) then
        seen[index]=true
        append(summary,table.concat({emu.framecount(),target_name(index),"complete_read",counts[index] or 0,band_counts[index] or 0,"",""},"\t"))
      end
    end)
  end
end
local function route_input(frame)
  if frame>=40 and frame<50 then return {start=true} end
  if frame>=130 and frame<140 then return {A=true} end
  if frame>=220 and frame<230 then return {start=true} end
  if frame>=300 and frame<310 then return {down=true} end
  if frame>=360 and frame<370 then return {A=true} end
  if frame>=480 and frame<490 then return {down=true} end
  if frame>=540 and frame<550 then return {A=true} end
  -- Opening dialogue dismissal. Keep each press bounded and observable.
  local presses = {700, 900, 1110, 1520, 1800, 2080, 2360, 2640, 2920, 3200, 3480, 3760, 4040, 4320, 4600, 4880, 5160, 5440, 5720}
  for _, start_frame in ipairs(presses) do
    if frame>=start_frame and frame<start_frame+10 then return {B=true} end
  end
  -- During the stage route, keep Kunio moving and attack periodically.
  if frame>=1700 and frame<5800 then
    local phase = (frame-1700) % 180
    if phase < 70 then return {right=true, B=true} end
    if phase < 100 then return {left=true, B=true} end
    if phase < 125 then return {A=true, B=true} end
  end
  return {}
end
while emu.framecount()<MAX_FRAMES do
  local frame=emu.framecount(); joypad.set(1,route_input(frame)); emu.frameadvance()
  if active and emu.framecount()>active_until then
    append(summary,table.concat({emu.framecount(),target_name(active),"window_done",counts[active] or 0,band_counts[active] or 0,first_addr[active] and ("$"..hex4(first_addr[active])) or "",last_addr[active] and ("$"..hex4(last_addr[active])) or ""},"\t"))
    active=nil
  end
end
append(summary,table.concat({emu.framecount(),"DONE","",write_count,"","",""},"\t"))
print("KUNIO_MANIFEST_RENDERER_CONTEXT_DONE"); pcall(function() FCEU.pause() end); pcall(function() emu.pause() end)
