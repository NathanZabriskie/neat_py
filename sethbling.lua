-- MarI/O by SethBling
-- Feel free to use this code, but please do not redistribute it.
-- Intended for use with the BizHawk emulator and Super Mario World or Super Mario Bros. ROM.
-- For SMW, make sure you have a save state named "DP1.state" at the beginning of a level,
-- and put a copy in both the Lua folder and the root directory of BizHawk.

-- Edited by Nathan Zabriskie
local socket = require("socket")
local JSON = (loadfile "JSON.lua")()

local SAVE_DIR = 'results/mario_bros'
local other_port = 8080
local my_port = 8088
local ip = '127.0.0.1'

NUM_GENOMES = 300

if gameinfo.getromname() == "Super Mario World (USA)" then
	Filename = "DP1.state"
	ButtonNames = {
		"A",
		"B",
		"X",
		"Y",
		"Up",
		"Down",
		"Left",
		"Right",
	}
elseif gameinfo.getromname() == "Super Mario Bros." then
	Filename = "SMB1-1.state"
	ButtonNames = {
		"A",
		"B",
		"Up",
		"Down",
		"Left",
		"Right",
	}
end

BoxRadius = 6
InputSize = (BoxRadius*2+1)*(BoxRadius*2+1)

Inputs = InputSize
Outputs = #ButtonNames
TimeoutConstant = 20


--[[
DeltaDisjoint = 2.0
DeltaWeights = 0.4
DeltaThreshold = 1.0

StaleSpecies = 15

MutateConnectionsChance = 0.25
PerturbChance = 0.90
CrossoverChance = 0.75
LinkMutationChance = 2.0
NodeMutationChance = 0.50
BiasMutationChance = 0.40
StepSize = 0.1
DisableMutationChance = 0.4
EnableMutationChance = 0.2
MaxNodes = 1000000
--]]

function getPositions()
	if gameinfo.getromname() == "Super Mario World (USA)" then
		marioX = memory.read_s16_le(0x94)
		marioY = memory.read_s16_le(0x96)

		local layer1x = memory.read_s16_le(0x1A);
		local layer1y = memory.read_s16_le(0x1C);

		screenX = marioX-layer1x
		screenY = marioY-layer1y
	elseif gameinfo.getromname() == "Super Mario Bros." then
		marioX = memory.readbyte(0x6D) * 0x100 + memory.readbyte(0x86)
		marioY = memory.readbyte(0x03B8)+16

		screenX = memory.readbyte(0x03AD)
		screenY = memory.readbyte(0x03B8)
	end
end

function getTile(dx, dy)
	if gameinfo.getromname() == "Super Mario World (USA)" then
		x = math.floor((marioX+dx+8)/16)
		y = math.floor((marioY+dy)/16)

		return memory.readbyte(0x1C800 + math.floor(x/0x10)*0x1B0 + y*0x10 + x%0x10)
	elseif gameinfo.getromname() == "Super Mario Bros." then
		local x = marioX + dx + 8
		local y = marioY + dy - 16
		local page = math.floor(x/256)%2

		local subx = math.floor((x%256)/16)
		local suby = math.floor((y - 32)/16)
		local addr = 0x500 + page*13*16+suby*16+subx

		if suby >= 13 or suby < 0 then
			return 0
		end

		if memory.readbyte(addr) ~= 0 then
			return 1
		else
			return 0
		end
	end
end

