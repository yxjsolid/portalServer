# -*- coding: utf-8 -*-
import web
from web import form
from portalClientMgmt import *

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
        self.render = web.template.render('tmp/', globals={"portalCfg":myPortalCfg()})

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
        clientMgmt.doPortalLogout(wlanacname, userIp)
        return self.render.logout(web.ctx.fullpath, 0, 0)

class defaultPage():
    def __init__(self):
        self.render = web.template.render('tmp/', globals={"portalCfg":myPortalCfg()})

    def GET(self):
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


if __name__ == "__main__":
    urls = (
        '/portalDefault.html', defaultPage,
        '/logout.html', logoutPage,
    )
    global portalCfg
    global udpSocket
    global receiver
    global clientMgmt

    portalCfg = myPortalCfg()
    clientMgmt = portalClientMgmt(portalCfg)

    #print globals()

    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()

