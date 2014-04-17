import sys
import socket
import binascii
import os
from time import sleep
import select
import portalProtocol
from portalProtocol import *
import struct

testUser = "xyang"
testPass = "password"

#testUser = "a"
#testPass = "a"
Portal_sharedSecret = "shared"

TIMEOUT_CHALLENGE = 5
TIMEOUT_AUTH = 5

STAT_FAILED = 0
STAT_SUCCESS = 1
STAT_CHALLENGE_TIMEOUT = 2
STAT_AUTH_TIMEOUT = 3



class portalClient():

    _dictSerialNo_ = {}

    def __init__(self, clientIp, serverIp, port, secret):
        self.server = (serverIp, int(port))
        self.client = (clientIp, int(port))

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.client)
        #self.udpSocket.setblocking(0)

        self.sharedSecret = secret
        self.usrName = None
        self.password = None
        self.reqId = 0
        self.challenge = None
        self.serialNo = None

    def getSerialNo(self):
        return self.serialNo

    def genSerialNo(self):
        while True:
            serialNo = random.randint(1, 0xffff)
            if str(serialNo) in self.__class__._dictSerialNo_:
                print "hasKey"
            else:
                self.__class__._dictSerialNo_[str(serialNo)] = 1
                self.serialNo = serialNo
                return serialNo
        pass


    def doReceive(self, timeout):
        #self.udpSocket.setblocking(1)
        ready = select.select([self.udpSocket], [], [], timeout)

        if ready[0]:
            try:
                data = self.udpSocket.recv(4096)
                # print "receive data len = ", len(data)
                return data
            except:
                #icmp unreachable received
                return None
        else:
            print "\n######### receive timeout #######\n"
            return None


    def doSendReq(self, frame):
        try:
            # print "send data:", frame.getFrameData()
            self.udpSocket.sendto(frame.getFrameData(), self.server)
        except KeyboardInterrupt:
            ##os.system('cls')
            print sys.exc_info()
            print '\x0D'





    def run(self, userIpStr, usrName, password):
        self.usrName = usrName
        self.password = password
        self.userIp = socket.ntohl(struct.unpack("I",socket.inet_aton(userIpStr))[0])





        ret = self.doAuth()

        if ret is STAT_AUTH_TIMEOUT or ret is STAT_CHALLENGE_TIMEOUT:
            self.sendTimeout()

        if ret is STAT_SUCCESS:
            self.sendSuccess()

        return ret

    def doLogout(self):

        reqFrame = Portal_Frame(portalProtocol.REQ_LOGOUT)
        reqFrame.setUserIp(self.userIp)
        reqFrame.setSerialNo(self.genSerialNo())

        reqFrame.errcode = 1
        print "\n\n $$$$$$$$$ doLogout, errorcode = ", reqFrame.errcode
        reqFrame.genAuthenticator(None, self.sharedSecret)
        self.doSendReq(reqFrame)


        pass

    def doAuth(self):

        print "\n\n"
        print "############ doAuthReq doChallenge ############"
        ret = self.doChallengeReq()
        print "doChallenge done "

        if ret is not STAT_SUCCESS:
            return ret


        print "\n\n"
        print "############ doAuthReq ############"
        ret = self.doAuthReq()
        print "doAuthReq done"

        if ret is not STAT_SUCCESS:
            pass

        return ret

    def sendSuccess(self):
        f = Portal_Frame(portalProtocol.AFF_ACK_AUTH)
        f.setReqID(self.reqId)
        f.setSerialNo(self.getSerialNo())
        f.setUserIp(self.userIp)
        f.genAuthenticator(None, self.sharedSecret)
        self.doSendReq(f)

    def sendTimeout(self):
        f = Portal_Frame(portalProtocol.REQ_LOGOUT)
        f.setReqID(self.reqId)
        f.setSerialNo(self.getSerialNo())
        f.setErrorCode(1)
        f.setUserIp(self.userIp)
        f.genAuthenticator(None, self.sharedSecret)
        self.doSendReq(f)

    def parseChallengeAck(self, reqFrame, ackData):
        # print "serino", frame.getSerialNo()
        # print "reqID %x " % frame.getReqID()
        if ackData is None:
            print "challenge Ack not received"
            return STAT_CHALLENGE_TIMEOUT

        ackFrame = Portal_Frame()
        ackFrame.receiveSome(ackData)
        ret = ackFrame.validateAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        if ret is False:
            print "challenge Ack validate failed"
            return STAT_FAILED

        if ackFrame.getErrorCode() != CODE_SUCCESS:
            print "challenge request failed, error= ", ackFrame.getErrorCode()
            return STAT_FAILED

        self.reqId = ackFrame.getReqID()
        attr = ackFrame.getAttr(ATTR_CHALLENGE)
        if attr:
            self.challenge = attr.getAttrData()
            # print "receiveChallengeAck", self.challenge
        else:
            raise ValueError

        return STAT_SUCCESS

    def doChallengeReq(self):
        reqFrame = Portal_Frame(portalProtocol.REQ_CHALLENGE)
        reqFrame.setSerialNo(self.genSerialNo())
        reqFrame.setUserIp(self.userIp)
        reqFrame.genAuthenticator(None, self.sharedSecret)


        print "challenge auth:",[buffer(reqFrame.getAuthenticator())[:]]

        self.doSendReq(reqFrame)
        ackData = self.doReceive(TIMEOUT_CHALLENGE)
        ret = self.parseChallengeAck(reqFrame, ackData)
        return ret

    def parseAuthAck(self, reqFrame, ackData):

        if ackData is None:
            print "auth ack not received"
            return STAT_AUTH_TIMEOUT

        ackFrame = Portal_Frame()
        ackFrame.receiveSome(ackData)
        ret = ackFrame.validateAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        if ret is False:
            print "auth Ack validate failed"
            return STAT_FAILED

        if ackFrame.getErrorCode() == CODE_SUCCESS:
            return STAT_SUCCESS
        else:
            return STAT_FAILED

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
        chapPassAttr.genChapPassAttr(reqIdBuff[0], usrPass, challenge)

        reqFrame = Portal_Frame(portalProtocol.REQ_AUTH)
        reqFrame.setUserIp(self.userIp)
        reqFrame.setSerialNo(self.genSerialNo())
        reqFrame.setReqID(reqId)
        reqFrame.appendAttr(nameAttr)
        reqFrame.appendAttr(chapPassAttr)

        print "send auth req, self.userIp = %x"%self.userIp

        reqFrame.genAuthenticator(None, self.sharedSecret)

        self.doSendReq(reqFrame)
        ackData = self.doReceive(TIMEOUT_AUTH)
        # if newFrame is not None:
        #     # newFrame.dumpAll()
        #     # print "getAuthenticator:", [buffer(newFrame.getAuthenticator())[:]]

        ret = self.parseAuthAck(reqFrame, ackData)
        return ret



if __name__ == '__main__':
    port = "50100"
    serverIp = "10.103.12.154"
    myIp = '10.103.12.152'
    userip = "3.3.3.4"

    client = portalClient(myIp, serverIp, port, Portal_sharedSecret)
    ret = client.run(userip, testUser, testPass)


    if ret is STAT_SUCCESS:
        print "login success"
    else:
        print "login failed"
