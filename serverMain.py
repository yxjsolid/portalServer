# -*- coding: utf-8 -*-
import web
from web import form
from portal.portalClientMgmt import *

class myPortalCfg():
    logoutPopup = True
    logo = "static/sonicwall.gif"
    portalPort = "2000"
    isPap = 1
    portalVersion = 2
    portalSecret = "shared"

loginForm = form.Form(
    form.Textbox('txtName'),
    form.Password('txtPassword'),
    form.Textbox('btnSubmit'),
    )

class logoutPage():
    def __init__(self):
        self.render = web.template.render('templates/', globals={"portalCfg":myPortalCfg()})

    def GET(self):
        return self.render.logout(web.ctx.fullpath, 1, 2400)

    def POST(self):
        # print "post"
        #
        # # print "web.rawinput()", web.rawinput()
        # print "web.input()", web.input()
        # print "web.data()", web.data()
        userIp = web.input().wlanuserip
        wlanacname = web.input().wlanacname
        print "logout userip = ", userIp
        clientMgmt.doPortalLogoutByAcName(wlanacname, userIp)
        return self.render.logout(web.ctx.fullpath, 0, 0)

class defaultPage():
    def __init__(self):
        global clientMgmt
        self.render = web.template.render('templates/', globals={"portalCfg":myPortalCfg(), "clientMgmt":clientMgmt})

    def GET(self):

        clientMgmt.dumpAllClients()

        return self.render.portalDefault(web.ctx.fullpath, None, None, None,None)

    def POST(self):
        # print "post"
        # print "web.rawinput()", web.rawinput()
        # print "web.input()", web.input()
        # print "web.data()", web.data()

        f = loginForm()
        if f.validates():
           pass
        else:
            raise TypeError

        userName = f.d.txtName
        password = f.d.txtPassword
        userIp = web.input().wlanuserip
        wlanacname = web.input().wlanacname

        print "login: usr:%s  pass:%s " %(userName, password)

        ret = clientMgmt.doPortalAuth(wlanacname, userIp, userName, password)
        userIp = userIp.encode("utf8")
        return self.render.portalDefault(web.ctx.fullpath, ret, userIp, wlanacname, userName)




def launchPortalWeb(clientMgmtin):
    urls = (
        '/portalDefault.html', defaultPage,
        '/logout.html', logoutPage,
    )

    #global clientMgmt


    #print clientMgmt

    #print globals()

    #globals = {"clientMgmt":clientMgmt}

    global clientMgmt
    clientMgmt = clientMgmtin

    app = MyApplication(urls, globals())




    print clientMgmt
    #app.internalerror = web.debugerror
    #app.run(port=8080)

    webtt = myThread(app, 8080)
    webtt.start()


class MyApplication(web.application):
    def __init__(self, mapping=(), fvars={}):
        web.application.__init__(self, mapping, fvars)


    def run(self, port=8080, *middleware):

        #print "global", globals()
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


class myThread (threading.Thread):
    def __init__(self, webApp, port):
        threading.Thread.__init__(self)
        self.webApp = webApp
        self.port = port

    def run(self):
        self.webApp.run(self.port)

if __name__ == "__main__":

    global portalCfg
    global udpSocket
    global receiver
    global clientMgmt

    portalCfg = myPortalCfg()
    clientMgmt = portalClientMgmt(portalCfg)
    launchPortalWeb()


