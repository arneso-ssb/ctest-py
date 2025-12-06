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

# Find Python for building a CPython extension module (_curlcrypto)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

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

# Generate the CFFI C source during the build (not during install)
set(GENERATED_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated)
set(GENERATED_C   ${GENERATED_DIR}/_curlcrypto.c)

add_custom_command(
  OUTPUT ${GENERATED_C}
  COMMAND ${CMAKE_COMMAND} -E make_directory ${GENERATED_DIR}
  COMMAND "${Python_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/ctest_py/_build_cffi.py" --emit-c "${GENERATED_C}"
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/ctest_py/_build_cffi.py
  COMMENT "Generating CFFI C source _curlcrypto.c"
  VERBATIM
)
add_custom_target(generate_cffi DEPENDS ${GENERATED_C})

# Build the Python extension module from the generated CFFI source
Python_add_library(_curlcrypto MODULE WITH_SOABI
    ${GENERATED_C}
)
add_dependencies(_curlcrypto generate_cffi)

# Link the extension against our C library and Python module interface
target_link_libraries(_curlcrypto PRIVATE curlcrypto Python::Module)

# If the generated C happens to include project headers, point to them
target_include_directories(_curlcrypto PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/c/include
)

# Ensure at runtime the extension can find the sibling libcurlcrypto.* next to it
if(APPLE)
  set(_origin "@loader_path")
elseif(UNIX)
  set(_origin "$ORIGIN")
endif()
if(UNIX)
  set_target_properties(_curlcrypto PROPERTIES
    BUILD_RPATH "${_origin}"
    INSTALL_RPATH "${_origin}"
  )
endif()

# Install the Python extension into the package directory
install(TARGETS _curlcrypto
  LIBRARY DESTINATION ctest_py   # Unix-like
  RUNTIME DESTINATION ctest_py   # Windows
)
