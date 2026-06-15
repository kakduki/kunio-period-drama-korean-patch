-- Kunio period drama runtime analysis helper for FCEUX.
--
-- Load the ROM first, then run this script from FCEUX's Lua window.
-- It drives the title/menu flow, watches PPU register activity when supported,
-- and writes frame-indexed memory dumps for later text/font analysis.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/fceux_lua"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "7200")
local SNAPSHOT_EVERY = tonumber(os.getenv("KUNIO_SNAPSHOT_EVERY") or "300")
local BURST_THRESHOLD = tonumber(os.getenv("KUNIO_PPU_BURST_THRESHOLD") or "24")

local summary_path = OUT_DIR .. "/summary.tsv"
local events_path = OUT_DIR .. "/events.tsv"

local ppu_writes_this_frame = 0
local ppu_addr_hi = nil
local ppu_addr = 0
local last_dump_frame = -999999
local dump_count = 0
local callback_mode = false

local function mkdir(path)
	os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function hex2(v)
	return string.format("%02X", v % 0x100)
end

local function hex4(v)
	return string.format("%04X", v % 0x10000)
end

local function byte_at(addr, domain)
	if domain ~= nil then
		local ok, value = pcall(function() return memory.readbyte(addr, domain) end)
		if ok and value ~= nil then
			return value
		end
	end
	local ok, value = pcall(function() return memory.readbyte(addr) end)
	if ok and value ~= nil then
		return value
	end
	return 0
end

local function dump_range(path, start_addr, length, domain)
	local f = assert(io.open(path, "wb"))
	for i = 0, length - 1 do
		f:write(string.char(byte_at(start_addr + i, domain)))
	end
	f:close()
end

local function dump_hex(path, start_addr, length, domain)
	local f = assert(io.open(path, "w"))
	for row = 0, length - 1, 16 do
		f:write(hex4(start_addr + row) .. ":")
		for col = 0, 15 do
			if row + col < length then
				f:write(" " .. hex2(byte_at(start_addr + row + col, domain)))
			end
		end
		f:write("\n")
	end
	f:close()
end

local function append(path, line)
	local f = assert(io.open(path, "a"))
	f:write(line .. "\n")
	f:close()
end

local function joy_for_frame(frame)
	-- Conservative boot/title/menu progression. This keeps moving without
	-- overwriting gameplay RAM with cheats or depending on savestates.
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

local function snapshot(reason)
	local frame = emu.framecount()
	if frame - last_dump_frame < 30 and reason ~= "periodic" then
		return
	end

	last_dump_frame = frame
	dump_count = dump_count + 1

	local stem = string.format("%s/frame_%06d_%03d_%s", OUT_DIR, frame, dump_count, reason)
	dump_range(stem .. "_cpu_ram.bin", 0x0000, 0x0800)
	dump_hex(stem .. "_cpu_ram.txt", 0x0000, 0x0800)
	dump_range(stem .. "_sram_6000_7fff.bin", 0x6000, 0x2000)
	dump_hex(stem .. "_sram_6000_7fff.txt", 0x6000, 0x2000)

	-- Newer FCEUX builds may support explicit memory domains. If this build
	-- does not, these files will still be produced from the default domain.
	dump_range(stem .. "_ppu_0000_3fff.bin", 0x0000, 0x4000, "ppu")
	dump_hex(stem .. "_nametable_2000_2fff.txt", 0x2000, 0x1000, "ppu")

	append(summary_path, table.concat({
		frame,
		reason,
		ppu_writes_this_frame,
		hex4(ppu_addr),
		stem
	}, "\t"))
end

local function on_ppuaddr_write(addr, size, value)
	ppu_writes_this_frame = ppu_writes_this_frame + 1
	if ppu_addr_hi == nil then
		ppu_addr_hi = value % 0x40
	else
		ppu_addr = ppu_addr_hi * 0x100 + value
		ppu_addr_hi = nil
	end
	append(events_path, table.concat({
		emu.framecount(),
		"PPUADDR",
		hex4(addr or 0x2006),
		hex2(value or 0),
		hex4(ppu_addr)
	}, "\t"))
end

local function on_ppudata_write(addr, size, value)
	ppu_writes_this_frame = ppu_writes_this_frame + 1
	append(events_path, table.concat({
		emu.framecount(),
		"PPUDATA",
		hex4(addr or 0x2007),
		hex2(value or 0),
		hex4(ppu_addr)
	}, "\t"))
	ppu_addr = (ppu_addr + 1) % 0x4000
end

local function try_register_write(addr, fn)
	if memory.registerwrite == nil then
		return false
	end
	local ok = pcall(function() memory.registerwrite(addr, fn) end)
	return ok
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tppu_writes\tlast_ppu_addr\tstem")
append(events_path, "frame\ttype\tcpu_addr\tvalue\ttracked_ppu_addr")

callback_mode = try_register_write(0x2006, on_ppuaddr_write)
callback_mode = try_register_write(0x2007, on_ppudata_write) or callback_mode

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

append(summary_path, "0\tlua_start\t0\t0000\tcallback_mode=" .. tostring(callback_mode))

while emu.framecount() < MAX_FRAMES do
	local frame = emu.framecount()
	ppu_writes_this_frame = 0

	joypad.set(1, joy_for_frame(frame))
	gui.text(2, 8, "Kunio dump frame " .. tostring(frame))
	gui.text(2, 17, "out: " .. OUT_DIR)

	emu.frameadvance()

	if callback_mode and ppu_writes_this_frame >= BURST_THRESHOLD then
		snapshot("ppu_burst")
	elseif frame % SNAPSHOT_EVERY == 0 then
		snapshot("periodic")
	end
end

snapshot("final")
append(summary_path, tostring(emu.framecount()) .. "\tlua_done\t0\t" .. hex4(ppu_addr) .. "\t" .. tostring(dump_count) .. "_dumps")
pcall(function() FCEU.pause() end)
