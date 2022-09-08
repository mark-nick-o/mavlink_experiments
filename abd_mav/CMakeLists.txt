cmake_minimum_required(VERSION 3.17)
project(ABD-MAV VERSION 0.1.0)
#test
include(CTest)
enable_testing()

add_executable(ABD-MAV main.cpp)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
target_link_libraries(${PROJECT_NAME} -lexplain )
include_directories("${CMAKE_CURRENT_SOURCE_DIR}//mavlink2C/common", "${CMAKE_CURRENT_SOURCE_DIR}//mavlink2C/ardupilotmega") 
