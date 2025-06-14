cmake_minimum_required(VERSION 3.31)
project(normal)

# 添加可执行目标
add_executable(normal main.cpp)

set(CMAKE_CXX_STANDARD 20)

# 默认配置 - macOS 原生构建
if(APPLE AND NOT CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Configuring for macOS native build")

    # macOS 特定设置
    set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum OS X deployment version")
    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    # macOS 编译器选项
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(normal PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    # macOS 链接器选项
    target_link_libraries(normal)
endif()

# Linux 交叉编译配置（通过工具链文件激活）
if(CMAKE_TOOLCHAIN_FILE)
    message(STATUS "Configuring for Linux cross-compilation")

    # 静态链接设置
    set(CMAKE_EXE_LINKER_FLAGS "-static")
    set(CMAKE_CXX_FLAGS "-static-libgcc -static-libstdc++")

    # Linux 特定设置
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        target_compile_options(normal PRIVATE -O2 -Wall)
    endif()
endif()