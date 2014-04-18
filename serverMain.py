# -*- coding: utf-8 -*-
import web
from web import form
from portalServer import *



myPortalServerIp = "10.103.12.152"

allClients = {}
udpSocket = None

def doLogout(userIp):
    global  allClients
    client = allClients[userIp]

    print client
    client.doLogout()

class myRadiusConfig():
    logoutPopup = True
    #Set the RADIUS server IP or Name
    #Make sure the LHM Server is setup as client on the RADIUS Server
    myRadiusServer = "10.103.12.150"

    #Set the RADIUS Port
    myRadiusPort = "1812"

    #Set the RADIUS Secret
    myRadiusSecret = "password"

    #Set the default LHM Session Timeout (for when no attributes is retrieved)
    sessTimer = "3600"

    #Set the default LHM Idle Timeout (for when no attributes is retrieved)
    idleTimer = "300"

    #Set the secret for use with optional HMAC auth, as configured in the Extern Guest Auth config on the SonicWALL
    strHmac = "password"

    #Set the digest method for the HMAC, either MD5 or SHA1
    hmacType = "MD5"
    #hmacType = "SHA1"
    #Set the logo image to use
    logo = "static/sonicwall.gif"

    ACIP = "10.103.12.158"
    portalPort = "2000"

login = form.Form(
    form.Textbox('txtName'),
    form.Password('txtPassword'),
    form.Textbox('btnSubmit'),
    )

myform = form.Form(
    form.Textbox("boe"),
    form.Textbox("bax",
                 form.notnull,
                 form.regexp('\d+', 'Must be a digit'),
                 form.Validator('Must be more than 5', lambda x:int(x)>5)),
    form.Textarea('moe'),
    form.Checkbox('curly'),
    form.Dropdown('french', ['mustard', 'fries', 'wine']))

class formtest:
    def __init__(self):
        self.render = web.template.render('tmp/')

    def GET(self):
        form = myform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return self.render.formtest(form)

    def POST(self):
        f = myform()
        # print form.d
        # print form.inputs

        print "web.input()", web.input()
        print "web.data()", web.data()
        f.validates()


        print f['french'].value
        print f.d.french

        print f.d

        if not f.validates():
            return self.render.formtest(f)
        else:
            # form.d.boe and form['boe'].value are equivalent ways of
            # extracting the validated arguments from the form.
            return "Grrreat success! boe: %s, bax: %s" % (f.d.boe, f['bax'].value)

def doAuth(userIp, userName, password):

    userName = userName.encode("utf8")
    password = password.encode("utf8")
    userIpStr = userIp.encode("utf8")
    print "userName = %r password = %r" % (userName, password)

    myCfg = myRadiusConfig()
    acip = myCfg.ACIP
    portalPort = myCfg.portalPort

    global udpSocket
    global receiver
    client = portalClient(userIpStr, acip, portalPort, Portal_sharedSecret, receiver)
    receiver.addClient(client)
    ret = client.run(userIpStr, userName, password)



    if ret is STAT_SUCCESS:
        global allClients
        allClients[userIpStr] = client

        return True
    else:
        return False

class logout():
    def __init__(self):
        self.render = web.template.render('tmp/', globals={"radiusCfg":myRadiusConfig()})

    def GET(self):

        print "get"

        print "web.rawinput()", web.ctx.fullpath
        # print "web.input()", web.input()
        print "web.data()", web.data()

        #return self.render.radius(myRadiusConfig())
        return self.render.logout(web.ctx.fullpath, 1, 2400)

    def POST(self):
        print "post"

        # print "web.rawinput()", web.rawinput()
        print "web.input()", web.input()
        print "web.data()", web.data()


        userIp = web.input().wlanuserip
        print "post logout userip = ", userIp


        doLogout(userIp)

        #return self.render.radius(myRadiusConfig())
        return self.render.logout(web.ctx.fullpath, 0, 0)


class index():
    def __init__(self):
        self.render = web.template.render('tmp/', globals={"radiusCfg":myRadiusConfig()})

    def GET(self):

        print "get"

        print "web.rawinput()", web.ctx.fullpath
        # print "web.input()", web.input()
        print "web.data()", web.data()

        #return self.render.radius(myRadiusConfig())
        return self.render.radius(web.ctx.fullpath, None, None)

    def POST(self):
        print "post"

       # print "web.rawinput()", web.rawinput()
        print "web.input()", web.input()
        print "web.data()", web.data()


        f = login()
        if f.validates():
            print f.d
        else:
            raise TypeError

        userName = f.d.txtName
        password = f.d.txtPassword
        userIp = web.input().wlanuserip

        print "usr:%r  pass:%r " %(userName, password)

        ret = doAuth(userIp, userName, password)

        #return self.render.radius(myRadiusConfig())
        userIp = userIp.encode("utf8")
        return self.render.radius(web.ctx.fullpath, ret, userIp)

if __name__ == "__main__":
    urls = (
        '/radius.html', 'index',
        '/logout.html', 'logout',
        '/form.html', "formtest"
    )
    global radiusCfg
    global udpSocket
    global receiver

    receiver = PortalPacketReceiver(2000)
    receiver.start()

    print "aaaaaaaaaaaaaa"
    radiusCfg = myRadiusConfig()

    #print globals()

    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()

