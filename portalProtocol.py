#encoding: utf-8
from ctypes import *
import random
import hashlib
import binascii
import socket

# typedef struct PortalFrame
# {
# uint8 ver;
# uint8 type;
# uint8 chap;
# uint8 rsvd;
# uint16 serialNo;
# uint16 reqID;
# uint32 userIp;
# uint16 userPort;
# uint8 errcode;
# uint8 attrNum;
# uint8 authenticator[16];
# uint8 attr[0]
# }PortalFrame;
REQ_CHALLENGE = 0x01
ACK_CHALLENGE = 0x02
REQ_AUTH = 0x03
ACK_AUTH = 0x04
REQ_LOGOUT = 0x05
ACK_LOGOUT = 0x06
AFF_ACK_AUTH = 0x07
NTF_LOGOUT = 0x08
REQ_INFO = 0x09
ACK_INFO = 0x0a

CODE_SUCCESS = 0
CODE_REJECT = 1
CODE_CONNECTED = 2
CODE_NEED_RETRY = 3
CODE_FAILED = 4


class Portal_Frame(BigEndianStructure):
#class Portal_Frame(Structure):
    _fields_ = [("ver",         c_ubyte),
                ("type",        c_ubyte),
                ("chap",        c_ubyte),
                ("rsvd",        c_ubyte),
                ("serialNo",    c_ushort),
                ("reqID",       c_ushort),
                ("userIp",      c_uint),
                ("userPort",    c_ushort),
                ("errcode",     c_ubyte),
                ("attrNum",     c_ubyte),
                ("authenticator", c_ubyte * 16)]


    _dictReqID_ ={}

    def __init__(self, type=REQ_CHALLENGE):
        Structure.__init__(self)
        #print "sizeof(Portal_Frame)", sizeof(Portal_Frame)

        self.ver = 2
        self.type = type

        self.attrList = []
        #self.genSerialNo()

        #print self.reqID

        return

    def testFame(self):
        self.ver = 1
        print [buffer(self)[:]]
        self.testSetAuthenticator()
        print [buffer(self)[:]]

    def getFrameData(self):

        #socket.htonl()
        #socket.htons()
        data = buffer(self)[:]
        for attr in self.attrList:
            data += attr.getData()

        return data

    def receiveSome(self, bytes):
        if len(bytes) < sizeof(self):
            raise IndexError

        memmove(addressof(self), bytes, sizeof(self))
        attrBytes = bytes[sizeof(self):]
        self.parseAttr(attrBytes)

    def parseAttr(self, attrBytes):
        attList = []

        while len(attrBytes) > 0:
            attr = Portal_Attr()
            attr.receiveSome(attrBytes)
            # attr.dumpAll()

            #dataTotalLen -= attr.getAttrLen()
            attrBytes = attrBytes[attr.getAttrLen():]
            attList.append(attr)


        if len(attList) != self.attrNum:
            raise IndexError

        self.attrList = attList

        pass


    def testSetAuthenticator(self):
        bytesa = "abce"
        print sizeof(self.authenticator)
        memset(addressof(self.authenticator), 0, 16)
        fit = min(len(bytesa), sizeof(self.authenticator))
        memmove(addressof(self.authenticator), bytesa, fit)

    def dumpAll(self):
        for elem in self._fields_:
            elemName = elem[0]
            elemObj = getattr(self, elemName)
            dumpFormat = "%-10s:0x%x"

            if isinstance(getattr(self, elem[0]), Array):
                arrayDump = "0x"
                for byte in elemObj[:]:
                    arrayDump += "%02x" % byte
                print "%-10s:" % elemName, arrayDump
            else:
                print dumpFormat %(elemName, elemObj)


    def dumpAttr(self):

        pass

    def isAuthenticatorMatch(self, auth1, auth2):
        # print "auth1:", [buffer(auth1)[:]]
        # print "auth2:", [buffer(auth2)[:]]


        if buffer(auth1)[:] == buffer(auth2)[:]:
            # print "Match"
            return True
        else:
            # print "mismatch"
            return False


    def validateAuthenticator(self, authIn, secret):
        authIdSave = self.getAuthenticator()
        self.genAuthenticator(authIn, secret)

        if self.isAuthenticatorMatch(authIdSave, self.getAuthenticator()):
            return True
        else:
            return False

    def resetAuthenticator(self):
        memset(addressof(self.authenticator), 0, sizeof(self.authenticator))

    def getAuthenticator(self):
        out = (c_ubyte * 16)()
        memmove(out, self.authenticator, 16)
        return out

    def genAuthenticator(self, authIn, secret):
        self.resetAuthenticator()
        if authIn is not None:
            memmove(addressof(self.authenticator), authIn, sizeof(self.authenticator))

        frameData = self.getFrameData()

        m = hashlib.md5()
        m.update(frameData)
        m.update(secret)
        digest = m.digest()

        #print "digets1",  m.hexdigest()
        memmove(addressof(self.authenticator), digest, sizeof(self.authenticator))




    def getErrorCode(self):
        return self.errcode

    def getReqID(self):
        return self.reqID

    def getSerialNo(self):
        return self.serialNo

    def genReqId(self):
        while True:
            reqID = random.randint(1, 0xffff)
            if str(reqID) in self.__class__._dictReqID_:
                print "hasKey"
            else:
                self.__class__._dictReqID_[str(reqID)] = 1
                self.setReqID(reqID)
                break
        pass

    def setUserIp(self, userIp):
        self.userIp = userIp

    def setSerialNo(self, serialNo):
        self.serialNo = serialNo
        pass

    def setReqID(self, reqId):
        self.reqID = reqId

    def setErrorCode(self, code):
        self.errcode = code

    def appendAttr(self, attr):
        self.attrNum += 1
        self.attrList.append(attr)

    def getAttr(self, attType):
        for attr in self.attrList:
            if attr.isType(attType):
                return attr

        return None

    def genChallengeAck(self):
        attr = Portal_Attr()
        challenge = attr.genChallengeAttr()
        self.appendAttr(attr)
        return challenge




