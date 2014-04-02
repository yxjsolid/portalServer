#include<stdio.h>
#include<openssl/md5.h>
#include<string.h>

unsigned char data1[] = {0x70, 0x61, 0x73, 0x73, 0x77, 0x6f, 0x72, 0x64};

unsigned char data2[] = {0x4f, 0x70, 0x61, 0x73, 0x73, 0x77, 0x6f, 0x72, 0x64, 0x21, 0xc2, 0xd5, 0x4a, 0x3e, 0x29, 0x6f, 0x44, 0xd2, 0xe9, 0xe9, 0x5, 0xee, 0x94, 0x2f, 0x99};
int main( int argc, char **argv )
{
	unsigned char md[16];
	int i;
	char tmp[3]={'\0'},buf[33]={'\0'};
	MD5_CTX ctx;

	printf("data1 len = %d \n", sizeof(data1));
	MD5(data1,sizeof(data1),md);

#if 0

	MD5_Init(&ctx);
	MD5_Update(&ctx,data1,sizeof(data1));
	MD5_Final(md,&ctx);
#endif	

	for (i = 0; i < 16; i++)
	{
		sprintf(tmp,"%2.2x",md[i]);
		strcat(buf,tmp);
	}
	printf("%s\n",buf);



	printf("data1 len = %d \n", sizeof(data2));
	MD5(data2,sizeof(data2),md);

#if 0

	MD5_Init(&ctx);
	MD5_Update(&ctx,data1,sizeof(data1));
	MD5_Final(md,&ctx);
#endif	

	memset(buf, 0 , 33);

	for (i = 0; i < 16; i++)
	{
		sprintf(tmp,"%2.2x",md[i]);
		strcat(buf,tmp);
	}
	printf("%s\n",buf);

	
	return 0;
}