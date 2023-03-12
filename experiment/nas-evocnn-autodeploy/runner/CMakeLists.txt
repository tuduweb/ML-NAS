project(benchncnn)

if(MSVC)
    # warning C4996: 'fopen': This function or variable may be unsafe. Consider using fopen_s instead. To disable deprecation, use _CRT_SECURE_NO_WARNINGS. See online help for details.
    add_definitions(/wd4996)
endif()
cmake_minimum_required(VERSION 3.16)

# ~/development/lightweight/ncnn/build/install/lib/cmake/ncnn
set(ncnn_DIR "/home/tuduweb/development/lightweight/ncnn/build-debug/install/lib/cmake/ncnn")
find_package(ncnn REQUIRED)

add_executable(benchncnn benchmark.cpp)
target_link_libraries(benchncnn PRIVATE ncnn)

# add benchncnn to a virtual project group
# set_property(TARGET benchncnn PROPERTY FOLDER "benchmark")
