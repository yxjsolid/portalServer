import pyrad.packet
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import random, socket,sys
import binascii

def test1():

    srv = Client(server="10.103.12.152", secret="password",
               dict=Dictionary("dictionary"))

    # req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
    #                          User_Name="wichert", NAS_Identifier="localhost")

    req=srv.CreateAuthPacket(
                             User_Name="test")
    #req["User-Password"]=req.PwCrypt("password")


    chapIdent = binascii.a2b_hex("5a")
    chappass = binascii.a2b_hex("8c214d319abb57cbdde133bc50897755")
    chall =    binascii.a2b_hex("91b2d5aa755c86cd8e7e52f1bb899b19")

# chapId:5a
# chapPassword: 8c214d319abb57cbdde133bc50897755
# chall: 91b2d5aa755c86cd8e7e52f1bb899b19



    req["CHAP-Password"] = chapIdent + chappass
    req["CHAP-Challenge"] = chall



    print req

    reply=srv.SendPacket(req)
    if reply.code==pyrad.packet.AccessAccept:
        print "access accepted"
    else:
        print "access denied"

    print "Attributes returned by server:"
    for i in reply.keys():
        print "%s: %s" % (i, reply[i])








test1()
