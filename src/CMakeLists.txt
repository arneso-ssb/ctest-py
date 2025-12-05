cmake_minimum_required(VERSION 3.15)
project(curlcrypto LANGUAGES C)

# Testing is optional (enabled with -DBUILD_TESTING=ON)
include(CTest)
enable_testing()

add_subdirectory(c)

# Install the built C library into the Python package
install(TARGETS curlcrypto
    LIBRARY DESTINATION ctest_py
    RUNTIME DESTINATION ctest_py
)
