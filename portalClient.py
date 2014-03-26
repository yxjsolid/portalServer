import sys
import socket
import binascii
import os
from time import sleep

strIP="127.0.0.1"		##Multicast (destination) IP to which data will be sent
intPort="50100"			##UDP port pair with the destination IP
strData=binascii.unhexlify('280000006d08000003f49451016f4e1531000000000401460800000000000001005e010548000001')  ##Data to send to multicast address
strData=binascii.unhexlify('280000006d08000003f49451016f4e1531000000000401460800000000000001005e010548000001')
intSleepTime=100		##The script will wait for X milliseconds before next packet is sent; the default is 100ms.
intTTL=5				##IP header TTL
intPacketCount=0		##Basic counter of packets sent
strStdOut=""			##Used to send messages to stdout


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)					##Create socket
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, intTTL)		##Socket type is Multicast


try:
    sock.sendto (strData, (strIP, int(intPort)))			##Send packets
    intPacketCount = intPacketCount + 1						##Increment packet counter
    strStdOut = "Packets Sent: " + str(intPacketCount)		##Stdout message
    sys.stdout.write(strStdOut + '\x08'*len(strStdOut))		##Update stdout
    sleep(intSleepTime)										##Wait before sending next packet

except KeyboardInterrupt:									##On Ctrl+C, print new line and break
    ##os.system('cls')
    print '\x0D'