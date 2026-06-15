-- Kunio period drama Bank 1 text-candidate read watcher for FCEUX.
--
-- Load the ROM first, then run this script from FCEUX's Lua window, or launch
-- it through scripts/run_fceux_lua_analysis.py --lua-script lua/kunio_bank1_watch.lua.
-- The watched CPU addresses come from rom_analysis/bank1_candidate_contexts.md.

local OUT_DIR = os.getenv("KUNIO_ANALYSIS_OUTPUT") or "rom_analysis/fceux_bank1_watch"
local MAX_FRAMES = tonumber(os.getenv("KUNIO_MAX_FRAMES") or "7200")
local HIT_LIMIT = tonumber(os.getenv("KUNIO_HIT_LIMIT") or "20000")

local summary_path = OUT_DIR .. "/summary.tsv"
local reads_path = OUT_DIR .. "/bank1_reads.tsv"

local hit_count = 0
local registered_count = 0
local callback_mode = false
local stopped_for_limit = false

local targets = {
	-- label, category, ROM hit, CPU record start, CPU record end, expected bytes
	{ label = "katana_watch_weapon", category = "weapon", rom = 0x05644, start = 0x9633, stop = 0x9637, bytes = "82 8C 91" },
	{ label = "kusuri_recovery", category = "recovery", rom = 0x05BDF, start = 0x9BCD, stop = 0x9BD3, bytes = "82 87 A3" },
	{ label = "soubi_ui_a", category = "ui", rom = 0x0602E, start = 0xA01A, stop = 0xA02B, bytes = "9C 90 A8" },
	{ label = "chikara_stat_a", category = "stat", rom = 0x06605, start = 0xA5EE, stop = 0xA5F8, bytes = "93 88 AA" },
	{ label = "chikara_stat_b", category = "stat", rom = 0x066FB, start = 0xA6EA, stop = 0xA6F2, bytes = "93 88 AA" },
	{ label = "chikara_stat_c", category = "stat", rom = 0x06845, start = 0xA82E, stop = 0xA838, bytes = "93 88 AA" },
	{ label = "chikara_stat_d", category = "stat", rom = 0x06B4A, start = 0xAB32, stop = 0xAB3F, bytes = "93 88 AA" },
	{ label = "soubi_ui_b", category = "ui", rom = 0x06BDF, start = 0xABCB, stop = 0xABD3, bytes = "9C 90 A8" },
	{ label = "okane_ui", category = "ui", rom = 0x06DE3, start = 0xADD1, stop = 0xADD7, bytes = "85 86 98" },
	{ label = "soubi_ui_c", category = "ui", rom = 0x06FA1, start = 0xAF91, stop = 0xAF9A, bytes = "9C 90 A8" },
	{ label = "chikara_stat_e", category = "stat", rom = 0x071A4, start = 0xB192, stop = 0xB19C, bytes = "93 88 AA" },
	{ label = "raifu_ui_a", category = "ui", rom = 0x0736A, start = 0xB359, stop = 0xB35E, bytes = "BB 95 AF" },
	{ label = "raifu_ui_b", category = "ui", rom = 0x0739D, start = 0xB38C, stop = 0xB391, bytes = "BB 95 AF" },
}

local function mkdir(path)
	os.execute('mkdir "' .. path .. '" >NUL 2>NUL')
end

local function hex2(v)
	return string.format("%02X", v % 0x100)
end

local function hex4(v)
	return string.format("%04X", v % 0x10000)
end

local function hex5(v)
	return string.format("%05X", v % 0x100000)
end

local function append(path, line)
	local f = assert(io.open(path, "a"))
	f:write(line .. "\n")
	f:close()
end

local function byte_at(addr)
	local ok, value = pcall(function() return memory.readbyte(addr) end)
	if ok and value ~= nil then
		return value
	end
	return 0
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

local function read_context(addr)
	local bytes = {}
	for offset = -2, 5 do
		bytes[#bytes + 1] = hex2(byte_at(addr + offset))
	end
	return table.concat(bytes, " ")
end

local function on_read_for(target)
	return function(addr, size, value)
		if hit_count >= HIT_LIMIT then
			stopped_for_limit = true
			return
		end
		hit_count = hit_count + 1
		local actual_addr = addr or 0
		local actual_value = value
		if actual_value == nil then
			actual_value = byte_at(actual_addr)
		end
		append(reads_path, table.concat({
			emu.framecount(),
			target.label,
			target.category,
			"ROM+0x" .. hex5(target.rom),
			"$" .. hex4(actual_addr),
			hex2(actual_value),
			"$" .. hex4(target.start) .. "-$" .. hex4(target.stop),
			target.bytes,
			read_context(actual_addr)
		}, "\t"))
	end
end

local function register_read(addr, fn)
	if memory.registerread == nil then
		return false
	end
	local ok = pcall(function() memory.registerread(addr, fn) end)
	if ok then
		return true
	end
	ok = pcall(function() memory.registerread(addr, 1, fn) end)
	return ok
end

mkdir(OUT_DIR)
append(summary_path, "frame\treason\tregistered\thits\tdetail")
append(reads_path, "frame\tlabel\tcategory\trom_hit\tcpu_addr\tvalue\trecord_cpu_range\texpected_bytes\tcontext")

for _, target in ipairs(targets) do
	for addr = target.start, target.stop do
		if register_read(addr, on_read_for(target)) then
			registered_count = registered_count + 1
			callback_mode = true
		end
	end
end

pcall(function() FCEU.speedmode("turbo") end)
pcall(function() emu.speedmode("turbo") end)

append(summary_path, table.concat({
	0,
	"lua_start",
	registered_count,
	0,
	"callback_mode=" .. tostring(callback_mode)
}, "\t"))

while emu.framecount() < MAX_FRAMES and not stopped_for_limit do
	local frame = emu.framecount()
	joypad.set(1, joy_for_frame(frame))
	gui.text(2, 8, "Kunio Bank1 watch frame " .. tostring(frame))
	gui.text(2, 17, "hits: " .. tostring(hit_count) .. " registered: " .. tostring(registered_count))
	emu.frameadvance()

	if frame % 300 == 0 then
		append(summary_path, table.concat({
			frame,
			"periodic",
			registered_count,
			hit_count,
			"running"
		}, "\t"))
	end
end

local final_reason = "lua_done"
if stopped_for_limit then
	final_reason = "hit_limit"
end

append(summary_path, table.concat({
	emu.framecount(),
	final_reason,
	registered_count,
	hit_count,
	"out=" .. OUT_DIR
}, "\t"))
pcall(function() FCEU.pause() end)
