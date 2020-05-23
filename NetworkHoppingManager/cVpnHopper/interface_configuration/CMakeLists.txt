cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

find_package(PkgConfig)
include_directories(${PROJECT_SOURCE_DIR}/includes)
add_library(interface_configuration STATIC interface_configuration.c)
target_link_libraries(interface_configuration)
