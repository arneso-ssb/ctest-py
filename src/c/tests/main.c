#include <stdio.h>
#include "curlcrypto.h"

int main(void) {
    const char *curl_ver = get_curl_version();
    const char *ssl_ver  = get_openssl_version();

    printf("libcurl version: %s\n", curl_ver ? curl_ver : "(null)");
    printf("OpenSSL version: %s\n", ssl_ver ? ssl_ver : "(null)");
    return 0;
}
