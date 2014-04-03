import sys
import socket
import binascii
import os
from time import sleep
import select
import portalProtocol
from portalProtocol import *


testUser = "test"
testPass = "password"
Portal_sharedSecret =  "shared"

TIMEOUT_CHALLENGE = 5
TIMEOUT_AUTH = 5

class portalClient():
    def __init__(self, clientIp, serverIp, port, secret):
        self.server = (serverIp, int(port))
        self.client = (clientIp, int(port))

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.client)
        #self.udpSocket.setblocking(0)

        self.sharedSecret = secret
        self.usrName = None
        self.password = None
        self.reqId = None
        self.challenge = None

    def doReceive(self, timeout):
        self.udpSocket.setblocking(1)
        print "timeout ", timeout
        ready = select.select([self.udpSocket], [], [], timeout)

        if ready[0]:
            try:
                data = self.udpSocket.recv(4096)
                # print "receive data len = ", len(data)
                newFrame = Portal_Frame()
                newFrame.receiveSome(data)
                return newFrame
            except:
                #icmp unreachable received
                return None
        else:
            print "\n######### receive timeout #######\n"
            return None


    def doSendReq(self, frame, timeout):
        try:
            # print "send data:", frame.getFrameData()
            self.udpSocket.sendto(frame.getFrameData(), self.server)
        except KeyboardInterrupt:
            ##os.system('cls')
            print sys.exc_info()
            print '\x0D'

        newFrame = self.doReceive(timeout)
        # if newFrame is not None:
        #     # newFrame.dumpAll()
        #     # print "getAuthenticator:", [buffer(newFrame.getAuthenticator())[:]]

        return newFrame

    def doAuth(self, usrName, password):
        self.usrName = usrName
        self.password = password
        self.status = REQ_CHALLENGE


        print "\n\n"
        print "############ doAuthReq doChallenge ############"
        ret = self.doChallengeReq()
        print "doChallenge done "

        if ret is False:
            return False


        print "\n\n"
        print "############ doAuthReq ############"
        ret = self.doAuthReq()
        print "doAuthReq done"

        return ret

    def parseChallengeAck(self, reqFrame, ackFrame):
        # print "serino", frame.getSerialNo()
        # print "reqID %x " % frame.getReqID()
        if ackFrame is None:
            print "challenge Ack not received"
            return False

        ret = ackFrame.validateAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        if ret is False:
            print "challenge Ack validate failed"
            return False

        self.reqId = ackFrame.getReqID()
        attr = ackFrame.getAttr(ATTR_CHALLENGE)
        if attr:
            self.challenge = attr.getAttrData()
            # print "receiveChallengeAck", self.challenge
        else:
            raise ValueError

        return True

    def doChallengeReq(self):
        reqFrame = Portal_Frame(portalProtocol.REQ_CHALLENGE)
        reqFrame.genAuthenticator(None, self.sharedSecret)

        print "challenge auth:",[buffer(reqFrame.getAuthenticator())[:]]

        ackFrame = self.doSendReq(reqFrame, TIMEOUT_CHALLENGE)
        ret = self.parseChallengeAck(reqFrame, ackFrame)
        return ret

    def parseAuthAck(self, reqFrame, ackFrame):

        if ackFrame is None:
            print "auth ack not received"
            return False

        ret = ackFrame.validateAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        if ret is False:
            print "auth Ack validate failed"
            return False

        if ackFrame.getErrorCode() == CODE_SUCCESS:
            return True
        else:
            return False

    def doAuthReq(self):
        reqId = self.reqId
        usrName = self.usrName
        usrPass = self.password
        challenge = self.challenge

        nameAttr = Portal_Attr()
        nameAttr.genUserNameAttr(usrName)

        reqtmp = c_ushort(reqId)
        reqIdBuff = (c_ubyte * 2)()
        memmove(addressof(reqIdBuff), addressof(reqtmp), 2)

        # print "reqtmp" ,reqtmp
        # print "reqIdBuff", reqIdBuff[0]
        # print "reqIdBuff", reqIdBuff[1]

        chapPassAttr = Portal_Attr()
        chapPassAttr.genChapPassAttr(reqIdBuff[1], usrPass, challenge)

        reqFrame = Portal_Frame(portalProtocol.REQ_AUTH)
        reqFrame.genSerialNo()
        reqFrame.setReqID(reqId)
        reqFrame.appendAttr(nameAttr)
        reqFrame.appendAttr(chapPassAttr)

        reqFrame.genAuthenticator(None, self.sharedSecret)

        ackFrame = self.doSendReq(reqFrame, TIMEOUT_AUTH)
        ret = self.parseAuthAck(reqFrame, ackFrame)
        return ret



if __name__ == '__main__':
    port = "50100"
    serverIp = "10.103.12.6"
    myIp = '10.103.12.152'

    client = portalClient(myIp, serverIp, port, Portal_sharedSecret)
    ret = client.doAuth(testUser, testPass)

    if ret:
        print "login success"
    else:
        print "login failed"
