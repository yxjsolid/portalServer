import socket
import portalProtocol
from portalProtocol import Portal_Frame
from time import sleep
from portalProtocol import *
from radiusClient import *

radiusServer = "10.103.12.152"
shardSecret = "password"


class portalDaemon():
    def __init__(self, clientIp, serverIp, port):
        self.server = (serverIp, port)
        self.client = (clientIp, port)

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.client)
        pass

    def challengeAck(self, reqFrame):

        ackFrame = Portal_Frame(portalProtocol.ACK_CHALLENGE)
        ackFrame.setSerialNo(reqFrame.serialNo)
        ackFrame.genReqId()
        challenge = ackFrame.genChallengeAck()
        self.lastChallenge = challenge

        print "set serialNo = %x \n" % ackFrame.serialNo

        self.doSend(ackFrame)

    def doRadiusAuth(self, name, id, chall, chappass ):
        radClient = portalRadiusClient(radiusServer, shardSecret)
        ret = radClient.doAuth(name, id, chall, chappass)
        return ret

    def handleAuthReq(self, reqFrame):

        reqId = reqFrame.getReqID()
        nameAttr = reqFrame.getAttr(ATTR_USERNAME)
        chapPassAttr = reqFrame.getAttr(ATTR_CHAP_PASSWORD)

        if nameAttr is None or chapPassAttr is None:
            raise AttributeError

        name = buffer(nameAttr.getAttrData())[:]
        chapPass = buffer(chapPassAttr.getAttrData())[:]
        challenge = buffer(self.lastChallenge)[:]

        print "handleAuthReq, reqId: %x" % reqId
        print "handleAuthReq, name: ", name
        print "handleAuthReq, chap: ", chapPass
        print "handleAuthReq, challenge", challenge

        print binascii.b2a_hex(name)
        print binascii.b2a_hex(chapPass)
        print binascii.b2a_hex(challenge)


        reqtmp = c_ushort(reqId)
        reqIdBuff = (c_ubyte * 2)()
        memmove(addressof(reqIdBuff), addressof(reqtmp), 2)
        ret = self.doRadiusAuth(name, chr(reqIdBuff[1]), challenge, chapPass)

        self.sendAuthAck(reqFrame, ret)
        return ret

    def sendAuthAck(self, reqFrame, ret):
        ackFrame = Portal_Frame(portalProtocol.ACK_AUTH)
        ackFrame.setSerialNo(reqFrame.getSerialNo())
        ackFrame.setReqID(reqFrame.getReqID())

        if ret:
            ackFrame.setErrorCode(CODE_SUCCESS)
        else:
            ackFrame.setErrorCode(CODE_REJECT)

        self.doSend(ackFrame)

    def doSend(self, frame):
        try:
            self.udpSocket.sendto(frame.getFrameData(), self.server)			##Send packets
        except KeyboardInterrupt:									##On Ctrl+C, print new line and break
        ##os.system('cls')
            print '\x0D'

    def notImplement(self, frame):
        raise TypeError

    def parseData(self, data):
        frame = Portal_Frame()
        frame.receiveSome(data)

        func = {
            REQ_CHALLENGE: self.challengeAck,
            ACK_CHALLENGE: self.notImplement,
            REQ_AUTH: self.handleAuthReq,
            ACK_AUTH: self.notImplement,
            REQ_LOGOUT: self.notImplement,
            ACK_LOGOUT: self.notImplement,
            AFF_ACK_AUTH: self.notImplement,
            NTF_LOGOUT: self.notImplement,
            REQ_INFO: self.notImplement,
            ACK_INFO: self.notImplement}

        func[frame.type](frame)
        return

    def run(self):
        while True:
            data, addr = self.udpSocket.recvfrom(2048)
            if not data:
                print "client has exist"
                break

            self.parseData(data)
            sleep(1)





if __name__ == '__main__':
    port = 50100
    serverIp = "10.103.12.152"
    myIp = '10.103.12.6'


    daemon = portalDaemon(myIp, serverIp, port)

    daemon.run()

    print "test"