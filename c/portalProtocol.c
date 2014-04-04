#include "portalProtocol.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h> /*for struct sockaddr_in*/
#include <stdio.h>
#include <openssl/md5.h>
#include <string.h>

#define TEST_SECRET "shared"
uint16 lastReqID = 0;
uint8 lastChallenge[16];


// TODO: need take care of reqid and challenge
void saveReqId(uint16 reqID)
{
	lastReqID = reqID;
}

void saveChallenge(uint8 *pChallin)
{
	memcpy(lastChallenge, pChallin, 16);
}


void dump(uint8 *data, int len)
{
	int i = 0;

	for ( i = 0; i < len ; i++)
	{
		if ( i && i%16 == 0)
			printf("\n");
		printf("%02x ", data[i]);

		
	}
	printf("\ndump end \n");

}

// TODO: Gen random rqeID
uint16 genReqId(void)
{
	uint16 reqid = 0x1234;

	saveReqId(reqid);


	return reqid;
}

int validateAuthenticator(PortalFrame *pkt, int pktTotalLen, uint8 *authIn, uint8 *secret)
{
	MD5_CTX ctx;
	uint8 md[16];
	uint8 authCodeSave[16];

	memcpy(authCodeSave, pkt->authenticator, 16);
	memset(pkt->authenticator, 0, 16);
	if (authIn)
	{
		memcpy(pkt->authenticator, authIn, 16);
	}

	MD5_Init(&ctx);
	MD5_Update(&ctx, pkt, pktTotalLen);
	MD5_Update(&ctx, secret, strlen(secret));
	MD5_Final(md,&ctx);

	if ( memcmp(authCodeSave, md, 16))
	{
		printf("authenticator miss match \n");
		return 0;
	}

	//recover the authentictor into req pkt
	memcpy(pkt->authenticator, authCodeSave, 16);

	return 1;
}


int setPacketAuthenticator(PortalFrame *pkt, int pktTotalLen, uint8 *authIn, uint8 *secret)
{
	MD5_CTX ctx;
	uint8 md[16];
	PortalAttr *pAttr;
	int attrTotalLen = 0;
	int i = 0;
	

	pAttr = pkt->attr;
	for (i = 0; i < pkt->attrNum; i++)
	{
		//printf("attr type: %d \n", pAttr->attrType);
		//printf("attr len: %d \n\n", pAttr->attrLen);

		attrTotalLen += pAttr->attrLen;
		pAttr = pkt->attr + attrTotalLen;
	}
	if (pktTotalLen != sizeof(PortalFrame)  + attrTotalLen)
	{
		printf("%s --> error! pktDatasize not match %d -- %d \n", __FUNCTION__, pktTotalLen, sizeof(PortalFrame)  + attrTotalLen);
	}



	memset(pkt->authenticator, 0, 16);
	if (authIn)
	{
		memcpy(pkt->authenticator, authIn, 16);
	}
	



	MD5_Init(&ctx);
	MD5_Update(&ctx, pkt, pktTotalLen);
	MD5_Update(&ctx, secret, strlen(secret));
	MD5_Final(md,&ctx);

	memcpy(pkt->authenticator, md, 16);

#if 0
	printf("gen authenticator :\n");
	dump(md, 16);
#endif
	
	return 1;
}

PortalAttr * getAttrFromPkt(PortalFrame *pkt, PortalAttrType type)
{
	int attrNum = pkt->attrNum;
	PortalAttr * pAttr = NULL;
	int i = 0;
	pAttr = pkt->attr;

	for (i = 0; i < pkt->attrNum; i++)
	{
		if (pAttr->attrType == type)
		{
			return pAttr;
		}

		pAttr = (PortalAttr *)((uint8 *)pAttr + pAttr->attrLen);
	}

	return NULL;
}

PortalAttr * createAttr(PortalAttrType type, uint8 *pData, int dataSize)
{
	PortalAttr *pAttr;

	pAttr = SWMALLOC(dataSize + sizeof(PortalAttr));
	if (!pAttr)
	{
		printf("%s --> out memory \n", __FUNCTION__);
		return NULL;
	}

	pAttr->attrType = type;
	pAttr->attrLen = dataSize + sizeof(PortalAttr);
	memcpy(pAttr->attrData, pData, dataSize);

	return pAttr;
}


// TODO: Gen random challenge
PortalAttr * createChallengeAttr(void)
{
	uint8 challenge[16];
	int i = 0;

	for( i = 0; i < 16; i++)
	{
		challenge[i] = 0xaa + i;
	}


	saveChallenge(challenge);
	
	
	return createAttr(ATTR_CHALLENGE, challenge, 16);
}


void setAuthAckPkt(PortalFrame *reqPkt, PortalFrame *ackPkt, PORTAL_ERRCODE errCode)
{
	ackPkt->type = ACK_AUTH;
	ackPkt->serialNo = reqPkt->serialNo;
	ackPkt->reqID = reqPkt->reqID;
	ackPkt->errcode = errCode;
}



int handleAFFAckAuth(PortalFrame *reqPkt, int pktSize, uint8 *sendBuffer, int *sendLen)
{
	PortalAttr *pAttr = NULL;

	if (!sendBuffer)
	{
		printf("%s --> sendBuffer is null \n", __FUNCTION__);
		return 0;
	}

	if (!validateAuthenticator(reqPkt, pktSize, NULL, TEST_SECRET))
	{
		printf("authenticator validate failed in logout req \n");
		return 0;
	}

	printf("peer auth success \n");
	
}



