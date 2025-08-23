import os
import sys
import subprocess
from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11.setup_helpers import ParallelCompile
from setuptools import setup, Extension
import pybind11

# Enable parallel compilation
ParallelCompile("NPY_NUM_BUILD_JOBS").install()

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "py_p_audio_core",
        sources=[
            "src/cpp/AudioSystem.cpp",
            "src/cpp/AudioRecorder.cpp", 
            "src/cpp/AudioPlayer.cpp",
            "src/cpp/WASAPILoopbackRecorder.cpp",
            "src/cpp/python_bindings.cpp",
            # ASIO SDK sources
            "asiosdk/common/asio.cpp",
            "asiosdk/common/asiodrvr.cpp", 
            "asiosdk/common/combase.cpp",
            "asiosdk/common/register.cpp",
            "asiosdk/host/ASIOConvertSamples.cpp",
            "asiosdk/host/asiodrivers.cpp",
            "asiosdk/host/pc/asiolist.cpp",
        ],
        include_dirs=[
            # Path to pybind11 headers
            pybind11.get_cmake_dir() + "/../../../include",
            "src/cpp",
            "include", 
            "asiosdk/common",
            "asiosdk/host",
            "asiosdk/host/pc",
            # Add PortAudio include path here
            "third_party/portaudio/include",
        ],
        libraries=["portaudio_static", "ole32", "winmm", "dsound", "setupapi", "uuid"] if sys.platform == "win32" else [],
        library_dirs=["third_party/portaudio/lib"] if sys.platform == "win32" else [],
        define_macros=[
            ("WIN32_LEAN_AND_MEAN", None),
            ("NOMINMAX", None),
        ] if sys.platform == "win32" else [],
        cxx_std=17,
        language='c++',
    ),
]

# Custom build command to handle dependencies
class CustomBuildExt(build_ext):
    def build_extensions(self):
        # Download/build PortAudio if needed
        self.ensure_portaudio()
        super().build_extensions()
    
    def ensure_portaudio(self):
        """Ensure PortAudio is available"""
        portaudio_dir = Path("third_party/portaudio")
        if not portaudio_dir.exists():
            print("PortAudio not found. You need to:")
            print("1. Download PortAudio from http://www.portaudio.com/")
            print("2. Extract to third_party/portaudio/")
            print("3. Build static library as portaudio_static_x64.lib")
            sys.exit(1)

setup(
    name="py-p-audio-native", 
    version="2.0.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": CustomBuildExt},
    zip_safe=False,
    python_requires=">=3.8",
)