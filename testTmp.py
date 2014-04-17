__author__ = 'xyang'

import socket
import struct
from portalProtocol import *
print "\n\n\n"

userIp = "18.52.86.120"

#socket.ntohl(struct.unpack("I",socket.inet_aton(str(ip)))[0])

ipaton = socket.inet_aton(userIp)

print "socket.inet_aton(str(ip)): %r" % ipaton
ipunpack = struct.unpack("I",ipaton)

print "uppack:%x " % ipunpack
print "uppack[0]:%x " % ipunpack[0]
print "socket.ntohl %x " % socket.ntohl(ipunpack[0])

ip = socket.ntohl(ipunpack[0])

reqFrame = Portal_Frame(REQ_CHALLENGE)
reqFrame.setUserIp(ip)
print "reqFrame.ip = %x"%reqFrame.userIp

data = reqFrame.getFrameData()
for i in data:
    print "%x "%ord(i)
