cmake_minimum_required (VERSION 3.2)

set (MODEL_NAME %MODEL_NAME%)
set (MODEL_IDENTIFIER %MODEL_IDENTIFIER%)

project (${MODEL_NAME})

if (MSVC)
  # link statically against the the Visual C runtime
  string(REPLACE "/MD"  "/MT"  CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}")
  string(REPLACE "/MDd" "/MTd" CMAKE_C_FLAGS_DEBUG   "${CMAKE_C_FLAGS_DEBUG}")
endif ()

if (WIN32)
   set(FMI_PLATFORM win)
elseif (APPLE)
   set(FMI_PLATFORM darwin)
else ()
   set(FMI_PLATFORM linux)
endif ()

if ("${CMAKE_SIZEOF_VOID_P}" STREQUAL "8")
    set (FMI_PLATFORM ${FMI_PLATFORM}64)
else ()
    set (FMI_PLATFORM ${FMI_PLATFORM}32)
endif ()

add_library(${MODEL_IDENTIFIER} SHARED modelDescription.xml %SOURCES%)

target_compile_definitions(${MODEL_IDENTIFIER} PUBLIC %DEFINITIONS%)

if (MSVC)
    target_compile_definitions(${MODEL_IDENTIFIER} PUBLIC _CRT_SECURE_NO_WARNINGS)
endif ()

target_include_directories(${MODEL_IDENTIFIER} PUBLIC
    %INCLUDE_DIRS%
    ${CMAKE_CURRENT_SOURCE_DIR}/sources
)

set_target_properties(${MODEL_IDENTIFIER} PROPERTIES
    PREFIX ""
    RUNTIME_OUTPUT_DIRECTORY         "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG   "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    LIBRARY_OUTPUT_DIRECTORY         "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG   "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    ARCHIVE_OUTPUT_DIRECTORY         "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    ARCHIVE_OUTPUT_DIRECTORY_DEBUG   "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
    ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/binaries/${FMI_PLATFORM}"
)

if (WIN32)
    # needed for Dymola FMUs
    target_link_libraries(${MODEL_IDENTIFIER} shlwapi.lib)
endif ()

add_custom_command(TARGET ${MODEL_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E tar cfv "${CMAKE_CURRENT_SOURCE_DIR}/${MODEL_NAME}.fmu" --format=zip
    modelDescription.xml
    binaries
    sources
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)
