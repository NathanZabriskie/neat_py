local socket = require("socket.core")
local cjson = require("cjson")

local other_port = 8080
local ip = '127.0.0.1'

print('Starting socket')
udp = socket.udp()
udp:setsockname("*", 8088)

local cmd = {command='init', args={num_inputs=2, num_outputs=2, num_genomes=100, allow_recurrent=true}}
udp:sendto(cjson.encode(cmd), ip, other_port)
res_json = udp:receive()
res = cjson.decode(res_json)

cmd = {command='start_gen'}
udp:sendto(cjson.encode(cmd), ip, other_port)
res_json = udp:receive()
res = cjson.decode(res_json)

cmd = {command='get_output', args={genome=0,inputs={0.1,0.3}}}
udp:sendto(cjson.encode(cmd), ip, other_port)
res_json = udp:receive()
res = cjson.decode(res_json)
for i, v in pairs(res['result']) do
    print(i, v)
end
