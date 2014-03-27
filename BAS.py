import socket
import portalProtocol
from portalProtocol import Portal_Frame
from time import sleep




address = ('127.0.0.1', 50100)
address = ('10.103.12.3', 50100)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(address)

frame = Portal_Frame()

while True:
    data, addr = s.recvfrom(2048)
    if not data:
        print "client has exist"
        break
    print "received:%r"%data, "from", addr

    frame.receiveSome(data)

    frame.dump()

    newFrame = Portal_Frame(portalProtocol.ACK_CHALLENGE)


    serverAddr = ('10.103.12.152', 50100)
    s.sendto (newFrame.send(), serverAddr)			##Send packets

    sleep(1)

s.close()