
cmake_minimum_required(VERSION 3.4)

project(HELICS_LAUNCHER)

set(CMAKE_CXX_STANDARD 14)

cmake_policy(SET CMP0074 OLD)
find_package(MPI REQUIRED)


SET(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib:${CMAKE_INSTALL_PREFIX}/include")

SET(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

add_executable(helics_launcher helics_launcher.cpp)

target_include_directories(helics_launcher PUBLIC ${MPI_C_HEADER_DIR})
target_link_libraries(helics_launcher PUBLIC ${MPI_mpi_LIBRARY})

install(TARGETS helics_launcher DESTINATION bin)
