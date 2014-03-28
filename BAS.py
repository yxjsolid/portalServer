import socket
import portalProtocol
from portalProtocol import Portal_Frame
from time import sleep



def mytest():
    address = ('127.0.0.1', 50100)
    address = ('10.103.12.6', 50100)
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



class portalDaemon():
    def __init__(self, clientIp, serverIp, port):
        self.server = (serverIp, port)
        self.client = (clientIp, port)

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.client)
        pass

    def challengeAck(self, reqFrame):

        ackFrame = Portal_Frame(portalProtocol.ACK_CHALLENGE)
        ackFrame.serialNo = reqFrame.serialNo

        ackFrame.genChallengeAck()


        print "set serialNo = %x \n" % ackFrame.serialNo

        self.doSend(ackFrame)


    def doSend(self, frame):
        try:
            self.udpSocket.sendto(frame.getFrameData(), self.server)			##Send packets
        except KeyboardInterrupt:									##On Ctrl+C, print new line and break
        ##os.system('cls')
            print '\x0D'


    def run(self):
        while True:
            data, addr = self.udpSocket.recvfrom(2048)
            if not data:
                print "client has exist"
                break

            frame = Portal_Frame()
            frame.receiveSome(data)
            self.challengeAck(frame)
            sleep(1)





if __name__ == '__main__':
    port = 50100
    serverIp = "10.103.12.152"
    myIp = '10.103.12.6'


    daemon = portalDaemon(myIp, serverIp, port)

    daemon.run()

    print "test"