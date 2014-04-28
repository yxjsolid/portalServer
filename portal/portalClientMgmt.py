__author__ = 'xyang'
from portalClient import *
import threading


class portalClientMgmt():
    def __init__(self, config):
        self.config = config
        self.allAcObj = {}
        pass

    def getGetClientDic(self):

        clientDic = {}

        clientList = []
        for  client in self.testGetAllClients():
            clientList.append({"acIp":client.serverIpStr, "userIp":client.userIpStr, "userName":client.usrName})
        clientDic = {"allClients":clientList}
        return clientDic


    def testGetAllClients(self):
        clients = []
        for ac in self.allAcObj:
            for clientKey in self.allAcObj[ac]:
                client = self.allAcObj[ac][clientKey]
                clients.append(client)

        return clients


    def clientDoAll(self, func):
        for ac in self.allAcObj:
            for clientKey in self.allAcObj[ac]:
                client = self.allAcObj[ac][clientKey]
                func(client)

    def dumpAllClientsObj(self):
        for  client in self.testGetAllClients():
            print (client.serverIpStr, client.userIpStr, client.usrName)

    def dumpAllClients(self):
        print self.allAcObj, "len:", len(self.allAcObj)
        for ac in self.allAcObj:
            print "AC:", ac
            for client in self.allAcObj[ac]:
                print "\t client:", client

    def doPortalAuth(self, wlanAcName, userIp, userName, password):
        acIp = self.getAcIpFromWlanAcname(wlanAcName)
        client = self.getPortalClient(acIp, userIp)

        self.dumpAllClients()

        ret = client.doClientAuth(userName, password)
        if ret is STAT_SUCCESS:
            return True
        else:
            self.removeClient(acIp, userIp)
            self.dumpAllClients()
            return False

    def doPortalLogoutByAcIp(self, acIp, userIp):
        client = self.getPortalClient(acIp, userIp)
        client.doLogout()
        self.removeClient(acIp, userIp)

    def doPortalLogoutByAcName(self, wlanAcName, userIp):
        acIp = self.getAcIpFromWlanAcname(wlanAcName)
        self.doPortalLogoutByAcIp(acIp, userIp)

    def removeClient(self, acIp, userIp):
        userIpStr = userIp.encode("utf8")
        acIpStr = acIp.encode("utf8")
        self.allAcObj[acIpStr].pop(userIpStr)

        if len(self.allAcObj[acIpStr]) == 0:
            self.allAcObj.pop(acIpStr)

        pass

    def getPortalClient(self, acIpStr, userIpStr):
        userIpStr = userIpStr.encode("utf8")
        acIpStr = acIpStr.encode("utf8")
        portalPort = self.config.portalPort
        isPap = self.config.isPap
        version = self.config.portalVersion
        secret = self.config.portalSecret

        if not self.allAcObj.has_key(acIpStr):
            self.allAcObj[acIpStr] = {}
        if not self.allAcObj[acIpStr].has_key(userIpStr):
            client = portalClient(userIpStr, acIpStr, portalPort, version, isPap, secret)
            self.allAcObj[acIpStr][userIpStr] = client
        else:
            client = self.allAcObj[acIpStr][userIpStr]

        return client

    def getAcIpFromWlanAcname(self, wlanacname):
        wlanacname = "".join(wlanacname.split('.'))
        wlanacname = [ wlanacname[x*3:x*3+3] for x in range(4)]
        wlanacname = map(lambda x:str(int(x)), wlanacname)
        wlanacIp = ".".join(wlanacname)
        return wlanacIp


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
