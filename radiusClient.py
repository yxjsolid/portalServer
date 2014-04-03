import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import binascii


class portalRadiusClient():
    def __init__(self, serverIn, secretIn):

        self.client = Client(server=serverIn, secret=secretIn,
                             dict=Dictionary("dictionary"))
        return

    def doAuth(self, userName, identStr, challengeStr, chapPassStr):
        print "ident:", identStr
        print "ident:", binascii.b2a_hex(identStr)
        print "challengeStr:", binascii.b2a_hex(challengeStr), type(challengeStr)
        print "chapPassStr:", binascii.b2a_hex(chapPassStr)

        req = self.client.CreateAuthPacket(User_Name=userName)

        req.authenticator = challengeStr
        req["CHAP-Challenge"] = challengeStr
        req["CHAP-Password"] = identStr + chapPassStr

        reply = self.client.SendPacket(req)

        if reply.code == pyrad.packet.AccessAccept:
            print "access accepted"
            ret = True
        else:
            print "access denied"
            ret = False



        print "Attributes returned by server:"
        for i in reply.keys():
            print "%s: %s" % (i, reply[i])

        return ret


if __name__ == '__main__':
    serverIp = "10.103.12.150"
    secret = "password"

    radClient = portalRadiusClient(serverIp, secret)

    name = "test"
    id = binascii.a2b_hex("5a")
    chall = binascii.a2b_hex("91b2d5aa755c86cd8e7e52f1bb899b19")
    chappass = binascii.a2b_hex("8c214d319abb57cbdde133bc50897755")



    radClient.doAuth(name, id, chall, chappass)
