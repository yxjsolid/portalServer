__author__ = 'xyang'
import sys
import socket

class myServer():
    def __init__(self, port):
        self.myaddr = ("0.0.0.0", int(port))
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSocket.bind(self.myaddr)
        pass

    def doSend(self, data, addr):
        print "send back to:", addr
        self.udpSocket.sendto(data, addr)

    def doReceive(self):
        count = 0
        while True:
            data, addr = self.udpSocket.recvfrom(2048)
            print "got data:",data

            if count > 5:
                self.doSend(data, addr)

            count += 1

            if not data:
                print "client has exist"
                break


if __name__ == '__main__':
    port = 50100


    server = myServer(port)
    server.doReceive()
