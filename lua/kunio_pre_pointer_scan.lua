-- Bounded scan for the English pre-pointer label THICK in the live MMC3 CPU map.
-- This avoids assuming a fixed CPU address for a PRG byte after bank switching.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/pre_pointer_scan"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "1800")
local scan_bytes = { 0x88, 0x89, 0x94, 0x85, 0xFF }
local last_hit = ""

local function mkdir(path)
	os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function append(path, line)
	local f = assert(io.open(path, "a"))
	f:write(line .. "\n")
	f:close()
end

local function hex2(v)
	return string.format("%02X", (v or 0) % 0x100)
end

local function hex4(v)
	return string.format("%04X", (v or 0) % 0x10000)
end

local function joy_for_frame(frame)
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

local function match_at(addr)
	for i, expected in ipairs(scan_bytes) do
		if memory.readbyte(addr + i - 1) ~= expected then
			return false
		end
	end
	return true
end

local function context(addr)
	local parts = {}
	for offset = -4, 12 do
		parts[#parts + 1] = hex2(memory.readbyte(addr + offset))
	end
	return table.concat(parts, " ")
end

mkdir(OUT_DIR)
local hits_path = OUT_DIR .. "/matches.tsv"
local summary_path = OUT_DIR .. "/summary.tsv"
append(hits_path, "frame\tcpu_addr\tbytes\tcontext")
append(summary_path, "frame\treason\tmatches")
append(summary_path, "0\tlua_start\t0")

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

local matches = 0
while emu.framecount() < MAX_FRAMES do
	local frame = emu.framecount()
	joypad.set(1, joy_for_frame(frame))
	for addr = 0x8000, 0xFFFB do
		if match_at(addr) then
			local key = tostring(frame) .. ":" .. hex4(addr)
			if key ~= last_hit then
				matches = matches + 1
				last_hit = key
				append(hits_path, table.concat({
					frame,
					"$" .. hex4(addr),
					"88 89 94 85 FF",
					context(addr),
				}, "\t"))
			end
		end
	end
	gui.text(2, 8, "Pre-pointer scan " .. tostring(frame))
	gui.text(2, 17, "THICK matches: " .. tostring(matches))
	emu.frameadvance()
end

append(summary_path, tostring(emu.framecount()) .. "\tlua_done\t" .. tostring(matches))
pcall(function() FCEU.pause() end)
