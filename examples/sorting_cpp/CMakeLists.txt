cmake_minimum_required(VERSION 3.14)
project(sorting_cpp)

set(CMAKE_CXX_STANDARD 14)

add_executable(quicksort quicksort.cpp)

install(TARGETS quicksort DESTINATION bin)
