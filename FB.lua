local socket = require("socket")
local JSON = (loadfile "JSON.lua")()

local sRAM=0x0037 -- game glitches around 680, 1360, 2048, 2731, 3414, 4096, 4780, 5460, 6xxx, 6826, 7502
local yRAM=0x003F
local pRAM=0x003B
local r = {0, 0, 0}
local w = {0, 0}
local s, y, p

local SAVE_FILE = 'FB.State'
local other_port = 8080
local my_port = 8088
local ip = '127.0.0.1'

local DEAD = 177


local function read_mem()
	local y, h
	y = memory.readbyte(yRAM)
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

local udp
if not udp then
	udp = socket.udp()
	udp:setsockname('*', my_port)
end

local function send_message(cmd)
	udp:sendto(JSON:encode(cmd), ip, other_port)
	return JSON:decode(udp:receive())
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
	else
		print('Initialize OK!')
	end
end

-- Program starts here
init_nl()

while true do
	mem = read_mem()
	draw_gui(mem['h'], mem['y'], 0, 0)
	print(mem['y'])
	if mem['y'] == DEAD then
		savestate.load(SAVE_FILE)
	end
	emu.frameadvance()
end
