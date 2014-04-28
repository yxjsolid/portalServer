__author__ = 'xyang'
import web
from web import form
from portal.portalClientMgmt import *
from serverMain import *
import time
import json

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

    def POST(self):
        # print "post"
        #
        # # print "web.rawinput()", web.rawinput()
        # print "web.input()", web.input()
        # print "web.data()", web.data()
        userIp = web.input().wlanuserip
        wlanacname = web.input().wlanacname
        print "logout userip = ", userIp
        clientMgmt.doPortalLogout(wlanacname, userIp)
        return self.render.logout(web.ctx.fullpath, 0, 0)

class getJsonData:
    def GET(self):
        pyDict = clientMgmt.getGetClientDic()
        web.header('Content-Type', 'application/json')
        return json.dumps(pyDict)

    def POST(self):
        acIp = web.input().acIp
        userIp = web.input().userIp
        clientMgmt.doPortalLogoutByAcIp(acIp, userIp)

        web.header('Content-Type', 'application/json')
        return json.dumps(None)

def launchMain():
    urls = (
        '/', mgmtPage,
        '/getJsonData.json', getJsonData,
    )
    app = MyApplication(urls, globals())
    #app.internalerror = web.debugerror
    #app.run(port=8888)

    webtt = myThread(app, 8888)
    webtt.start()






if __name__ == "__main__":

    global portalCfg
    global clientMgmt

    portalCfg = myPortalCfg()
    clientMgmt = portalClientMgmt(portalCfg)

    #print globals()




    launchMain()
    #
    time.sleep(1)

    launchPortalWeb(clientMgmt)
    print "done"
