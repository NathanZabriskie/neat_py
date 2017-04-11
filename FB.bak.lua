local socket = require("luasockets")
print(socket._VERSION)
--local cjson = require("cjson")

local sRAM=0x0037 -- game glitches around 680, 1360, 2048, 2731, 3414, 4096, 4780, 5460, 6xxx, 6826, 7502
local yRAM=0x003F
local pRAM=0x003B
local r = {0, 0, 0}
local w = {0, 0}
local s, y, p

local SAVE_FILE = 'FB_START.State'
local other_port = 8080
local my_port = 8088
local ip = '127.0.0.1'

local udp = socket.udp()
udp:setsockname('*', my_port)

local NUM_GENERATIONS = 100
local NUM_GENOMES = 200

local DEAD = 177
local survived_frames = 0

local function read_mem()
	local y, h
	y = memory.readbyte(yRAM)
	y = y / DEAD -- Dead is the maximum y value
	s = memory.readbyte(sRAM)
	p = memory.readbyte(pRAM)

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

	return {h=h, y=y, s=s}
end

local function draw_gui(h, y, cur_generation, cur_genome)
	gui.text(10,9, "Pipe height: " .. h)
	gui.text(10,29,"Bird Height: " .. y)
	gui.text(190,9,"Generation: " .. cur_generation)
	gui.text(190,29, "Genome: " .. cur_genome)
end

local function send_message(cmd)
	udp:sendto(cjson.encode(cmd), ip, other_port)
	return cjson.decode(udp:receive())
end

local function init_nl()
	print('Initializing')
	local cmd = {command='init',
				args={num_inputs=3,
					  num_outputs=1,
					  num_genomes=100,
					  allow_recurrent=true}}
	res = send_message(cmd)
	if res['status'] ~= 'OK' then
		print('Something went wrong during initialization...')
	end
end

local function start_generation()
	local cmd = {command:'start_gen'}
	res = send_message(cmd)
	if res['status'] ~= 'OK' then
		print('Something went wrong during initialization...')
	end
end

-- PROGRAM STARTS HERE
print('Starting up!')
init_nl()
while true do
	t = joypad.get(1)
	joypad.set(1, t)

	ram = read_mem()
	draw_gui(ram['h'], ram['y'], 0, 0)
	emu.frameadvance()
end
for generation=0, NUM_GENERATIONS-1 do
	start_generation()
end

--t = joypad.get(1)
--emu.frameadvance()