int handleLogoutReq(PortalFrame *reqPkt, int pktSize, uint8 *sendBuffer, int *sendLen)
{
	PortalAttr *pAttr = NULL;

	if (!sendBuffer)
	{
		printf("%s --> sendBuffer is null \n", __FUNCTION__);
		return 0;
	}

	if (!validateAuthenticator(reqPkt, pktSize, NULL, TEST_SECRET))
	{
		printf("authenticator validate failed in logout req \n");
		return 0;
	}

	if (reqPkt->errcode)
	{
		printf("peer timout msg received\n");
	}
	else
	{
		printf("peer logout msg recieved\n");
	}


}



int handleAuthReq(PortalFrame *reqPkt, int pktSize, uint8 *sendBuffer, int *sendLen)
{
	PortalFrame *ackPkt = NULL;
	PortalAttr *pAttr = NULL;

	if (!sendBuffer)
	{
		printf("%s --> sendBuffer is null \n", __FUNCTION__);
		return 0;
	}


	if (!validateAuthenticator(reqPkt, pktSize, NULL, TEST_SECRET))
	{
		printf("authenticator validate failed in auth req \n");
		return 0;
	}

	
	printf("\n\n get auth req, reqid = %x \n", reqPkt->reqID);
	printf("ChapI = %x \n", ((uint8 *)&(reqPkt->reqID))[0]);

	pAttr =  getAttrFromPkt(reqPkt, ATTR_USERNAME);
	
	if (pAttr)
	{
		uint8 username[256];
		memset(username, 0, 256);
		memcpy(username, pAttr->attrData, pAttr->attrLen - 2);
		printf("username = %s \n",username);
	}
	else
	{
		printf("error ! username not found \n");
	}


	pAttr =  getAttrFromPkt(reqPkt, ATTR_CHAP_PASSWORD);
	
	if (pAttr)
	{
		printf("dump chapPass:");
		dump(pAttr->attrData, pAttr->attrLen - 2);
	}
	else
	{
		printf("error ! chap password not found \n");
	}


	// TODO: implement radius auth process here

	

	ackPkt = (PortalFrame *)sendBuffer;
	//setAuthAckPkt(reqPkt, ackPkt, ERR_FAILED);
	setAuthAckPkt(reqPkt, ackPkt, ERR_SUCCESS);

	*sendLen = sizeof(PortalFrame);
	setPacketAuthenticator(ackPkt, *sendLen, reqPkt->authenticator, TEST_SECRET);

	return 1;
}








int handleChallengeReq(PortalFrame *reqPkt, int pktSize, uint8 *sendBuffer, int *sendLen)
{
	PortalFrame *ackPkt = NULL;
	PortalAttr *pAttr = NULL;

	if (!sendBuffer)
	{
		printf("%s --> sendBuffer is null \n", __FUNCTION__);
		return 0;
	}

	if (!validateAuthenticator(reqPkt, pktSize, NULL, TEST_SECRET))
	{
		printf("authenticator validate failed in challenge req\n");
		return 0;
	}


	
	ackPkt = (PortalFrame *)sendBuffer;


	//memset(ackPkt, 0xff, sizeof(PortalFrame));

	ackPkt->type = ACK_CHALLENGE;
	ackPkt->serialNo = reqPkt->serialNo;
	ackPkt->reqID = genReqId();
	ackPkt->attrNum = 1;
	
	pAttr = createChallengeAttr();

	if (!pAttr)
	{
		return 0;
	}
	memcpy(ackPkt->attr, pAttr, pAttr->attrLen);
	*sendLen = sizeof(PortalFrame) + pAttr->attrLen;

	setPacketAuthenticator(ackPkt, *sendLen, reqPkt->authenticator, TEST_SECRET);

	SWFREE(pAttr);

	return 1;
}




int handlePortalPacket(uint8 *pktIn, int inPktSize, uint8 *pSendBuffer, int *pSendLen)
{
	PortalFrameType pktType;
	PortalFrame *reqPkt = NULL;
	int ret = 0;

	if (inPktSize < sizeof(PortalFrame))
	{
		printf(" data size error\n");
		return 0;
	}

	reqPkt = (PortalFrame *)pktIn;
	pktType = reqPkt->type;


	// TODO: validate packet type and reqid
	
	switch(pktType)
	{
		case REQ_CHALLENGE:
			printf("\n\n ###########  receive challenge req \n");
			ret = handleChallengeReq(reqPkt, inPktSize, pSendBuffer, pSendLen);
			break;

		case REQ_AUTH:
			printf("\n\n ###########  receive auth req \n");
			ret = handleAuthReq(reqPkt, inPktSize, pSendBuffer, pSendLen);
			break;


		case REQ_LOGOUT:
			printf("\n\n ###########  receive logout req \n");
			ret = handleLogoutReq(reqPkt, inPktSize, pSendBuffer, pSendLen);
			break;


		case AFF_ACK_AUTH:
			printf("\n\n ###########  receive AFF ACK AUTH \n");
			ret = handleAFFAckAuth(reqPkt, inPktSize, pSendBuffer, pSendLen);
			break;
			
	}
	

	return ret;


}




