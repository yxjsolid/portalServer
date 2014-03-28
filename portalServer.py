import sys
import socket
import binascii
import os
from time import sleep
import select
import portalProtocol
from portalProtocol import Portal_Frame



def test():
    port = 50100
    serverIp = "10.103.12.6"
    myIp = '10.103.12.152'


    strIP="127.0.0.1"		##Multicast (destination) IP to which data will be sent
    intPort="50100"			##UDP port pair with the destination IP
    address = ('127.0.0.1', 50100)

    strData=binascii.unhexlify('280000006d08000003f49451016f4e1531000000000401460800000000000001005e010548000001')  ##Data to send to multicast address
    strData=binascii.unhexlify('280000006d08000003f49451016f4e1531000000000401460800000000000001005e010548000001')
    intSleepTime=100		##The script will wait for X milliseconds before next packet is sent; the default is 100ms.
    intTTL=5				##IP header TTL
    intPacketCount=0		##Basic counter of packets sent
    strStdOut=""			##Used to send messages to stdout


    BASAddress = (serverIp, port)

    address = (myIp, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(address)



    frame = Portal_Frame()


    try:
        s.sendto (frame.send(), BASAddress)			##Send packets
        intPacketCount = intPacketCount + 1						##Increment packet counter
        strStdOut = "Packets Sent: " + str(intPacketCount)		##Stdout message
        sys.stdout.write(strStdOut + '\x08'*len(strStdOut))		##Update stdout
        print "tttttttt"
        #sleep(intSleepTime)										##Wait before sending next packet

    except KeyboardInterrupt:									##On Ctrl+C, print new line and break
        ##os.system('cls')
        print '\x0D'

    print "aaaaaaaaaaaaaaaaaa"

    s.setblocking(1)
    ready = select.select([s], [], [], None)
    print "ready", ready

    if ready[0]:
        print "11111111"
        data =s.recv(4096)
        print "22222"

        newFrame = Portal_Frame(portalProtocol.ACK_CHALLENGE)


        newFrame.receiveSome(data)

        print "receive frame"
        newFrame.dump()


    else:
        print "timeout"


class portalClient():
    def __init__(self, clientIp, serverIp, port):
        self.server = (serverIp, port)
        self.client = (clientIp, port)

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.client)
        pass

    def doAuth(self):
        pass


    def doReceive(self):
        ready = select.select([self.udpSocket], [], [], 2)

        if ready[0]:
            data = self.udpSocket.recv(4096)

            print "receive data len = ", len(data)

            newFrame = Portal_Frame(portalProtocol.ACK_CHALLENGE)
            newFrame.receiveSome(data)

            return newFrame

        else:
            print "\n\n######### timeout #######\n\n"
            return None

    def doChallenge(self):
        frame = Portal_Frame(portalProtocol.ACK_CHALLENGE)

        print "%x" % frame.serialNo

        try:
            self.udpSocket.sendto(frame.getFrameData(), self.server)			##Send packets
        except KeyboardInterrupt:									##On Ctrl+C, print new line and break
        ##os.system('cls')
            print '\x0D'

        newFrame = self.doReceive()
        newFrame.dumpAll()

if __name__ == '__main__':
    port = 50100
    serverIp = "10.103.12.6"
    myIp = '10.103.12.152'


    client = portalClient(myIp, serverIp, port)

    client.doChallenge()

    print "test"