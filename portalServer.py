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


    def doSendReq(self, frame):
        try:

            print "send data:", frame.getFrameData()

            self.udpSocket.sendto(frame.getFrameData(), self.server)			##Send packets
        except KeyboardInterrupt:									##On Ctrl+C, print new line and break
            ##os.system('cls')
            print '\x0D'

        newFrame = self.doReceive()
        newFrame.dumpAll()
        return newFrame

    def doChallenge(self):
        frame = Portal_Frame(portalProtocol.REQ_CHALLENGE)

        print "%x" % frame.serialNo

        newFrame = self.doSendReq(frame)
        self.receiveChallengeAck(newFrame)

    def receiveChallengeAck(self, frame):
        print "serino", frame.getSerialNo()
        print "reqID %x " % frame.getReqID()

        attr = frame.getAttr(ATTR_CHALLENGE)
        if attr:
            challenge = attr.getAttrData()
            print "receiveChallengeAck", challenge
        else:
            raise ValueError

        self.doAuthReq(frame.getReqID(), testUser, testPass, challenge)
        pass


    def doAuthReq(self, reqId, usrName, usrPass, challenge):
        nameAttr = Portal_Attr()
        nameAttr.genUserNameAttr(usrName)

        reqtmp = c_ushort(reqId)
        reqIdBuff = (c_ubyte * 2)()
        memmove(addressof(reqIdBuff), addressof(reqtmp), 2)

        print "reqtmp" ,reqtmp
        print "reqIdBuff", reqIdBuff[0]
        print "reqIdBuff", reqIdBuff[1]

        chapPassAttr = Portal_Attr()
        chapPassAttr.genChapPassAttr(reqIdBuff[1], usrPass, challenge)


        authReq = Portal_Frame(portalProtocol.REQ_AUTH)
        authReq.genSerialNo()
        authReq.setReqID(reqId)
        authReq.appendAttr(nameAttr)
        authReq.appendAttr(chapPassAttr)


        newFrame = self.doSendReq(authReq)

        pass




if __name__ == '__main__':
    port = 50100
    serverIp = "10.103.12.6"
    myIp = '10.103.12.152'


    client = portalClient(myIp, serverIp, port)

    client.doChallenge()

    print "test"