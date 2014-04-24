import socket
import portalProtocol
from portalProtocol import Portal_Frame
from time import sleep
from portalProtocol import *
from radiusClient import *

radiusServer = "10.103.12.254"
shardSecret = "shared"


radiusServer = "122.224.140.174"
shardSecret = "test123"
#radiusServer = "10.8.35.2"
#shardSecret = "password"

Portal_sharedSecret =  "shared"

class portalDaemon():
    def __init__(self, clientIp, serverIp, port, secret):
        self.server = (serverIp, port)
        self.client = (clientIp, port)

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.client)

        self.sharedSecret = secret
        pass

    def doRadiusAuth(self, name, id, chall, chappass ):
        radClient = portalRadiusClient(radiusServer, shardSecret)
        ret = radClient.doAuth(name, id, chall, chappass)
        return ret


    def handleChallengeAck(self, reqFrame):

        ret = reqFrame.validateAuthenticator(None, self.sharedSecret)
        if ret is False:
            print "challenge req valid failed"
            return False

        ackFrame = Portal_Frame(portalProtocol.ACK_CHALLENGE)
        ackFrame.setSerialNo(reqFrame.serialNo)
        ackFrame.genReqId()
        ackFrame.setVersion(reqFrame.getVersion())
        challenge = ackFrame.genChallengeAck()
        self.lastChallenge = challenge

        print "set serialNo = %x \n" % ackFrame.serialNo

        ackFrame.genAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        self.doSend(ackFrame)


    def handleAuthReq(self, reqFrame):

        ret = reqFrame.validateAuthenticator(None, self.sharedSecret)
        if ret is False:
            print "auth req valid failed"
            return False

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
        ret = self.doRadiusAuth(name, chr(reqIdBuff[0]), challenge, chapPass)

        self.sendAuthAck(reqFrame, ret)
        return ret


    def handleLogoutReq(self, frame):
        print "handle Logout Req"
        return True

    def handleAffAuthAck(self, frame):
        print "handleAffAuthAck"
        return True

    def sendAuthAck(self, reqFrame, ret):
        ackFrame = Portal_Frame(portalProtocol.ACK_AUTH)
        ackFrame.setSerialNo(reqFrame.getSerialNo())
        ackFrame.setReqID(reqFrame.getReqID())

        if ret:
            ackFrame.setErrorCode(CODE_SUCCESS)
        else:
            ackFrame.setErrorCode(CODE_REJECT)

        ackFrame.genAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)

        print "\n\n\n\n####### send auth ack###########"
        
        self.doSend(ackFrame)
        print "####### send auth ack done"

    def doSend(self, frame):
        try:
            #self.udpSocket.sendto(frame.getFrameData(), self.server)			##Send packets
            self.udpSocket.sendto(frame.getFrameData(), self.fromAddr)			##Send packets
        except KeyboardInterrupt:									##On Ctrl+C, print new line and break
        ##os.system('cls')
            print '\x0D'

    def notImplement(self, frame):
        print "notImplement"
        raise TypeError

    def parseData(self, data, fromAddr):
        frame = Portal_Frame()
        frame.receiveSome(data)
        self.fromAddr = fromAddr


        func = {
            REQ_CHALLENGE: self.handleChallengeAck,
            ACK_CHALLENGE: self.notImplement,
            REQ_AUTH: self.handleAuthReq,
            ACK_AUTH: self.notImplement,
            REQ_LOGOUT: self.handleLogoutReq,
            ACK_LOGOUT: self.notImplement,
            AFF_ACK_AUTH: self.handleAffAuthAck,
            NTF_LOGOUT: self.notImplement,
            REQ_INFO: self.notImplement,
            ACK_INFO: self.notImplement}

        ret = func[frame.type](frame)
        return

    def run(self):
        while True:
            data, addr = self.udpSocket.recvfrom(2048)
            if not data:
                print "client has exist"
                break

            self.parseData(data, addr)





if __name__ == '__main__':
    port = 2000

    serverIp = "10.103.12.152"
    serverIp = "60.12.241.157"
    myIp = '0.0.0.0'


    daemon = portalDaemon(myIp, serverIp, port, Portal_sharedSecret)

    daemon.run()

    print "test"