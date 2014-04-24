import sys
import socket
import binascii
import os
from time import sleep
import select
import portalFrame
from portalFrame import *
import struct
import threading
testUser = "xyang"
testPass = "password"

#testUser = "a"
#testPass = "a"
Portal_sharedSecret = "shared"

TIMEOUT_CHALLENGE = 5
TIMEOUT_AUTH = 15

STAT_FAILED = 0
STAT_SUCCESS = 1
STAT_AUTH_DONE = 2
STAT_CHALLENGE_TIMEOUT = 3
STAT_AUTH_TIMEOUT = 4



class portalClient():

    _dictSerialNo_ = {}

    def __init__(self,userIpStr, serverIp, port, secret, receiver):
        self.server = (serverIp, int(port))
        self.userIp = socket.ntohl(struct.unpack("I", socket.inet_aton(userIpStr))[0])
        self.threadEvent = threading.Event()

        self.receiver = receiver
        self.sharedSecret = secret
        self.usrName = None
        self.password = None
        self.reqId = 0
        self.challenge = None
        self.serialNo = None

    def waitAckPkt(self, pktType, timeout):
        self.waitPktType = pktType
        self.newFrame = None
        self.threadEvent.clear()
        self.threadEvent.wait(timeout)

        if self.newFrame != None:
            #print "got new frame"
            pass
        else:
            #print "timeout"
            pass
        return self.newFrame


    def clientWakeup(self, frame):
        if frame.type == self.waitPktType:
            self.threadEvent.set()
            self.newFrame = frame
        else:
            print "client recetive pkt type ", frame.type

    def getSerialNo(self):
        return self.serialNo


    def debugGenSerialNo(self):
        self.serialNo = 0x1
        return 1

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


    def doReceiveAck(self, timeout):
        ready = select.select([self.udpSocket], [], [], timeout)
        packetCnt = 0
        if ready[0]:
            try:
                data = self.udpSocket.recv(4096)
                packetCnt += 1

                pkt = Portal_Frame()
                pkt.receiveSome(data)
                self.udpSocket.close()
                return pkt
            except:
                print sys.exc_info()
                print "\n\n\n xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                return None
                # else:
                #     print "\n######### receive timeout #######\n"
                #     return None



    def doSendReq(self, frame):

        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # print "send data:", frame.getFrameData()
            self.udpSocket.sendto(frame.getFrameData(), self.server)
        except KeyboardInterrupt:
            ##os.system('cls')
            print sys.exc_info()
            print '\x0D'


    def run(self, userIpStr, usrName, password, isPap):
        self.usrName = usrName
        self.password = password
        self.userIp = socket.ntohl(struct.unpack("I",socket.inet_aton(userIpStr))[0])

        if isPap:
            ret = self.doPapAuth()
        else:
            ret = self.doChapAuth()

        if ret is STAT_AUTH_TIMEOUT or ret is STAT_CHALLENGE_TIMEOUT:
            self.sendTimeout()

        print "ret",ret

        if ret is STAT_SUCCESS:
            print "send success"
            self.sendSuccess()

        return ret

    def doLogout(self):

        reqFrame = Portal_Frame(portalFrame.REQ_LOGOUT)
        reqFrame.setUserIp(self.userIp)
        reqFrame.setSerialNo(self.genSerialNo())
        reqFrame.genAuthenticator(None, self.sharedSecret)
        self.doSendReq(reqFrame)
        ackFrame = self.waitAckPkt(ACK_LOGOUT, TIMEOUT_AUTH)
        pass

    def doPapAuth(self):

        print "############ doPapAuth ############"
        ret = self.doPapAuthReq()
        print "doPapAuth done,ret=", ret

        return ret
        pass

    def doChapAuth(self):

        print "\n\n"
        print "############ doAuthReq doChallenge ############"
        ret = self.doChallengeReq()


        if ret is STAT_AUTH_DONE:
            return STAT_SUCCESS

        if ret is not STAT_SUCCESS:
            print "doChallenge failed "
            return ret
        else:
            print "doChallenge done "


        print "\n\n"
        print "############ doChapAuth ############"
        ret = self.doChapAuthReq()
        print "doChapAuthReq done, ret = ",ret

        if ret is not STAT_SUCCESS:
            pass

        return ret

    def sendSuccess(self):
        f = Portal_Frame(portalFrame.AFF_ACK_AUTH)
        f.setReqID(self.reqId)
        f.setSerialNo(self.getSerialNo())
        f.setUserIp(self.userIp)
        f.genAuthenticator(None, self.sharedSecret)
        self.doSendReq(f)

    def sendTimeout(self):
        f = Portal_Frame(portalFrame.REQ_LOGOUT)
        f.setReqID(self.reqId)
        f.setSerialNo(self.getSerialNo())
        f.setErrorCode(1)
        f.setUserIp(self.userIp)
        f.genAuthenticator(None, self.sharedSecret)
        self.doSendReq(f)

    def parseChallengeAck(self, reqFrame, ackFrame):
        # print "serino", frame.getSerialNo()
        # print "reqID %x " % frame.getReqID()
        # if ackData is None:
        #     print "challenge Ack not received"
        #     return STAT_CHALLENGE_TIMEOUT
        #
        #
        #
        # ackFrame = Portal_Frame()
        # ackFrame.receiveSome(ackData)

        if ackFrame is None:
            print "challenge Ack not received"
            return STAT_CHALLENGE_TIMEOUT

        ret = ackFrame.validateAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        if ret is False:
            print "challenge Ack validate failed"
            return STAT_FAILED

        errCode = ackFrame.getErrorCode()

        if errCode == CODE_CONNECTED:
            print "client alreay authed"
            return STAT_AUTH_DONE

        if errCode != CODE_SUCCESS:
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
        reqFrame = Portal_Frame(portalFrame.REQ_CHALLENGE)
        reqFrame.setSerialNo(self.genSerialNo())
        #reqFrame.setSerialNo(self.debugGenSerialNo())

        reqFrame.setUserIp(self.userIp)
        reqFrame.genAuthenticator(None, self.sharedSecret)

        self.doSendReq(reqFrame)
        #ackFrame = self.waitAckPkt(ACK_CHALLENGE, TIMEOUT_CHALLENGE)
        ackFrame = self.doReceiveAck(TIMEOUT_CHALLENGE)
        ret = self.parseChallengeAck(reqFrame, ackFrame)
        return ret

    def parseAuthAck(self, reqFrame, ackFrame):

        if ackFrame is None:
            print "auth ack not received"
            return STAT_AUTH_TIMEOUT

        ret = ackFrame.validateAuthenticator(reqFrame.getAuthenticator(), self.sharedSecret)
        if ret is False:
            print "auth Ack validate failed"
            return STAT_FAILED

        errCode = ackFrame.getErrorCode()

        if errCode == CODE_CONNECTED:
            print "client alreay authed"
            return STAT_SUCCESS

        if errCode == CODE_SUCCESS:
            return STAT_SUCCESS
        else:
            print "failed errcode = ", errCode
            return STAT_FAILED

    def doPapAuthReq(self):
        reqId = self.reqId
        usrName = self.usrName
        usrPass = self.password

        nameAttr = Portal_Attr()
        nameAttr.genUserNameAttr(usrName)

        papPassAttr = Portal_Attr()
        papPassAttr.genPapPassAttr(usrPass)

        reqFrame = Portal_Frame(portalFrame.REQ_AUTH)
        reqFrame.setUserIp(self.userIp)
        reqFrame.setSerialNo(self.genSerialNo())
        reqFrame.setAuthPapType()
        reqFrame.setReqID(reqId)
        reqFrame.appendAttr(nameAttr)
        reqFrame.appendAttr(papPassAttr)

        print "send auth req, self.userIp = %x"%self.userIp

        reqFrame.genAuthenticator(None, self.sharedSecret)

        self.doSendReq(reqFrame)
        ackFrame = self.doReceiveAck(TIMEOUT_AUTH)
       #ackFrame = self.waitAckPkt(ACK_AUTH, TIMEOUT_AUTH)
        # if newFrame is not None:
        #     # newFrame.dumpAll()
        #     # print "getAuthenticator:", [buffer(newFrame.getAuthenticator())[:]]
        ret = self.parseAuthAck(reqFrame, ackFrame)

        print "doPapAuthReq ret = ", ret
        return ret


    def doChapAuthReq(self):
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

        reqFrame = Portal_Frame(portalFrame.REQ_AUTH)
        reqFrame.setUserIp(self.userIp)
        reqFrame.setSerialNo(self.genSerialNo())
        reqFrame.setReqID(reqId)
        reqFrame.appendAttr(nameAttr)
        reqFrame.appendAttr(chapPassAttr)

        print "send auth req, self.userIp = %x"%self.userIp

        reqFrame.genAuthenticator(None, self.sharedSecret)

        self.doSendReq(reqFrame)
        #ackFrame = self.waitAckPkt(ACK_AUTH, TIMEOUT_AUTH)
        ackFrame = self.doReceiveAck(TIMEOUT_AUTH)
        # if newFrame is not None:
        #     # newFrame.dumpAll()
        #     # print "getAuthenticator:", [buffer(newFrame.getAuthenticator())[:]]

        ret = self.parseAuthAck(reqFrame, ackFrame)
        return ret


class PortalPacketReceiver (threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)

        self.address = ('0.0.0.0', int(port))
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.address)
        self.clients = {}

    def run(self):
        #print "Starting " + "PortalPacketReceiver \n"
        #threadLock.acquire()
        #threadLock.release()class myThread (threading.Thread):
        self.doReceive()

    def handleData(self, pktData):
        #print "pktData:", [pktData]
        pkt = Portal_Frame()
        pkt.receiveSome(pktData)
        client = self.getClient(pkt.userIp)
        if client:
            client.clientWakeup(pkt)

    def getClient(self, userIp):
        if self.clients.has_key(userIp):
            client = self.clients[userIp]
            return client
        else:
            print "not found client ip :", userIp

    def doReceive(self):
        ready = select.select([self.udpSocket], [], [], None)
        packetCnt = 0
        #if ready[0]:
        while True:
            try:
                data = self.udpSocket.recv(4096)
                packetCnt += 1
                print "total packets= ", packetCnt
                self.handleData(data)
            except:
                print sys.exc_info()
                print "\n\n\n xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                return None
            # else:
            #     print "\n######### receive timeout #######\n"
            #     return None


    def addClient(self, client):
        self.clients[client.userIp] = client

        print "reciever : all client:", self.clients

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