ATTR_USERNAME = 0x1
ATTR_PASSWORD = 0x2
ATTR_CHALLENGE = 0x3
ATTR_CHAP_PASSWORD = 0x4

class Portal_Attr(Structure):
    _fields_ = [("attrType",    c_ubyte),
                ("attrLen",     c_ubyte)]

    def __init__(self):
        Structure.__init__(self)
        self.attrData = None
        return

    def isType(self, type):
        return self.attrType == type

    def getAttrLen(self):
        return self.attrLen

    def genUserNameAttr(self, usrName):
        self.attrType = ATTR_USERNAME
        self.attrLen = len(usrName) + 2
        self.attrData = usrName
        # print "self.attrData %r"%self.attrData, self.attrData
        # print "####### name = %r"%usrName, usrName, type(usrName)

    def genChapPassMD5(self, chapId, password, challenge):
        data1 = buffer(challenge)[:]
        
        m = hashlib.md5()
        m.update(chr(chapId))
        m.update(password)
        m.update(data1)
        digest = m.hexdigest()
        # print "chapId:%x" % chapId
        # print "chapPassword:", digest
        # print "chall:", binascii.b2a_hex(buffer(challenge)[:])

        digest = binascii.a2b_hex(digest)
        return digest

    def genChapPassAttr(self, chapId, password, challenge):
        self.attrType = ATTR_CHAP_PASSWORD
        self.attrLen = 16 + 2
        self.attrData = self.genChapPassMD5(chapId, password, challenge)

    def genRandomBytes(self, size):
        output = (c_ubyte * size)()
        for i in range(size):
            rByte = random.randint(0, 0xff)
            output[i] = c_ubyte(rByte)

        return output

    def genChallengeAttr(self):
        self.attrType = ATTR_CHALLENGE
        self.attrLen = 16 + 2
        self.attrData = self.genRandomBytes(16)
        return self.attrData

    def getData(self):
        data = buffer(self)[:] + buffer(self.attrData)[:]
        return data

    def getAttrData(self):
        return self.attrData

    def receiveSome(self, bytes):
        if len(bytes) < sizeof(self):
            raise IndexError

        memmove(addressof(self), bytes, sizeof(self))

        if len(bytes) < self.attrLen:
            raise IndexError
        dataBytes = bytes[sizeof(self): self.attrLen]
        self.parseAttrData(dataBytes)

    def parseAttrData(self, dataBytes):
        self.attrData = (c_ubyte * (self.attrLen - 2))()
        memmove(addressof(self.attrData), dataBytes, self.attrLen - 2)


    def genAttr(self, type):

        pass

    def dumpAll(self):
        for elem in self._fields_:
            elemName = elem[0]
            elemObj = getattr(self, elemName)
            dumpFormat = "%-10s:0x%x"

            if isinstance(getattr(self, elem[0]), Array):
                arrayDump = "0x"
                for byte in elemObj[:]:
                    arrayDump += "%02x" % byte
                print "%-10s:" % elemName, arrayDump
            else:
                print dumpFormat %(elemName, elemObj)


        print "data: %r " % buffer(self.attrData)[:]


if __name__ == '__main__':

    # frame = Portal_Frame()
    # frame.dump()
    # frame.genSerialNo()

    attr = Portal_Attr()
    attr.genChallengeAttr()
