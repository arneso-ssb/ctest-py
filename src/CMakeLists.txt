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

# Find Python for post-install CFFI bindings generation
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Install the built C library into the Python package
install(TARGETS curlcrypto
    LIBRARY DESTINATION ctest_py
    RUNTIME DESTINATION ctest_py
)

# Also install the CFFI builder script so path resolution is stable
install(FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/ctest_py/_build_cffi.py
    DESTINATION ctest_py
)

# Generate CFFI bindings after install so the shared library is in place
install(CODE [[
    set(_cffi_script "${CMAKE_INSTALL_PREFIX}/ctest_py/_build_cffi.py")
    set(_cffi_workdir "${CMAKE_INSTALL_PREFIX}/ctest_py")
    file(MAKE_DIRECTORY "${_cffi_workdir}")
    execute_process(
        COMMAND "${Python_EXECUTABLE}" "${_cffi_script}"
        WORKING_DIRECTORY "${_cffi_workdir}"
        RESULT_VARIABLE _cffi_result
    )
    if(NOT _cffi_result EQUAL 0)
        message(FATAL_ERROR "CFFI builder failed with code ${_cffi_result}")
    endif()
]])
