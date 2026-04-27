cmake_minimum_required (VERSION 2.6)
project (cVpnHopper)

find_package(PkgConfig)
#find_package(Threads REQUIRED)

set (cVpnHopper_VERSION_MAJOR 1)
set (cVpnHopper_VERSION_MINOR 0)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0 -g")

option(INTERFACE_CONFIGURATION "use interface configuration" ON)
option(EXECUTABLE_TESTER "use executabe for testing library for python use" ON)

configure_file (
  "${PROJECT_SOURCE_DIR}/cVpnHopper.h.in"
  "${PROJECT_BINARY_DIR}/cVpnHopper.h"
  )

MESSAGE( STATUS "PROJECT_BINARY_DIR: " ${PROJECT_BINARY_DIR} " PROJECT_SOURCE_DIR " ${PROJECT_SOURCE_DIR})
include_directories(${CMAKE_CURRENT_BINARY_DIR} ${CMAKE_CURRENT_SOURCE_DIR}/includes/ ${PC_PTHREAD_INCLUDE_DIRS})

if (INTERFACE_CONFIGURATION)
	include_directories(${CMAKE_CURRENT_SOURCE_DIR}/interface_configuration/)
	add_subdirectory(interface_configuration)
endif(INTERFACE_CONFIGURATION)

add_library (cVpnHopper SHARED src/cVpnHopper.c)

if (INTERFACE_CONFIGURATION)
	target_link_libraries(cVpnHopper interface_configuration)
endif (INTERFACE_CONFIGURATION)

if (EXECUTABLE_TESTER)
	add_executable(cVpnHopping_tester src/common.c)
endif (EXECUTABLE_TESTER)

target_link_libraries(cVpnHopper ${PC_PTHREAD_LIBRARY_DIRS})

if (EXECUTABLE_TESTER)
	target_link_libraries(cVpnHopping_tester cVpnHopper)
endif (EXECUTABLE_TESTER)

set_target_properties(cVpnHopper PROPERTIES
    VERSION ${cVpnHopper_VERSION_MAJOR}
    SOVERSION ${cVpnHopper_VERSION_MINOR}
    PUBLIC_HEADER cVpnHopper.h)

#install (FILES ${PROJECT_SOURCE_DIR}/ DESTINATION ${PROJECT_BINARY_DIR})
install (FILES ${PROJECT_BINARY_DIR}/cVpnHopper.h DESTINATION include)
