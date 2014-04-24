__author__ = 'xyang'
from portalClient import *

class portalClientMgmt():
    def __init__(self, config):
        self.config = config
        self.allAcObj = {}
        pass

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

    def doPortalLogout(self, wlanAcName, userIp):
        acIp = self.getAcIpFromWlanAcname(wlanAcName)
        client = self.getPortalClient(acIp, userIp)
        client.doLogout()

        self.removeClient(acIp, userIp)

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
