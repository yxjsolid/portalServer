import web
from portalClientMgmt import *
from portalWebServer import *
import time
import json

class portalServerMgmt():
    def __init__(self):
        self.serverCfg = None
        self.clientMgmt = None
        self.serverThread = None

        pass

    def portalServerLaunch(self):
        port = self.serverCfg.webServerPort
        self.serverThread = launchPortalWeb(self, port)
        self.serverThread.start()

    def portalServerStop(self):
        self.serverThread.stop()
        self.serverThread = None
        pass

class mgmtPage():
    def __init__(self):
        self.render = web.template.render('templates/', globals={})

    def GET(self):

        print clientMgmt
        print globals()

        clientMgmt.dumpAllClients()
        clientMgmt.dumpAllClientsObj()

        if globals().has_key("clientMgmt"):
            print "has key"
            print globals()["clientMgmt"]

        return self.render.mgmt(clientMgmt)


class getStatusJson:
    def GET(self):
        pyDict = clientMgmt.getGetClientDic()

        # print portalServerThread

        if serverMgmt.serverThread is not None:
            pyDict['serverStatus'] = 1
        else:
            pyDict['serverStatus'] = 0

        web.header('Content-Type', 'application/json')
        return json.dumps(pyDict)

class configServerJson:
    def POST(self):
        action = web.input().action

        serverCfg = serverMgmt.serverCfg
        if action.encode("utf8") == "startServer":
            serverCfg.isPap = int(web.input().authMethod)
            serverCfg.portalVersion = int(web.input().version)
            serverCfg.portalSecret = web.input().secret.encode("utf8")
            serverCfg.webServerPort = int(web.input().serverPort)
            serverMgmt.portalServerLaunch()

        if action.encode("utf8") == "stopServer":
            serverMgmt.portalServerStop()

        print web.input()
        web.header('Content-Type', 'application/json')
        return json.dumps(None)


class getServerSettingsJson:
    def GET(self):
        pydic =  portalCfg.dumpJsonData()
        web.header('Content-Type', 'application/json')
        return json.dumps(pydic)


class doLogoutJson:
    def POST(self):
        acIp = web.input().acIp
        userIp = web.input().userIp
        clientMgmt.doPortalLogoutByAcIp(acIp, userIp)
        web.header('Content-Type', 'application/json')
        return json.dumps(None)

def launchMain(serverMgmtIn):
    urls = (
        '/', mgmtPage,
        '/getStatusJson.json', getStatusJson,
        '/getServerSettingsJson.json', getServerSettingsJson,
        '/doLogout.json', doLogoutJson,
        '/configServerJson.json', configServerJson,
    )

    global clientMgmt
    global portalCfg
    global serverMgmt
    clientMgmt =  serverMgmtIn.clientMgmt
    portalCfg = serverMgmtIn.serverCfg
    serverMgmt = serverMgmtIn
    app = MyApplication(urls, globals())


    webthread = myThread(app, portalCfg.mgmtPort)
    webthread.start()



if __name__ == "__main__":

    global serverMgmt
    global portalCfg
    global clientMgmt
    global portalServerThread

    portalCfg = myPortalCfg()
    clientMgmt = portalClientMgmt(portalCfg)

    #print globals()
    serverMgmt = portalServerMgmt()
    serverMgmt.serverCfg =  portalCfg
    serverMgmt.clientMgmt = portalClientMgmt(serverMgmt.serverCfg)
    serverMgmt.portalServerLaunch()

    time.sleep(0.1)

    launchMain()

