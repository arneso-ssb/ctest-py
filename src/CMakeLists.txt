cmake_minimum_required(VERSION 3.28)

# Fallbacks for manual CMake runs (outside scikit-build-core)
if(NOT DEFINED SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME "ctest-py" CACHE STRING "Fallback project name")
endif()
if(NOT DEFINED SKBUILD_PROJECT_VERSION)
    set(SKBUILD_PROJECT_VERSION "0.0.0" CACHE STRING "Fallback project version")
endif()

project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES C)

# Testing is optional (enabled with -DBUILD_TESTING=ON)
include(CTest)
enable_testing()

add_subdirectory(c)

# Install the built C library into the Python package
install(TARGETS curlcrypto
    LIBRARY DESTINATION ctest_py
    RUNTIME DESTINATION ctest_py
)

# Also install the CFFI builder script so it can be invoked manually if needed
install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/ctest_py/_build_cffi.py
    DESTINATION ctest_py
)
