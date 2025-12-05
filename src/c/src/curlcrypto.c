#include <stdio.h>
#include <stdlib.h>

#include <curl/curl.h>          // for libcurl version probe
#include <openssl/opensslv.h>   // for OpenSSL version defines
#include <openssl/crypto.h>     // ensure libcrypto is linked

#include "curlcrypto.h"

const char *get_curl_version(void) {
    return curl_version();
}

const char *get_openssl_version(void) {
    return OPENSSL_VERSION_TEXT;
}