function getSprites()
	if gameinfo.getromname() == "Super Mario World (USA)" then
		local sprites = {}
		for slot=0,11 do
			local status = memory.readbyte(0x14C8+slot)
			if status ~= 0 then
				spritex = memory.readbyte(0xE4+slot) + memory.readbyte(0x14E0+slot)*256
				spritey = memory.readbyte(0xD8+slot) + memory.readbyte(0x14D4+slot)*256
				sprites[#sprites+1] = {["x"]=spritex, ["y"]=spritey}
			end
		end

		return sprites
	elseif gameinfo.getromname() == "Super Mario Bros." then
		local sprites = {}
		for slot=0,4 do
			local enemy = memory.readbyte(0xF+slot)
			if enemy ~= 0 then
				local ex = memory.readbyte(0x6E + slot)*0x100 + memory.readbyte(0x87+slot)
				local ey = memory.readbyte(0xCF + slot)+24
				sprites[#sprites+1] = {["x"]=ex,["y"]=ey}
			end
		end

		return sprites
	end
end

function getExtendedSprites()
	if gameinfo.getromname() == "Super Mario World (USA)" then
		local extended = {}
		for slot=0,11 do
			local number = memory.readbyte(0x170B+slot)
			if number ~= 0 then
				spritex = memory.readbyte(0x171F+slot) + memory.readbyte(0x1733+slot)*256
				spritey = memory.readbyte(0x1715+slot) + memory.readbyte(0x1729+slot)*256
				extended[#extended+1] = {["x"]=spritex, ["y"]=spritey}
			end
		end

		return extended
	elseif gameinfo.getromname() == "Super Mario Bros." then
		return {}
	end
end

function getInputs()
	getPositions()

	sprites = getSprites()
	extended = getExtendedSprites()

	local inputs = {}

	for dy=-BoxRadius*16,BoxRadius*16,16 do
		for dx=-BoxRadius*16,BoxRadius*16,16 do
			inputs[#inputs+1] = 0

			tile = getTile(dx, dy)
			if tile == 1 and marioY+dy < 0x1B0 then
				inputs[#inputs] = 1
			end

			for i = 1,#sprites do
				distx = math.abs(sprites[i]["x"] - (marioX+dx))
				disty = math.abs(sprites[i]["y"] - (marioY+dy))
				if distx <= 8 and disty <= 8 then
					inputs[#inputs] = -1
				end
			end

			for i = 1,#extended do
				distx = math.abs(extended[i]["x"] - (marioX+dx))
				disty = math.abs(extended[i]["y"] - (marioY+dy))
				if distx < 8 and disty < 8 then
					inputs[#inputs] = -1
				end
			end
		end
	end

	--mariovx = memory.read_s8(0x7B)
	--mariovy = memory.read_s8(0x7D)

	return inputs
end


function clearJoypad()
	controller = {}
	for b = 1,#ButtonNames do
		controller["P1 " .. ButtonNames[b]] = false
	end
	joypad.set(controller)
end


local udp
if not udp then
	udp = socket.udp()
	udp:setsockname('*', my_port)
end

local function draw_gui(cur_generation, cur_genome, survived_frames)
	gui.drawBox(0, 0, 300, 26, 0xD0FFFFFF, 0xD0FFFFFF)
	gui.text(10,9,"Generation: " .. cur_generation)
	gui.text(10,29, "Genome: " .. cur_genome)
	gui.text(190,9, "Fitness: " .. survived_frames)
end

local function send_message(cmd)
	udp:sendto(JSON:encode(cmd), ip, other_port)
	res = JSON:decode(udp:receive())
	if res['status'] ~= 'OK' then
		print('Got bad status ' .. res['status'])
	end
	return res
end


local function init_nl()
	print('Initializing')
	local cmd = {command='init',
				args={num_inputs=Inputs,
					  num_outputs=Outputs,
					  num_genomes=NUM_GENOMES,
					  allow_recurrent=true}}
	send_message(cmd)
end


local function start_gen()
	local cmd = {command='start_gen'}
	send_message(cmd)
end


local function end_gen()
	local cmd = {command='end_gen'}
	send_message(cmd)
end


local function assign_fitness(genome, fitness)
	local cmd = {command='assign_fitness',
				 args={genome=genome,
				 	   fitness=fitness}}
	send_message(cmd)
end


local function get_output(genome, inputs)
	local cmd = {command='get_output',
				 args={genome=genome,
			           inputs=inputs}}
	local res = send_message(cmd)
	return res['result']
end


local function save_best(save_dir, save_file)
	local cmd = {command='save_best',
				 args={outdir=save_dir,
			 		   outfile=save_file}}
	send_message(cmd)
end


local function save_species(save_dir)
	local cmd = {command='save_species',
				 args={outdir=save_dir}}
	send_message(cmd)
end


local function set_best(best_genome)
	local cmd = {command='set_best',
			     args={genome=best_genome}}
	send_message(cmd)
end


local function save_backup(directory, file)
	local cmd = {command='save_backup',
				 args={outdir=directory,
			 		   outfile=file}}
	send_message(cmd)
end


local function process_outputs(outputs)
	local out = {}
    for o=1,Outputs do
            local button = "P1 " .. ButtonNames[o]
            if outputs[o] > 0.5 then
                    out[button] = true
            else
                    out[button] = false
            end
    end

	return out
end


function evaluateCurrent(genome)
	inputs = getInputs()
	local out = get_output(genome, inputs)
	controller = process_outputs(out)

	if controller["P1 Left"] and controller["P1 Right"] then
		controller["P1 Left"] = false
		controller["P1 Right"] = false
	end
	if controller["P1 Up"] and controller["P1 Down"] then
		controller["P1 Up"] = false
		controller["P1 Down"] = false
	end

	joypad.set(controller)
end

-- Program starts here

--[[gui.drawText(0, 0, "Gen " .. pool.generation .. " species " .. pool.currentSpecies .. " genome " .. pool.currentGenome .. " (" .. math.floor(measured/total*100) .. "%)", 0xFF000000, 11)
gui.drawText(0, 12, "Fitness: " .. math.floor(rightmost - (pool.currentFrame) / 2 - (timeout + timeoutBonus)*2/3), 0xFF000000, 11)
gui.drawText(100, 12, "Max Fitness: " .. math.floor(pool.maxFitness), 0xFF000000, 11)--]]
init_nl()
local generation = 0
local found_best = false

while true do
	generation = generation + 1

	start_gen()
	for genome=0, NUM_GENOMES-1 do
		local rightmost = 0
		local timeout = TimeoutConstant
		local dead = false
		local frame = 1
		clearJoypad()
		savestate.load(Filename)
		while not dead do
			getPositions()
		    if marioX > rightmost then
	            rightmost = marioX
	            timeout = TimeoutConstant
		    end
			timeout = timeout - 1

			local timeoutBonus = frame / 4
			if timeout + timeoutBonus <= 0 then
				dead = true
				local fitness = rightmost - frame / 2
				if gameinfo.getromname() == "Super Mario Bros." and rightmost > 3186 then
	            	fitness = fitness + 1000
	            end
				assign_fitness(genome, math.max(0,fitness))
			else
				evaluateCurrent(genome)
				joypad.set(controller)
				frame = frame + 1
				emu.frameadvance()
				draw_gui(generation, genome, math.floor(math.max(0, rightmost - frame / 2)))
			end
		end
	end

	end_gen()
	if generation % 5 == 0 then
		--save_best(SAVE_DIR,'gen_' .. tostring(generation))
		--save_species(SAVE_DIR .. '/' .. tostring(generation))
		save_backup(SAVE_DIR, 'gen_' .. tostring(generation) .. '.pkl')
	end
end
