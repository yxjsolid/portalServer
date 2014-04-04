
typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;

#define SWMALLOC	malloc
#define SWFREE		free


typedef enum
{
	ERR_SUCCESS 	= 0,
	ERR_REJECT 		= 1,
	ERR_CONNECTED 	= 2,
	ERR_NEED_RETRY 	= 3,
	ERR_FAILED 		= 4,
}PORTAL_ERRCODE;






typedef enum
{
	ATTR_USERNAME 		= 0x1,
	ATTR_PASSWORD 		= 0x2,
	ATTR_CHALLENGE 		= 0x3,
	ATTR_CHAP_PASSWORD 	= 0x4
}PortalAttrType;



typedef struct PortalAttr
{
	uint8 attrType;
	uint8 attrLen;
    uint8 attrData[0];
}PortalAttr;



typedef enum
{
	REQ_CHALLENGE 	= 0x01,
	ACK_CHALLENGE 	= 0x02,
	REQ_AUTH 		= 0x03,
	ACK_AUTH 		= 0x04,
	REQ_LOGOUT 		= 0x05,
	ACK_LOGOUT 		= 0x06,
	AFF_ACK_AUTH 	= 0x07,
	NTF_LOGOUT 		= 0x08,
	REQ_INFO 		= 0x09,
	ACK_INFO 		= 0x0a,
}PortalFrameType;

typedef struct PortalFrame
{
	uint8 ver;
	uint8 type;
	uint8 chap;
	uint8 rsvd;
	uint16 serialNo;
	uint16 reqID;
	uint32 userIp;
	uint16 userPort;
	uint8 errcode;
	uint8 attrNum;
    uint8 authenticator[16];
    PortalAttr attr[0];
}PortalFrame;





extern int handlePortalPacket(uint8 *pktIn, int inPktSize, uint8 *pSendBuffer, int *pSendLen);

