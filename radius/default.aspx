<%@ Page Language="VB" Debug="true" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Xml" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Math" %>
<%@ Import Namespace="System.DirectoryServices" %>
<%@ Import Namespace="System.Collections" %>
<%@ Import Namespace="System.Security" %>
<%@ Import namespace="System.Security.Cryptography.X509Certificates"%>
<%@ Assembly name="System.DirectoryServices, Version=1.0.3300.0, Culture=neutral,PublicKeyToken=b03f5f7f11d50a3a"%>

<!-- #INCLUDE file="myvars.aspx" -->

<script language="VB" runat="server">

'This class allows SSL certs signed by unknown CAs to be accepted.
'This is necessary for the POST to the SonicWALL authorizing the LHM session.
Public Class acceptAllCerts
	Implements System.Net.ICertificatePolicy
	Public Function CheckValidationResult(ByVal srvPoint As ServicePoint, _
	ByVal cert As X509Certificate, ByVal request As WebRequest, ByVal problem As Integer) _
	   As Boolean Implements ICertificatePolicy.CheckValidationResult
		Return True
	End Function
End Class

'Sample LHM redirect querystring:
'http://127.0.0.1/peak_html/default.aspx?sessionId=0b712fd83b9f5313db5af1cea6b1004f&ip=10.50.165.231&mac=00:0e:35:bd:c9:37&ufi=0006b11184300&mgmtBaseUrl=https://10.50.165.193:4043/&clientRedirectUrl=https://10.50.165.193:444/&req=http%3A//www.google.com/ig

Dim ip as String
Dim sessionId as String
Dim mac as String
Dim ufi as String
Dim mgmtBaseUrl as String
Dim clientRedirectUrl as String
Dim req as String
Dim hmac as String
Dim customCode as String

Sub Page_Load(src as Object, e as EventArgs)

	LHMResult.Text=""
	catchError.Text=""
	authResult.Text=""

	ip=Request.QueryString("ip")
	sessionId=Request.QueryString("sessionId")
	mac=Request.QueryString("mac")
	ufi=Request.QueryString("ufi")
	mgmtBaseUrl=Request.QueryString("mgmtBaseUrl")
	clientRedirectUrl=Request.QueryString("clientRedirectUrl")
	req=Request.QueryString("req")
	hmac=Request.QueryString("hmac")
	customCode=Request.QueryString("cc")

	'customCode grabs the "cc=" querystring value sent by the SonicWALL. This allows you to use the same
	'page (e.g. this page) for the "Session Expiration" (?cc=2), "Idle Timeout" (?cc=3) and "Max Sessions" (?cc=4) page. 
	If customCode <> "" Then
		Select Case customCode
		Case "2"
			LHMResult.Text="<br><H3><font color=""red"">Your LHM session has expired. You may try to initiate a new session.</font></H3>"
		Case "3"
			LHMResult.Text="<br><H3><font color=""red"">You have exceeded your idle timeout. Please log back in.</font></H3>"
		Case "4"
			LHMResult.Text="<br><H3><font color=""red"">The maximum number of sessions has been reached. Please try again later.</font></H3>"
		End Select
	End If

	'Use the override class in myvars.aspx to accept untrusted certificates from the SonicWALL
	'This is necessary for the POST to the SonicWALL authorizing the LHM session.
	System.Net.ServicePointManager.CertificatePolicy = New acceptAllCerts

	'Note - the routine below for handling the hmac requires the use of the SonicSSL.dll and libeay.dll libraries.
	'The DLL must be copied to the IIS server, and the SonicSSL dll must be registered with "regsvr32 sonicssl.dll"
	If hmac <> "" Then
	
		'SonicWALL URL Encode routine is different from Microsoft - this is the SonicWALL method
		req=Replace(req,"%","%25")
		req=Replace(req,":","%3A")
		req=Replace(req," ","%20")
		req=Replace(req,"?","%3F")
		req=Replace(req,"+","%2B")
		req=Replace(req,"&","%26")
		req=Replace(req,"=","%3D")

		Dim strHmacText as String
		Dim objCrypto as Object
		Dim strHmacGenerated
		Dim loginError as String

		'Initialize the Crypto object
		objCrypto = Server.CreateObject("SonicSSL.Crypto")

		'The text to be encoded 
		strHmacText = sessionId & ip & mac & ufi & mgmtBaseUrl & clientRedirectUrl & req

		'Calculate the hash with a key strHmac, the return value is a string converted form the output sha1 binary.
		'The hash algorithm (MD5 or SHA1) is configured in myvars and in the Extern Guest Auth config on the SonicWALL
		If hmacType = "MD5" Then
			strHmacGenerated = objCrypto.hmac_md5(strHmacText, strHmac)
		Else
			strHmacGenerated = objCrypto.hmac_sha1(strHmacText, strHmac)
		End If

		If strHmacGenerated <> hmac Then
			Dim hmacFail as String
			hmacFail = "<font color=""red"">The HMAC failed validation. Please notify an attendant.</font><br><br>"
			hmacFail+="<font color=""9CBACE"">Received HMAC: " & hmac & "<br>Calculated HMAC: " & strHmacGenerated & "<br>"
			hmacFail+="Make sure the digest functions on the SonicWALL and LHM server match.<br>"
			hmacFail+="Also make sure the shared secret on the SonicWALL and myvars match</font>"
			catchError.Text=hmacFail
		End If
			
	End If

