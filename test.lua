local socket = require("socket.core")
local cjson = require("cjson")

local port = 8080
local ip = '127.0.0.1'

local cmd = {command='test', data={1,2,3,4}}

udp = socket.udp()
udp:setsockname("*", 8080)

while true do
    udp:sendto(cjson.encode(cmd), ip, port)
end
