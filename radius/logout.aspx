<%@ Page Language="VB" Debug="true" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.Net" %>
<%@ Import Namespace="System.IO" %>
<%@ Import Namespace="System.Xml" %>
<%@ Import Namespace="System.Text" %>
<%@ Import Namespace="System.Security" %>
<%@ Import namespace="System.Security.Cryptography.X509Certificates"%>

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

Dim sessionId as String
Dim mgmtBaseUrl as String
Dim eventId as String = "&eventId=1"

'Grab the code and the session lifetime from the generator page
Sub Page_Load(src as Object, e as EventArgs)
	sessionId=Request.QueryString("sessId")
	mgmtBaseUrl=Request.QueryString("mgmtBaseUrl")
	sessTimer=Request.QueryString("sessTimer")


	'Use the override class in myvars.aspx to accept untrusted certificates from the SonicWALL
	'This is necessary for the POST to the SonicWALL authorizing the LHM session.
	System.Net.ServicePointManager.CertificatePolicy = New acceptAllCerts

	'When the page loads, make the loggedIn span visible
	loggedIn.Visible=True
	loggedOut.Visible=False

	Me.Button1.Attributes.Add("OnClick", "self.close()")

End Sub

'The Logout button
Sub btnSubmit_Click(Sender As Object, E As EventArgs)

	'Let the user know that we are setting up the session, just in case it takes more than a second
	LHMResult.Text = "Authorizing session. Please wait."

	'The LHM cgi on the SonicWALL - this does not change
	Dim loginCgi as String = "externalGuestLogoff.cgi"
	
	'Assemble the data to post back to the SonicWALL to authorize the LHM session
	Dim loginParams as String = "sessId=" & sessionId & eventId
	
	'Combine mgmtBaseUrl from the original redirect with the login cgi
	Dim postToSNWL as String = mgmtBaseUrl & loginCgi

	'Convert the loginParams to a well behaved byte array
	Dim byteArray As Byte() = Encoding.UTF8.GetBytes(loginParams)
	
	Try
		'Make the loggedOut span visible
		loggedIn.Visible=False
		loggedOut.Visible=True
		
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
		Dim codePath as String = "SonicWALLAccessGatewayParam/LogoffReply/ResponseCode"
		
		'Response.Write(snwlResponse.SelectSingleNode(codePath).InnerXml)
		
		'Response code 150 - Logout Succeeded
		If snwlResponse.SelectSingleNode(codePath).InnerXml = "150" 
			LHMResult.Text = "<br><b><font color=""green"">Your session has been logged out.<br><br>Thank you for using LHM Guest Services.</font></b>"

		'Response code 251 - Bad HMAC.
		ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "251"
			LHMResult.Text = "<br><b><font color=""red"">Session logout failed:</font></b> The request failed message authentication. Sorry for the inconvenience. Please close and relaunch your browser to try again."

		'Response code 253 - Invalid SessionID.
		ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "253"
			LHMResult.Text = "<br><b><font color=""red"">Session logout failed:</font></b> The request failed to match a known session identity. Sorry for the inconvenience. Please close and relaunch your browser to try again."

		'Response code 254 - Invalid CGI.
		ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "254"
			LHMResult.Text = "<br><b><font color=""red"">Session logout failed:</font></b> The request was missing an essential parameter. Sorry for the inconvenience. Please close and relaunch your browser to try again."

		'Response code 255 - Internal Error.
		ElseIf snwlResponse.SelectSingleNode(codePath).InnerXml = "255"
			LHMResult.Text = "<br><b><font color=""red"">Session logout failed:</font></b> The request failed due to an unspecified error. Sorry for the inconvenience. Please close and relaunch your browser to try again."

		End If

		'Close the streams
		dataStream.Close()
		snwlReply.Close()

		'If there is some asp.net error trying to talk to the SonicWALL, print it in the same color as the background.
		Catch ex as Exception
			catchError.Text = "<font color=""9CBACE"">" & ex.ToString & "</font>"
			LHMResult.Text = "<br><b><font color=""red"">Session logout failed:</font></b> The request failed due to an unspecified error. Sorry for the inconvenience. Please close and relaunch your browser to try again. If the problem persists, please notify an attendant."
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
	font-size: 10pt;
	background-color:#006699;
}

tr.smalltext {
	font-size: 8pt;
}

.button {
	border: 1px solid #000000;
	background-color: #ffffff;
	font-size: 8pt;
}
</STYLE>

<HTML>
<HEAD>
<TITLE>LHM Logout Page</TITLE>