End Sub

sub OnBtnClearClicked (Sender As Object, e As EventArgs)
	txtName.Text = ""
	txtPassword.Text = ""
	authResult.Text=""
	LHMResult.Text=""
	catchError.Text=""
end sub

Sub btnSubmit_Click(Sender As Object, E As EventArgs)

	'Try RADIUS Auth
	Try
		
		Response.Buffer = true

		Dim objWShell as Object
		Dim objCmd as Object
		Dim strPResult as String
		Dim strStatus as String
		
		objWShell = CreateObject("WScript.Shell") 
		objCmd = objWShell.Exec(server.mappath("WinRadiusClient.exe") & " -u " & txtName.Text & " -p " & txtPassword.Text & " -s " & myRadiusServer & " -port " & myRadiusPort & " -secret " & myRadiusSecret) 
		strPResult = objCmd.StdOut.Readall() 
		objCmd = nothing
		objWShell = nothing 
 
		if InStr(strPResult,"Access accepted")>0 then 
			strStatus = "succeeded" 
			authResult.Text="<font color=""green""><b>Credentials Accepted.</b></font><br>Session Lifetime: " & round(sessTimer/60) & " minutes.<br>Idle Timer: " & round(idleTimer/60) & " minutes."
		
		'Auth succeeded - move on to LHM Auth
		LHM()
		
		Else
			strStatus = "failed" 
			authResult.Text="<font color=""Red""><b>Credentials Rejected.</b></font><br>Please enter a valid username and password. " 
		End If
 
		'Uncomment to see full results from RADIUS Client
		'response.write ("Authentication has " & strStatus) 
		'response.write (".<br>" & replace(strPResult,vbCrLf,"<br>")) 

		Catch ex as Exception
			catchError.Text = "<font color=""9CBACE"">" & ex.ToString & "</font>"
	End Try

End Sub
	
