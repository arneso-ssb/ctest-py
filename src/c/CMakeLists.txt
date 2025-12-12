find_package(CURL REQUIRED)
find_package(OpenSSL REQUIRED)

# ------------------------------------------------------------------------------
# cloudsqlite: Shared library for SQLite extension (loaded via load_extension())
# ------------------------------------------------------------------------------
add_library(cloudsqlite SHARED
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

set_target_properties(cloudsqlite PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS ON
)

target_include_directories(cloudsqlite
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(cloudsqlite
    PRIVATE
        CURL::libcurl
        OpenSSL::SSL
        OpenSSL::Crypto
)

# ------------------------------------------------------------------------------
# curlcrypto: Static library for Python CFFI bindings
# Contains only the CFFI interface code (curlcrypto.c)
# ------------------------------------------------------------------------------
add_library(curlcrypto STATIC
    src/curlcrypto.c
)

# Enable Position Independent Code for the static library
# (required when embedding in a shared Python extension module)
set_target_properties(curlcrypto PROPERTIES
    POSITION_INDEPENDENT_CODE ON
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
)

# Public include path (so Python extension can include headers)
target_include_directories(curlcrypto
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Link curlcrypto against cloudsqlite so CFFI can access the full functionality
target_link_libraries(curlcrypto
    PUBLIC
        cloudsqlite
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
