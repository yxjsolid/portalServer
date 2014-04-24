__author__ = 'xyang'
import sys
import socket
import threading
import select
import time

class myClient(threading.Thread):
    def __init__(self, serverIp, port, name, data):
        threading.Thread.__init__(self)
        self.server = (serverIp, int(port))
        self.name = name
        self.data = data
        self.socketList = []
        #self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        pass

    def doSendReq(self, data):
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socketList.append(self.udpSocket)

        try:
            # print "send data:", frame.getFrameData()
            self.udpSocket.sendto(data, self.server)
            print self.udpSocket.fileno()
        except KeyboardInterrupt:
            ##os.system('cls')
            print sys.exc_info()
            print '\x0D'

    def doReceive(self):
        #ready = select.select([self.udpSocket], [], [], 100)
        #ready = select.select([self.udpSocket], [], [], 100)
        packetCnt = 0
        #if ready[0]:

        #time.sleep(4)

        while True:

            ready = select.select(self.socketList, [], [], None)

            for sock in ready[0]:
                try:
                    data = sock.recv(4096)
                    packetCnt += 1

                    print self.name, ":got data-->", data
                except:
                    print sys.exc_info()
                    print "\n\n\n xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    return None
                # else:






    def run(self):

        #data = "%s"

        for i in range(10):
            #self.doSendReq(self.data)
            self.doSendReq("%s"%i)
        self.doReceive()


if __name__ == '__main__':
    port = 50100
    serverIp = "10.103.12.154"
    myIp = '10.103.12.152'
    userip = "3.3.3.4"
    data1 = "12345678"



    # for i in range(100000):
    #     udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #
    #     #udpSocket.bind(('0.0.0.0', i))
    #     print udpSocket.fileno(),  i
        #help(udpSocket)


    client1 = myClient(serverIp, port, "client1", data1)
    client1.start()

    # data2 = "abcdefg"
    # client2 = myClient(serverIp, port, "client2", data2)
    # client2.start()