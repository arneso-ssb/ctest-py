find_package(CURL REQUIRED)
find_package(OpenSSL REQUIRED)

add_library(curlcrypto SHARED
    src/curlcrypto.c
    src/bcvencrypt.c
    src/bcvlog.c
    src/bcvmodule.c
    src/bcvutil.c
    src/blockcachevfs.c
#   src/blockcachevfsd.c
    src/extension.c
    src/simplexml.c
    src/sqlite3.c
#   src/tclsqlite.c
)

# Public include path (so other targets, e.g. Python extension or tests, can include this)
target_include_directories(curlcrypto
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Require C11 (recommended for modern C code)
set_target_properties(curlcrypto PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

target_link_libraries(curlcrypto
    PUBLIC
        CURL::libcurl
        OpenSSL::SSL
        OpenSSL::Crypto
)

# Optional: Define a C test executable
if(BUILD_TESTING)
    add_executable(curlcrypto_test
        tests/main.c
    )

    target_link_libraries(curlcrypto_test
        PRIVATE curlcrypto
    )

    # Register as a CTest test
    add_test(NAME curlcrypto_version_test COMMAND curlcrypto_test)
endif()
