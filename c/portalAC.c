
#include "portalProtocol.h"


#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h> /*for struct sockaddr_in*/

int handlePortalPacket(uint8 *pktIn, int inPktSize, uint8 *pSendBuffer, int *pSendLen);

#define DEST_IP   "10.103.12.152"
#define DEST_PORT 50100
#define MYPORT  50100


int doSend(int fd, struct sockaddr_in * addr_srv, uint8 *send_buf, int dataLen)
{
	if(sendto(fd,send_buf, dataLen, 0, (struct sockaddr*)addr_srv, sizeof(struct sockaddr_in)) <0)
	{
		printf("sendto() error");
		return 0;
	}
}


int setServerAddr(struct sockaddr_in * addr_srv)
{
	memset(addr_srv,0,sizeof(struct sockaddr_in));
	addr_srv->sin_family = AF_INET;
	addr_srv->sin_port = htons(DEST_PORT);

	if(inet_aton(DEST_IP, &addr_srv->sin_addr)<0)
	{
		printf("inet_aton() error");
		return 0;
	}
	return 1;

}

int doSocket()
{
	int res;
	int sockfd;
	struct sockaddr_in dest_addr;
	struct sockaddr_in server_addr;
	char pktIn[2048];

	
	sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (sockfd == -1) 
	{
		printf("socket() error");
		return 0;
	}

	dest_addr.sin_family = AF_INET;
	//dest_addr.sin_port = htons(DEST_PORT);
	//dest_addr.sin_addr.s_addr = inet_addr(DEST_IP);

	dest_addr.sin_port = htons(MYPORT);
	dest_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	bzero(&(dest_addr.sin_zero), 8);  

	res = bind(sockfd, (struct sockaddr*)&dest_addr, sizeof(struct sockaddr));
	if (res == -1)
	{
		printf("bind() error");
		return 0;
	}


	setServerAddr(&server_addr);

	while(1)
	{
		uint8 sendBuffer[1024];
		int sendLen = 0;
		
		res = recv(sockfd, pktIn, 2048, 0);
		if (res == -1)
		{
			printf("recv() error");
			return 0;
		}
		printf("received data = %d \n", res);

		memset(sendBuffer, 0, sizeof(sendBuffer));
		handlePortalPacket(pktIn, res, sendBuffer, &sendLen);


		doSend(sockfd, &server_addr, sendBuffer, sendLen);
	}
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

PortalAttr * createChallengeAttr(void)
{
	uint8 challenge[16];
	int i = 0;

	for( i = 0; i < 16; i++)
	{
		challenge[i] = 0xaa + i;
	}
	
	return createAttr(ATTR_CHALLENGE, challenge, 16);
}


int handleChallengeReq(uint8 *pktIn, int pktSize, uint8 *sendBuffer, int *sendLen)
{
	
	PortalFrame *reqPkt = NULL;
	PortalFrame *ackPkt = NULL;
	PortalAttr *pAttr = NULL;

	if (!sendBuffer)
	{
		printf("%s --> sendBuffer is null \n", __FUNCTION__);
		return 0;
	}

	reqPkt = (PortalFrame *)pktIn;
	ackPkt = (PortalFrame *)sendBuffer;


	ackPkt->type = ACK_CHALLENGE;
	ackPkt->serialNo = reqPkt->serialNo;
	ackPkt->reqID = 0x1234;
	ackPkt->attrNum = 1;
	
	pAttr = createChallengeAttr();

	if (!pAttr)
	{
		return 0;
	}
	memcpy(ackPkt->attr, pAttr, pAttr->attrLen);
	*sendLen = sizeof(PortalFrame) + pAttr->attrLen;

	SWFREE(pAttr);

	return 1;
}

int handlePortalPacket(uint8 *pktIn, int inPktSize, uint8 *pSendBuffer, int *pSendLen)
{
	PortalFrameType pktType;

	if (inPktSize < sizeof(PortalFrame))
	{
		printf(" data size error\n");
		return 0;
	}

	pktType = ((PortalFrame *)pktIn)->type;
	switch(pktType)
	{
		case REQ_CHALLENGE:
			handleChallengeReq(pktIn, inPktSize, pSendBuffer, pSendLen);
			break;
	}
	

	return 1;


}


int main()
{
	PortalFrame frame;
	int res;
  	int sockfd;
  	struct sockaddr_in dest_addr;


	doSocket();


}




