
typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;


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
    uint8 attr[0]
}PortalFrame;