Sub LHM()

		'Let the user know that we are setting up the session, just in case it takes more than a second
		LHMResult.Text = "Authorizing session. Please wait."

		'The LHM cgi on the SonicWALL - this does not change
		Dim loginCgi as String = "externalGuestLogin.cgi"
		
		'Assemble the data to post back to the SonicWALL to authorize the LHM session
		Dim loginParams as String = "sessId=" & sessionId & "&userName=" & Server.URLEncode(txtName.Text) & "&sessionLifetime=" & sessTimer & "&idleTimeout=" & idleTimer
		
		'Combine mgmtBaseUrl from the original redirect with the login cgi
		Dim postToSNWL as String = mgmtBaseUrl & loginCgi

		'Convert the loginParams to a well behaved byte array
		Dim byteArray As Byte() = Encoding.UTF8.GetBytes(loginParams)
		
		Try
			'Create the webrequest to the SonicWALL
			Dim toSNWL as WebRequest = WebRequest.Create(postToSNWL)

			'Calculate the length of the byte array
			toSNWL.ContentLength = byteArray.Length

			'Set the method for the webrequest to POST
			toSNWL.Method = "POST"

			'Set the content type
			toSNWL.ContentType = "application/x-www-form-urlencoded"

			'Open the request stream
			Dim dataStream As Stream = toSNWL.GetRequestStream()

			'Write the byte array to the request stream
			dataStream.Write(byteArray, 0, byteArray.Length)

			'Close the Stream object
			dataStream.Close()

			'Get the response
			Dim snwlReply As WebResponse = toSNWL.GetResponse()

			'Display the status - looking for 200 = OK.
			'Response.Write(CType(snwlReply, HttpWebResponse).StatusCode)
			
			'Grab the response and stuff it into an xml doc for possible review
			Dim snwlResponse as XmlDocument = New XmlDocument() 
			snwlResponse.Load(snwlReply.GetResponseStream())

			'Set the xPath to the SNWL reply, and get the response
			Dim codePath as String = "SonicWALLAccessGatewayParam/AuthenticationReply/ResponseCode"
			
			'Response.Write(snwlResponse.SelectSingleNode(codePath).InnerXml)
			
			'Response code 50 - Login Succeeded
			If snwlResponse.SelectSingleNode(codePath).InnerXml = "50" 

				'Do we want to provide a logout popup window?
				If logoutPopup = "1" Then
					'Popup hack using Javascript for logout window
					Dim sb As New System.Text.StringBuilder()
					sb.Append("<script language='javascript'>")
					sb.Append("window.open('logout.aspx?sessId=")
					sb.Append(Server.URLEncode(CStr(sessionId)))
					sb.Append("&mgmtBaseUrl=")
					sb.Append(Server.URLEncode(CStr(mgmtBaseUrl)))
					sb.Append("&sessTimer=")
					sb.Append(Server.URLEncode(CStr(sessTimer)))
					sb.Append("','logOut','toolbar=no,")
					sb.Append("addressbar=no,menubar=no,")
					sb.Append("width=400,height=250');")
					sb.Append("<")
					sb.Append("/")
					sb.Append("script>")
					RegisterStartupScript("stp", sb.ToString)
				End If
				
				LHMResult.Text = "<br><b><font color=""green"">Session authorized:</font></b> You may now go to the URL you originally requested: <a target=""_blank"" href=""" & req & """>" & req & "</a>"

			'Response code 51 - Session Limit Exceeded
			ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "51"
				LHMResult.Text = "<br><b><font color=""red"">Session Limit Reached:</font></b> The maximum number of guest session has been reached. Sorry for the inconvenience. Please close and relaunch your browser to try again."
			
			'Response code 100 - Login Failed.
			ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "100"
				LHMResult.Text = "<br><b><font color=""red"">Session creation failed:</font></b> Your session cannot be created at this time. Sorry for the inconvenience. Please close and relaunch your browser to try again."

			'Response code 251 - Bad HMAC.
			ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "251"
				LHMResult.Text = "<br><b><font color=""red"">Session creation failed:</font></b> The request for authorization failed message authentication. Sorry for the inconvenience. Please close and relaunch your browser to try again."

			'Response code 253 - Invalid SessionID.
			ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "253"
				LHMResult.Text = "<br><b><font color=""red"">Session creation failed:</font></b> The request for authorization failed to match a known session identity. Sorry for the inconvenience. Please close and relaunch your browser to try again."

			'Response code 254 - Invalid CGI.
			ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "254"
				LHMResult.Text = "<br><b><font color=""red"">Session creation failed:</font></b> The request for authorization was missing an essential parameter. Sorry for the inconvenience. Please close and relaunch your browser to try again."

			'Response code 255 - Internal Error.
			ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "255"
				LHMResult.Text = "<br><b><font color=""red"">Session creation failed:</font></b> The request for authorization failed due to an unspecified error. Sorry for the inconvenience. Please close and relaunch your browser to try again."

			End If

			'Close the streams
			dataStream.Close()
			snwlReply.Close()

			'If there is some asp.net error trying to talk to the SonicWALL, print it in the same color as the background.
			Catch ex as Exception
				catchError.Text = "<font color=""9CBACE"">" & ex.ToString & "</font>"
				LHMResult.Text = "<br><b><font color=""red"">Session creation failed:</font></b> The request for authorization failed due to an unspecified error. Sorry for the inconvenience. Please close and relaunch your browser to try again. If the problem persists, please notify an attendant."
		End Try
End Sub
</script>

<STYLE>
body {
  font-size: 10pt;
  font-family: verdana,helvetica,arial,sans-serif;
  color:#000000;
  background-color:#9CBACE;
}

tr.heading {
  background-color:#006699;
}

.button {
	border: 1px solid #000000;
	background-color: #ffffff;
}
</STYLE>

<HTML>
<HEAD>
<TITLE>LHM ADAuth Script</TITLE>
</HEAD>

<BODY>
<form id="frmValidator" runat="server">

<table width="100%" border="0" cellpadding="2" cellspacing="0">
	<tr class="heading">
		<td colspan=3 align="center"><font color="white">&nbsp</td>
	</tr>
	<tr class="heading">
		<td width="50%" valign="center"><font color="white"><b>RADIUS LHM Authentication</b></font></td>
		<td><center><img width="216" height="51" src="<%= logo %>"></center></td>
		<td width="50%" align="right" valign="center"><font color="white"><b>Powered by SonicWALL LHM</b>&nbsp</font></td>
	</tr>
	<tr class="heading">
		<td colspan=3 align="center"><font color="white">&nbsp</td>
	</tr>
</table>

<table width="90%" border="0" cellpadding="2" cellspacing="0">
	<tr>
		<td><b>Wecome <%= ip%> to SonicWALL's LHM Basic RADIUS Authenticator.</b><br><br>Please enter your username and password to obtain secure guest internet access.<br>
		</td>
	</tr>
</table>
<table width="100%" border="0" cellpadding="2" cellspacing="0">
	<tr class="heading">
		<td colspan=3 align="center"><font color="white">Using RADIUS Server: <%=myRadiusServer%></td>
	</tr>
</table>
<table width="100%" border="0" cellpadding="2" cellspacing="0">
	<tr>
		<br>
		<td width="20%">Enter your login name:</td>
		<td width="20%"><asp:TextBox id="txtName" runat="server" /></td>
		<td><asp:RequiredFieldValidator id="valTxtName" ControlToValidate="txtName" ErrorMessage="Please enter your name." runat="server" /></td>
	</tr>
	<tr>
		<td width="20%">Enter your password:</td>
		<td width="20%"><asp:TextBox id="txtPassword" textmode="password" runat="server" /></td>
		<td><asp:RequiredFieldValidator id="valTxtPassword" ControlToValidate="txtPassword" ErrorMessage="Please enter your password." runat="server" /></td>
	</tr>
	<tr>
		<td></td><td><asp:Label id=authResult runat="server" />&nbsp</td>
	</tr>
	<tr>
		<td></td>
		<td><asp:button id="btnSubmit" class="button" text="  Submit  " onClick="btnSubmit_Click" runat="server" />
		&nbsp&nbsp
		<asp:button id="btnClear" class="button" text=" Clear All " CausesValidation="False" onClick="OnBtnClearClicked" runat="server" />
		</td>
	</tr>
	<tr>
		<td colspan=2><asp:Label id=LHMResult runat="server" /></td>
	</tr>
	<tr>
		<td colspan=2><asp:Label id=catchError runat="server" /></td>
	</tr>
</table>
</form>
</BODY>
</HTML>