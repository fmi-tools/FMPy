cmake_minimum_required (VERSION 3.2)

project (remoting)

# set(CMAKE_BUILD_TYPE Debug)

set(RPCLIB "" CACHE STRING "RPCLIB installation directory")

if (WIN32)
    if ("${CMAKE_SIZEOF_VOID_P}" STREQUAL "8")
        set(FMI_PLATFORM win64)
    else ()
        set(FMI_PLATFORM win32)
	endif ()
else ()
    set(FMI_PLATFORM linux64)
endif ()

message("FMI_PLATFORM: ${FMI_PLATFORM}")

if (MSVC)
  # link statically against the the Visual C runtime
  set(variables
    CMAKE_C_FLAGS_DEBUG
    CMAKE_C_FLAGS_MINSIZEREL
    CMAKE_C_FLAGS_RELEASE
    CMAKE_C_FLAGS_RELWITHDEBINFO
    CMAKE_CXX_FLAGS_DEBUG
    CMAKE_CXX_FLAGS_MINSIZEREL
    CMAKE_CXX_FLAGS_RELEASE
    CMAKE_CXX_FLAGS_RELWITHDEBINFO
  )

  foreach(variable ${variables})
    if(${variable} MATCHES "/MD")
      string(REGEX REPLACE "/MD" "/MT" ${variable} "${${variable}}")
    endif()
  endforeach()

  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)

endif ()

# server
add_executable(server_tcp
    ../../src/fmpy/c-code/fmi2Functions.h
    ../../src/fmpy/c-code/fmi2FunctionTypes.h
    ../../src/fmpy/c-code/fmi2TypesPlatform.h
    ../thirdparty/Reference-FMUs/include/FMI.h
    ../thirdparty/Reference-FMUs/include/FMI2.h
    ../thirdparty/Reference-FMUs/src/FMI.c
    ../thirdparty/Reference-FMUs/src/FMI2.c
    remoting_tcp.h
    server_tcp.cpp
)

set_property(TARGET server_tcp PROPERTY CXX_STANDARD 11)

target_include_directories(server_tcp PUBLIC
    ../thirdparty/Reference-FMUs/include
    ../../src/fmpy/c-code
    ../src/fmucontainer
    "${RPCLIB}/include"
)

if (UNIX)
    target_compile_options(server_tcp PRIVATE "-pthread")
endif ()

if (WIN32)
    target_link_libraries(server_tcp
      "${RPCLIB}/lib/rpc.lib"
    )
else ()
    target_link_libraries(server_tcp
      "${RPCLIB}/lib/librpc.a"
      ${CMAKE_DL_LIBS}
      pthread
    )
endif ()

add_custom_command(TARGET server_tcp POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy
  "$<TARGET_FILE:server_tcp>"
  "${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/remoting/${FMI_PLATFORM}"
)

if (UNIX)
    set(CMAKE_THREAD_PREFER_PTHREAD TRUE)
    set(THREADS_PREFER_PTHREAD_FLAG TRUE)
endif ()

# client
add_library(client_tcp SHARED
  ../../src/fmpy/c-code/fmi2Functions.h
  ../../src/fmpy/c-code/fmi2FunctionTypes.h
  ../../src/fmpy/c-code/fmi2TypesPlatform.h
  remoting_tcp.h
  client_tcp.cpp
)

set_property(TARGET client_tcp PROPERTY CXX_STANDARD 11)
set_target_properties(client_tcp PROPERTIES LINK_SEARCH_START_STATIC 1)
set_target_properties(client_tcp PROPERTIES LINK_SEARCH_END_STATIC 1)

set_target_properties(client_tcp PROPERTIES PREFIX "")

if (UNIX)
    set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
    set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")
    find_package(Threads REQUIRED)
endif()

target_include_directories(client_tcp PRIVATE
  ..
  ../../src/fmpy/c-code
  ../src/fmucontainer
  "${RPCLIB}/include"
)

if (WIN32)
    target_link_libraries(client_tcp
      "${RPCLIB}/lib/rpc.lib"
    )
else ()
    target_link_libraries(client_tcp
      "${RPCLIB}/lib/librpc.a"
      Threads::Threads
    )
endif ()

add_custom_command(TARGET client_tcp POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy
  "$<TARGET_FILE:client_tcp>"
  "${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/remoting/${FMI_PLATFORM}"
)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.h.in ${CMAKE_CURRENT_BINARY_DIR}/config.h)


if (WIN32)

    # shared memory server
    add_executable(server_sm
        communication.c communication.h
        process.c process.h 
        remote.c remote.h
        server.c server.h
        ${CMAKE_CURRENT_BINARY_DIR}/config.h
    )

    set (CMAKE_C_STANDARD 99)

    target_include_directories(server_sm PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/c-code
        ${CMAKE_CURRENT_BINARY_DIR}
    )

    add_custom_command(TARGET server_sm POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy
      "$<TARGET_FILE:server_sm>"
      "${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/remoting/${FMI_PLATFORM}"
    )

    # shared memory client_sm
    add_library(client_sm SHARED
        client.c client.h
        communication.c communication.h
        process.c process.h 
        remote.c remote.h
        ${CMAKE_CURRENT_BINARY_DIR}/config.h
    )

    target_include_directories(client_sm PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/c-code
        ${CMAKE_CURRENT_BINARY_DIR}
    )

    add_custom_command(TARGET client_sm POST_BUILD COMMAND ${CMAKE_COMMAND} -E copy
        "$<TARGET_FILE:client_sm>"
        "${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/remoting/${FMI_PLATFORM}"
    )

endif ()

# client test
add_executable(client_test
  client_test.cpp
)

set_property(TARGET client_test PROPERTY CXX_STANDARD 11)

target_include_directories(client_test PUBLIC
  ../../src/fmpy/c-code
  ../src/fmucontainer
)

target_link_libraries(client_test
  ${CMAKE_DL_LIBS}
)

if (BUILD_TESTER)

    add_executable(test_sizeof
        ${CMAKE_CURRENT_SOURCE_DIR}/test_sizeof.c
        remote.h
    )

    target_include_directories(test_sizeof PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/c-code
    )

    add_custom_command(OUTPUT test_sizeof.c
        COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/gen_sizeof.py
        DEPENDS gen_sizeof.py
    )

    add_executable(test_server
        ${CMAKE_CURRENT_SOURCE_DIR}/test_server.c
    )
    target_include_directories(test_server PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/c-code)

    target_include_directories(test_sizeof PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../../src/fmpy/c-code
    )

endif ()
