cmake_minimum_required(VERSION 3.18)
project(py_p_audio_native)

# C++17 required
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Windows-specific settings
if(WIN32)
    add_definitions(-DWIN32_LEAN_AND_MEAN -DNOMINMAX)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

# Find required packages
find_package(pybind11 REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src/cpp)

# PortAudio static library path (adjust as needed)
set(PORTAUDIO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/third_party/portaudio")
set(PORTAUDIO_INCLUDE_DIR "${PORTAUDIO_ROOT}/include")
set(PORTAUDIO_LIBRARY "${PORTAUDIO_ROOT}/lib/portaudio_static_x64.lib")

# ASIO SDK path  
set(ASIOSDK_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/asiosdk")
include_directories("${ASIOSDK_ROOT}/common")
include_directories("${ASIOSDK_ROOT}/host")

# Source files
set(CPP_SOURCES
    src/cpp/AudioSystem.cpp
    src/cpp/AudioRecorder.cpp  
    src/cpp/AudioPlayer.cpp
    src/cpp/WASAPILoopbackRecorder.cpp
    src/cpp/python_bindings.cpp
)

# ASIO SDK sources
set(ASIO_SOURCES
    asiosdk/common/asio.cpp
    asiosdk/common/asiodrvr.cpp
    asiosdk/common/combase.cpp
    asiosdk/common/register.cpp
    asiosdk/host/ASIOConvertSamples.cpp
    asiosdk/host/asiodrivers.cpp
    asiosdk/host/pc/asiolist.cpp
)

# Create pybind11 module
pybind11_add_module(py_p_audio_core ${CPP_SOURCES} ${ASIO_SOURCES})

# Link libraries
if(WIN32)
    target_link_libraries(py_p_audio_core PRIVATE 
        ${PORTAUDIO_LIBRARY}
        ole32
        winmm
        dsound
        setupapi
        uuid
    )
endif()

# Include directories for the module
target_include_directories(py_p_audio_core PRIVATE 
    ${PORTAUDIO_INCLUDE_DIR}
    ${ASIOSDK_ROOT}/common
    ${ASIOSDK_ROOT}/host
    ${ASIOSDK_ROOT}/host/pc
)

# Compiler-specific properties
target_compile_definitions(py_p_audio_core PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})

# Output directory
set_target_properties(py_p_audio_core PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/src/python/py_p_audio_native"
)