<SCRIPT LANGUAGE="Javascript"> 

//'Javascript Seconds Countdown Timer
var SecondsToCountDown = <%= sessTimer%>;
var originalTime=" ";

function CountDown() 
{ 
	clockStr="";

	dayStr=Math.floor(SecondsToCountDown/86400)%100000
	if(dayStr>0){
		if(dayStr>1){
			dayStr+=" days ";
		} else dayStr+=" day ";
		clockStr=dayStr;
	}
	hourStr=Math.floor(SecondsToCountDown/3600)%24
	if(hourStr>0){
		if(hourStr>1){
			hourStr+=" hours ";
		} else hourStr+=" hour ";
		clockStr+=hourStr;
	}
	minuteStr=Math.floor(SecondsToCountDown/60)%60
	if(minuteStr>0){
		if(minuteStr>1){
			minuteStr+=" minutes ";
		} else minuteStr+=" minute ";
		clockStr+=minuteStr;
	}
	secondStr=Math.floor(SecondsToCountDown/1)%60
	if(secondStr>0){	
		if(secondStr>1){
			secondStr+=" seconds ";
		} else secondStr+=" second ";
		clockStr+=secondStr;
	}

	if(SecondsToCountDown > 0)
	{
		--SecondsToCountDown;
	}

	if(originalTime.length < 2)
	{
		originalTime = clockStr;
	}

	// Make sure the form is still there before trying to set a value
	if(document.frmValidator){
		document.frmValidator.originalTime.value = originalTime;
		document.frmValidator.countdown.value = clockStr;
	}	
	
	setTimeout("CountDown()", 1000);
	if(SecondsToCountDown == 0)
	{ 
		document.frmValidator.countdown.value = "Session Expired"; 
	} 
} 

//'Disable right-click so that the window doesn't get refreshed since the countdown is clientside.
document.oncontextmenu = disableRightClick;
function disableRightClick()
{
  return false;
}

//'Disable F5 key, too, on IE at least.
function noF5()
{
	var key_f5 = 116;        
	if (key_f5==event.keyCode)
	{
		event.keyCode=0;
		return false;
	}
	return false;
}

document.onkeydown=noF5
document.onmousedown=disableRightClick

</SCRIPT> 

</HEAD>

<BODY onload='CountDown()'>
<span id="loggedIn" runat="server">
<form id="frmValidator" runat="server">
<table width="100%" border="0" cellpadding="2" cellspacing="0">
	<tr class="heading">
		<td colspan=2 align="center">&nbsp</td>
	</tr>
	<tr class="heading">
		<td colspan=2 align="center"><font color="white"><b>SonicWALL LHM Logout Window</b></font></td>
	</tr>
	<tr class="heading">
		<td colspan=2 align="center">&nbsp</td>
	</tr>
	<tr class="smalltext"><td><br></td></tr>
	<tr class="smalltext">
		<td>Original Session Time:</td>
		<td><asp:textbox width=250 id="originalTime" runat="server" /></td>
	</tr>
	<tr class="smalltext">
		<td>Remaining Session Time:</td>
		<td><asp:textbox width=250 id="countdown" runat="server" /></td>
	</tr>
	<tr class="smalltext">
		<td colspan=2><br>You may use this window to manually logout your session at any time, or you may safely close this window if you prefer to let your session timeout automatically.</font></td>
	</td>
	<tr>
		<td colspan=2><center><asp:button id="btnSubmit" class="button" text="  Logout  " onClick="btnSubmit_Click" runat="server" /></center></td>
	</tr>
</table>
</form>
</span>

<span id="loggedOut" runat="server">
<form id="logout" runat="server">
<table width="100%" border="0" cellpadding="2" cellspacing="0">
	<tr class="heading">
		<td colspan=2 align="center">&nbsp</td>
	</tr>
	<tr class="heading">
		<td colspan=2 align="center"><font color="white"><b>SonicWALL LHM Logout Window</b></font></td>
	</tr>
	<tr class="heading">
		<td colspan=2 align="center">&nbsp</td>
	</tr>
	<tr>
		<td><asp:Label id=LHMResult runat="server" /></td>
	</tr>
	<tr>
		<td><asp:Label id=catchError runat="server" /></td>
	</tr>
	<tr><td><br></td></tr>
	<tr>
		<td><center><asp:button id="Button1" class="button" text="  Close  " runat="server" /></center></td>
	</tr>
</table>
</form>
</span>

</BODY>
</HTML>