import argparse
import sys
from pathlib import Path

from cffi import FFI

ffi = FFI()

# Declare the C API we want to use
ffi.cdef(
    """
    const char *get_curl_version(void);
    const char *get_openssl_version(void);
    """
)

# Path to the built shared library (CMake install step puts it here)
base_dir = Path(__file__).resolve().parent

if sys.platform.startswith("win"):
    libname = "curlcrypto.dll"
elif sys.platform == "darwin":
    libname = "libcurlcrypto.dylib"
else:
    libname = "libcurlcrypto.so"

# Full path to the shared library (not used directly here, but kept for clarity)
libpath = base_dir / libname

# Use forward declarations to avoid depending on project headers when emitting C
ffi.set_source(
    "_curlcrypto",  # Name of the generated Python extension
    """
    #include "curlcrypto.h"
    """,
    libraries=["curlcrypto"],
    library_dirs=[str(base_dir)],
)


def main() -> int:
    """Emit the CFFI C source file instead of compiling the extension.

    If --emit-c PATH is not provided, write the file next to this script as
    _curlcrypto.c.
    """
    parser = argparse.ArgumentParser(
        description="Generate C source for the _curlcrypto CFFI module"
    )
    parser.add_argument(
        "--emit-c",
        metavar="PATH",
        help="Output path for the generated C file (_curlcrypto.c)",
    )
    args = parser.parse_args()

    out_path = Path(args.emit_c) if args.emit_c else (base_dir / "_curlcrypto.c")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ffi.emit_c_code(str(out_path))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
