import ctest_py


def test_curl_version() -> None:
    curl_version = ctest_py.curl_version()
    assert curl_version.startswith("libcurl")


def test_openssl_version() -> None:
    openssl_version = ctest_py.openssl_version()
    assert openssl_version.startswith("OpenSSL")
