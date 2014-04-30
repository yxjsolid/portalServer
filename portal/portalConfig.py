
class myPortalServerCfg():
    def __init__(self):
        self.logoutPopup = True
        self.logo = "static/sonicwall.gif"
        self.portalPort = "2000"
        self.isPap = 1
        self.portalVersion = 2
        self.portalSecret = "shared"
        self.webServerPort = 8080
        self.mgmtPort = 8888

    def dumpJsonData(self):
        cfgDic = {}
        cfgDic['Port'] = self.webServerPort
        cfgDic['authMethod'] = self.isPap
        cfgDic['version'] = self.portalVersion
        cfgDic['secret'] = self.portalSecret.encode("utf8")

        return cfgDic