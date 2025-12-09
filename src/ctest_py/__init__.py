"""ctest_py - Python bindings for the curlcrypto C library using CFFI."""

from cffi.api import CData

from ._curlcrypto import ffi
from ._curlcrypto import lib

__all__ = [
    "curl_version",
    "openssl_version",
]


def _decode(result: CData) -> str:
    """Convert a char* from C into a Python str safely."""
    if result == ffi.NULL:
        return ""
    return ffi.string(result).decode("utf-8", errors="replace")


def curl_version() -> str:
    """Returns: The version string of libcurl used in the underlying C library."""
    return _decode(lib.get_curl_version())


def openssl_version() -> str:
    """Returns: The version string from OpenSSL."""
    return _decode(lib.get_openssl_version())
