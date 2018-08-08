#include <cstdlib>
#include <iostream>
#ifndef WIN32
   #include <arpa/inet.h>
   #include <netdb.h>
#else
   #include <winsock2.h>
   #include <ws2tcpip.h>
#endif
#include <srt/srt.h>

int main()
{
    int res = srt_startup();
    if (0 != res) {
        std::cerr << "srt_startup failed" << std::endl;
        return EXIT_FAILURE;
    }
    SRTSOCKET s = srt_socket(AF_INET, SOCK_DGRAM, 0);
    if (s == SRT_INVALID_SOCK) {
        srt_cleanup();
        std::cerr << "srt_socket failed" << std::endl;
        return EXIT_FAILURE;
    }
    int version = 0;
    int len = sizeof(version);
    res = srt_getsockopt(s, 0, SRTO_VERSION, &version, &len);
    if (0 != res) {
        srt_close(s);
        srt_cleanup();
        std::cerr << "srt_getsockopt failed" << std::endl;
        return EXIT_FAILURE;
    }
    int major = version / 0x10000;
    int minor = version % 0x10000 / 0x100;
    int patch = version % 0x10000 % 0x100;
    std::cout << "SRT version: " << major << "." << minor << "." << patch << std::endl;
    srt_close(s);
    srt_cleanup();
    return EXIT_SUCCESS;
}
