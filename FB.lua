local socket = require("socket")
local JSON = (loadfile "JSON.lua")()

local sRAM=0x0037 -- game glitches around 680, 1360, 2048, 2731, 3414, 4096, 4780, 5460, 6xxx, 6826, 7502
local yRAM=0x003F
local pRAM=0x003B
local cRAM=0x0041
local r = {0, 0, 0}
local w = {0, 0}
local s, p

local SAVE_FILE = 'FB.State'
local SAVE_DIR = 'results/flappy'
local other_port = 8080
local my_port = 8088
local ip = '127.0.0.1'

local DEAD = 177
local NUM_GENERATIONS = 100
local NUM_GENOMES = 150

local function read_mem()
	local y, h
	y = memory.readbyte(yRAM)
	s = memory.readbyte(sRAM)
	p = memory.readbyte(pRAM)
	local cleared = memory.readbyte(cRAM)

	if w[1] > 0 then
		w[1] = w[1]-1
	end
	if w[2] > 0 then
		w[2] = w[2]-1
	end
	if p ~= r[1] then
		w[1] = 110
		r[1] = p
	end
	if w[1] == 0 and r[2] ~= r[1] then
		r[2] = r[1]
		w[2] = 20
	end
	if w[2] == 0 and r[3] ~= r[2] then
		r[3] = r[2]
	end
	h = 85+15*r[3]

	return {h=h, y=y, s=s, cleared=cleared}
end


local function draw_gui(h, y, cur_generation, cur_genome, survived_frames)
	gui.text(10,9, "Pipe height: " .. h)
	gui.text(10,29,"Bird Height: " .. y)
	gui.text(190,9,"Generation: " .. cur_generation)
	gui.text(190,29, "Genome: " .. cur_genome)
	gui.text(350,9, "Fitness: " .. survived_frames)
end

local udp
if not udp then
	udp = socket.udp()
	udp:setsockname('*', my_port)
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
				args={num_inputs=2,
					  num_outputs=1,
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

-- Program starts here
init_nl()
savestate.load(SAVE_FILE)

for generation=0, NUM_GENERATIONS-1 do
	start_gen()
	for genome=0, NUM_GENOMES-1 do
		local survived_frames = 0
		local cleared_pipes = 0
		local dead = false
		local fitness = 0.0
		while not dead do
			mem = read_mem()
			cleared_pipes = mem['cleared']
			fitness = survived_frames + cleared_pipes * 100
			--if mem['y'] < 20 then
			--	fitness = fitness / 4
			--end
			draw_gui(mem['h'], mem['y'], generation, genome, fitness)

			if mem['y'] == DEAD then
				savestate.load(SAVE_FILE)
				dead = true
			else
				out = get_output(genome, {mem['y']/DEAD, mem['h']/DEAD})

				out = out[1]
				local controller = joypad.get(1)
				controller['A'] = false
				if mem['s'] ~= 255 and out > 0.5 then
					controller['A'] = true
				end
				joypad.set(controller, 1)
				emu.frameadvance()
				survived_frames = survived_frames + 1
			end
		end

		assign_fitness(genome, fitness)
	end
	end_gen()
	save_best(SAVE_DIR,'gen_' .. tostring(generation))
	if generation % 5 == 0 then
		save_species(SAVE_DIR .. '/' .. tostring(generation))
	end
end

while true do
	mem = read_mem()
	draw_gui(mem['h'], mem['y'], 0, 0)
	if mem['y'] == DEAD then
		savestate.load(SAVE_FILE)
	end
	emu.frameadvance()
end
