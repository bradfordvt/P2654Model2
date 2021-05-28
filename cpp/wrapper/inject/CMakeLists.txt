cmake_minimum_required(VERSION 3.10)
project(injectwrap VERSION 1.0.0 LANGUAGES CXX)

set(SWIG /swigwin-4.0.2/swig.exe)
find_package(PythonLibs 3.7 REQUIRED)
message(STATUS "PYTHON_LIBRARIES = ${PYTHON_LIBRARIES}")
message(STATUS "PYTHON_EXECUTABLE = ${PYTHON_EXECUTABLE}")
message(STATUS "PYTHON_INCLUDE_DIRS = ${PYTHON_INCLUDE_DIRS}")
message(STATUS "execute_process(COMMAND ${SWIG} -c++ -python ${CMAKE_CURRENT_SOURCE_DIR}/injectwrap.i)")
execute_process(COMMAND ${SWIG} -c++ -python ${CMAKE_CURRENT_SOURCE_DIR}/injectwrap.i)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${DEFAULT_BUILD_TYPE}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${DEFAULT_BUILD_TYPE}" CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

include(GNUInstallDirs)

set(SOURCE_FILES
                injectwrap_wrap.cxx
)

message(STATUS "CMAKE_BUILD_TYPE : ${CMAKE_BUILD_TYPE}")

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

target_include_directories(${PROJECT_NAME} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../..>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../rvf>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../../strategy/inject>
    $<BUILD_INTERFACE:/Program\ Files/Python37/include>
    $<INSTALL_INTERFACE:include>
    PRIVATE ${INC_DIR})

if(CMAKE_HOST_WIN32)
set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".pyd")
else()
set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".so.1")
endif()

if(CMAKE_BUILD_TYPE STREQUAL Debug)
    message(STATUS "Do debug stuff")
    set(MY_BIN_DIR ${CMAKE_CURRENT_BINARY_DIR}/Debug)
    target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/../../rvf/build/Debug/rvf.lib ${PROJECT_SOURCE_DIR}/../../strategy/build/Debug/strategy.lib ${PYTHON_LIBRARIES})
elseif(CMAKE_BUILD_TYPE STREQUAL Release)
    message(STATUS "Do release stuff")
    set(MY_BIN_DIR ${CMAKE_CURRENT_BINARY_DIR}/Release)
    target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/../../rvf/build/Release/rvf.lib ${PROJECT_SOURCE_DIR}/../../strategy/build/Release/strategy.lib ${PYTHON_LIBRARIES})
elseif(CMAKE_BUILD_TYPE STREQUAL RelWithDebInfo)
    message(STATUS "Do release with debug info stuff")
    set(MY_BIN_DIR ${CMAKE_CURRENT_BINARY_DIR}/Debug)
    target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/../../rvf/build/Debug/rvf.lib ${PROJECT_SOURCE_DIR}/../../strategy/build/Debug/strategy.lib ${PYTHON_LIBRARIES})
elseif(CMAKE_BUILD_TYPE STREQUAL MinSizeRel)
    message(STATUS "Do minimal size release stuff")
    set(MY_BIN_DIR ${CMAKE_CURRENT_BINARY_DIR}/Release)
    target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/../../rvf/build/Release/rvf.lib ${PROJECT_SOURCE_DIR}/../../strategy/build/Release/strategy.lib ${PYTHON_LIBRARIES})
else()
    message(STATUS "Do debug stuff (default)")
    set(MY_BIN_DIR ${CMAKE_CURRENT_BINARY_DIR}/Debug)
    target_link_libraries(${PROJECT_NAME} ${PROJECT_SOURCE_DIR}/../../rvf/build/Debug/rvf.lib ${PROJECT_SOURCE_DIR}/../../strategy/build/Debug/strategy.lib ${PYTHON_LIBRARIES})
endif()
#     target_link_libraries(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/../../build/rvf/Debug/rvf.lib ${CMAKE_CURRENT_SOURCE_DIR}/../../build/strategy/Debug/strategy.lib ${PYTHON_LIBRARIES})

set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1)

install(TARGETS ${PROJECT_NAME} EXPORT injectwrapConfig
    ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(EXPORT injectwrapConfig DESTINATION share/injectwrap/cmake)

export(TARGETS ${PROJECT_NAME} FILE injectwrapConfig.cmake)

message(STATUS "CMAKE_BINARY_DIR : ${CMAKE_BINARY_DIR}")
message(STATUS "CMAKE_CURRENT_BINARY_DIR :${CMAKE_CURRENT_BINARY_DIR}")
message(STATUS "PROJECT_BINARY_DIR : ${PROJECT_BINARY_DIR}")
message(STATUS "injectmwrap_BINARY_DIR :${injectmwrap_BINARY_DIR}")

if(CMAKE_HOST_WIN32)
add_custom_command(TARGET ${PROJECT_NAME}
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E rename ${MY_BIN_DIR}/injectwrap.pyd ${MY_BIN_DIR}/_injectwrap.pyd
        COMMAND ${CMAKE_COMMAND} -E copy ${MY_BIN_DIR}/_injectwrap.pyd ${CMAKE_CURRENT_SOURCE_DIR}/../../../p2654model2/strategy/inject/strategies/
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/injectwrap.py ${CMAKE_CURRENT_SOURCE_DIR}/../../../p2654model2/strategy/inject/strategies/
)
else()
add_custom_command(TARGET wrapper
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E rename ${MY_BIN_DIR}/injectwrap.so.1 ${MY_BIN_DIR}/_injectwrap.so.1
        COMMAND ${CMAKE_COMMAND} -E copy ${MY_BIN_DIR}/_injectwrap.so.1 ${CMAKE_CURRENT_SOURCE_DIR}/../../../p2654model2/strategy/inject/strategies/
        COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/injectwrap.py ${CMAKE_CURRENT_SOURCE_DIR}/../../../p2654model2/strategy/inject/strategies/
)
endif()
