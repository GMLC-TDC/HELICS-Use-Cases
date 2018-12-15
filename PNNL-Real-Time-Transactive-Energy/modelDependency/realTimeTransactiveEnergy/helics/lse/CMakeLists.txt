

cmake_minimum_required(VERSION 3.4)

project(LSE)

set(CMAKE_CXX_STANDARD 14)

find_package(HELICS REQUIRED)

mark_as_advanced(BOOST_INSTALL_PATH)
mark_as_advanced(CMAKE_BUILD_TYPE)
mark_as_advanced(HELICS_APP)
mark_as_advanced(HELICS_BROKER)
mark_as_advanced(HELICS_DIR)
mark_as_advanced(HELICS_PLAYER)
mark_as_advanced(HELICS_RECORDER)
mark_as_advanced(BOOST_INSTALL_PATH)

add_executable(lse lse.cpp)

target_link_libraries(lse ${ZeroMQ_LIBRARY})
target_link_libraries(lse HELICS::helics-static)

install(TARGETS lse DESTINATION bin)
