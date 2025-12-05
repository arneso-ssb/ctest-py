from cffi import FFI
import os
import sys

ffi = FFI()

# Declare the C API we want to use
ffi.cdef("""
    const char *get_curl_version(void);
    const char *get_openssl_version(void);
""")

# Path to the built shared library (CMake install step puts it here)
base_dir = os.path.dirname(__file__)

if sys.platform.startswith("win"):
    libname = "curlcrypto.dll"
elif sys.platform == "darwin":
    libname = "libcurlcrypto.dylib"
else:
    libname = "libcurlcrypto.so"

libpath = os.path.join(base_dir, libname)

ffi.set_source(
    "_curlcrypto",   # Name of generated Python extension
    """
    // Provide forward declarations directly to avoid needing headers at build time
    extern const char *get_curl_version(void);
    extern const char *get_openssl_version(void);
    """,
    libraries=["curlcrypto"],
    library_dirs=[base_dir],
)

if __name__ == "__main__":
    ffi.compile(verbose=True)
