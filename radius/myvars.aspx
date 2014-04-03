<script language="VB" runat="server">

'Set the logoutPopup window flag - 0 = no popup, 1 = popup
'The use of the logoutPopup in this script is encouraged because the login event is non-exclusive.
Dim logoutPopup as String = "1"

'Set the RADIUS server IP or Name
'Make sure the LHM Server is setup as client on the RADIUS Server
Dim myRadiusServer as String = "10.50.165.2"

'Set the RADIUS Port
Dim myRadiusPort as String = "1812"

'Set the RADIUS Secret
Dim myRadiusSecret as String = "password"

'Set the default LHM Session Timeout (for when no attributes is retrieved)
Dim sessTimer as String = "3600"

'Set the default LHM Idle Timeout (for when no attributes is retrieved)
Dim idleTimer as String = "300"

'Set the secret for use with optional HMAC auth, as configured in the Extern Guest Auth config on the SonicWALL
Dim strHmac as String = "password"

'Set the digest method for the HMAC, either MD5 or SHA1
Dim hmacType as String = "MD5"
'Dim hmacType as String = "SHA1"

'Set the logo image to use
Dim logo as String = "sonicwall.gif"

'------------------------End of Configurable Settings-------------------------
</script>