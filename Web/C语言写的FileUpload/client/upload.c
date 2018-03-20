#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/md5.h>
//#include <sys/types.h>
#include <unistd.h>
#include <assert.h>
#include <signal.h>
#include <errno.h>
#include "protocol.h"

int my_write(int fd,void *buffer,int length)
{
    int bytes_left = length;
    int bytes_written;

    while(bytes_left>0)
    {
        bytes_written=write(fd,buffer,bytes_left);
        if(bytes_written<=0)
        {
            if(errno==EINTR)
                bytes_written=0;
            else
                return(-1);
        }
        bytes_left-=bytes_written;
        buffer+=bytes_written;
    }
    return(0);
}

int my_read(int fd,void *buffer,int length)
{
    int bytes_left = length;
    int bytes_read;

    bytes_left=length;
    while(bytes_left>0)
    {
        bytes_read=read(fd,buffer, bytes_left);
        if(bytes_read<0)
        {
            if(errno==EINTR)
                bytes_read=0;
            else {
                printf("error in reading: %s\n", strerror(errno));
                return(-1);
            }
        }
        else if(bytes_read==0)
            break;
        bytes_left -= bytes_read;
        buffer += bytes_read;
    }
    return(length-bytes_left);
}

static inline int read_file_into_buf(const char *file, char **buf, long *filesize)
{
    FILE *fp;

    fp = fopen(file, "rb");
    fseek(fp, 0, SEEK_END);
    *filesize = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    *buf = malloc(*filesize);
    if(fread(*buf, 1, *filesize, fp) < *filesize) {
        perror("fread error.\n");
        return -1;
    }
    fclose(fp);
    return 0;
}


static inline void md5checksum(const char *plain, long length, char checksum[33])
{
    unsigned char digest[16];
    MD5_CTX ctx;
    int i;

    MD5_Init(&ctx);
    MD5_Update(&ctx, plain, length);
    MD5_Final(digest, &ctx);

    for(i = 0; i < 16; i++)
        sprintf(&checksum[i*2], "%02x", (unsigned int)digest[i]);
    checksum[32] = '\0';
}


int send_file_info(int sock, unsigned int uid, char checksum[32], long filesize, unsigned int *resume_id)
{
    char buf[LEN_RESUME_TEMPLATE+1] = "";

    snprintf(buf, LEN_RESUME_TEMPLATE+1, RESUME_TEMPLATE, uid, checksum, filesize);
    //printf("===================\n");
    //write(1, buf, LEN_RESUME_TEMPLATE);
    //printf("\n===================\n");
    if(my_write(sock, buf, LEN_RESUME_TEMPLATE) < 0)
        return -1;
    if(my_read(sock, buf, LEN_RESUME_TEMPLATE_ACK) < 0)
        return -1;
    //printf("==================\n");
    //write(1, buf, LEN_RESUME_TEMPLATE_ACK);
    //printf("==================\n");
    if(sscanf(buf, RESUME_TEMPLATE_ACK, resume_id) != 1)
        return -1;
    return 0;
}


int send_chunk_head(int sock, unsigned int chunk_id)
{
    char buf[LEN_CHUNK_HEAD_TEMPLATE+1] = "";

    snprintf(buf, LEN_CHUNK_HEAD_TEMPLATE+1, CHUNK_HEAD_TEMPLATE, chunk_id);
    if(my_write(sock, buf, LEN_CHUNK_HEAD_TEMPLATE) < 0)
        return -1;
    return 0;
}


int send_chunk_body(int sock, char *file_buf, long file_size, unsigned i)
{
    if(i == (file_size + UPLOAD_CHUNK_SIZE - 1) / UPLOAD_CHUNK_SIZE - 1) {
        if(my_write(sock, file_buf + i * UPLOAD_CHUNK_SIZE, file_size%UPLOAD_CHUNK_SIZE) < 0)
            return -1;
        else
            return 0;
    }

    if(my_write(sock, file_buf + i * UPLOAD_CHUNK_SIZE, UPLOAD_CHUNK_SIZE) < 0)
        return -1;
    else
        return 0;
}


int upload(const char *file_name, const char *dest_ip, int port, unsigned int uid)
{
    int sock;
    struct sockaddr_in dest_addr;
    long file_size;
    char *file_buf;
    char checksum[33];
    
    //signal(SIGPIPE, SIG_IGN);

    read_file_into_buf(file_name, &file_buf, &file_size);
    md5checksum(file_buf, file_size, checksum);
    printf("File MD5: %s\n", checksum);
    printf("File Size: %ld\n", file_size);

    unsigned int i, total_chunk_num, reconnect_count, resume_id;
    total_chunk_num = (file_size + UPLOAD_CHUNK_SIZE - 1) / UPLOAD_CHUNK_SIZE;
    printf("Chunk_num: %u\n", total_chunk_num);


    i = reconnect_count = 0;
    while(i < total_chunk_num && reconnect_count < 20) {
        sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP);
        if(sock < 0) {
            perror("socket error.\n");
            return -1;
        }

        memset(&dest_addr, 0, sizeof(dest_addr));
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_addr.s_addr = inet_addr(dest_ip);
        dest_addr.sin_port = htons(port);
        /* connect */
        reconnect_count ++;
        //gets(checksum);
        if(connect(sock, (struct sockaddr*)&dest_addr, sizeof(dest_addr)) < 0) {
            perror("Connecting to remote server failed, waiting for reconnecting.\n");
            if(reconnect_count > 10) {
                perror("Failed to connect to remote server. Please check the network.\n");
                break;
            }
            sleep(5);
            continue;
        }

        /* ask where to start */
        if(send_file_info(sock, uid, checksum, file_size, &resume_id) < 0) {
            close(sock);
            continue;
        }

        printf("starting from %uth chunk\n", resume_id);

        /* upload */
        for(i = resume_id; i < total_chunk_num; i++) {
            //printf("sending %uth chunk head\n", i);
            if(send_chunk_head(sock, i) < 0)
                break;
            //printf("sending %uth chunk body\n", i);
            if(send_chunk_body(sock, file_buf, file_size, i) < 0)
                break;
        }
        close(sock);
    }

    free(file_buf);

    if(i < total_chunk_num) {
        printf("Upload failed, %u/%u\n", i, total_chunk_num);
        return -1;
    }

    printf("Upload done, %u/%u\n", i, total_chunk_num);
    return 0;
}

int main(int argc, char* argv[])
{
    //upload(argv[1], "127.0.0.1", 4399, 1);
    upload(argv[1], "123.206.75.118", 14399, 1);
}
