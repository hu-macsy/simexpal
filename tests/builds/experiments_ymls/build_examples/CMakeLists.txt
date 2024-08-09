cmake_minimum_required(VERSION 3.14)
project(test_build_cpp)

set(CMAKE_CXX_STANDARD 14)

add_executable(test_build test_build.cpp)

install(TARGETS test_build)
