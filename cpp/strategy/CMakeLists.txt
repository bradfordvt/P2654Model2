cmake_minimum_required(VERSION 3.10)

project(strategy VERSION 1.0.0 LANGUAGES CXX)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${DEFAULT_BUILD_TYPE}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${DEFAULT_BUILD_TYPE}" CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

include(GNUInstallDirs)

set(SOURCE_FILES
                transform/cdummytstrategy.cpp
)

add_library(${PROJECT_NAME} ${SOURCE_FILES})

message(STATUS "location of strategyerror.hpp : ${CMAKE_CURRENT_SOURCE_DIR}/..")
message(STATUS "location of CMAKE_INSTALL_LIBDIR : ${CMAKE_INSTALL_LIBDIR}")

target_include_directories(${PROJECT_NAME} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/transform>
    $<INSTALL_INTERFACE:include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/..>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../rvf>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../rvf/protocols>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../rvf/commands>
    PRIVATE ${INC_DIR})

set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1)

install(TARGETS ${PROJECT_NAME} EXPORT strategyConfig
    ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})
# install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(EXPORT strategyConfig DESTINATION share/strategy/cmake)

export(TARGETS ${PROJECT_NAME} FILE strategyConfig.cmake)