import speeddb

server = speeddb.SpeedDBServer('db')
server.run(workers=5)