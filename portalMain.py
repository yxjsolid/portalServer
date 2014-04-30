from portal.portalMgmtServer import *
from portal.portalWebServer import *
from portal.portalClientMgmt import *
from portal.portalConfig import *

if __name__ == "__main__":

    global serverMgmt
    global portalCfg
    global clientMgmt
    global portalServerThread

    portalCfg = myPortalServerCfg()
    serverMgmt = portalServerMgmt()
    serverMgmt.serverCfg =  portalCfg
    serverMgmt.clientMgmt = portalClientMgmt(serverMgmt.serverCfg)
    serverMgmt.portalServerLaunch()

    time.sleep(0.1)

    launchMain(serverMgmt)