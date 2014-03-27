from ctypes import *
import random
import binascii

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




class Portal_Frame(Structure):
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

    _dictSerialNo_ ={}

    def __init__(self, type=REQ_CHALLENGE):
        Structure.__init__(self)
        print "sizeof(Portal_Frame)", sizeof(Portal_Frame)

        self.ver = 2
        self.type = type
        self.genSerialNo()
        return

    def testFame(self):
        self.ver = 1
        print [buffer(self)[:]]
        self.testSetAuthenticator()
        print [buffer(self)[:]]

    def send(self):
        return buffer(self)[:]

    def receiveSome(self, bytes):
        fit = min(len(bytes), sizeof(self))
        memmove(addressof(self), bytes, fit)


    def testSetAuthenticator(self):
        bytesa = "abce"
        print sizeof(self.authenticator)
        memset(addressof(self.authenticator), 0, 16)
        fit = min(len(bytesa), sizeof(self.authenticator))
        memmove(addressof(self.authenticator), bytesa, fit)

    def dump(self):
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




    def genSerialNo(self):
        while True:
            serialNo = random.randint(1, 0xffff)
            print serialNo

            if str(serialNo) in self.__class__._dictSerialNo_:
                print "hasKey"
            else:
                self.__class__._dictSerialNo_[str(serialNo)] = 1
                self.setSerialNo(serialNo)

                break

        pass

    def setSerialNo(self, serialNo):
        self.serialNo = serialNo
        pass


frame = Portal_Frame()
frame.dump()

frame.genSerialNo()

