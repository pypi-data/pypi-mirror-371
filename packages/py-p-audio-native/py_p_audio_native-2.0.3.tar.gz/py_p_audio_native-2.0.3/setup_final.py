from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
import pybind11

# Define the extension module with mock implementation
ext_modules = [
    Pybind11Extension(
        "py_p_audio_core",
        sources=[
            "src/cpp/real_implementation.cpp",
        ],
        include_dirs=[
            pybind11.get_cmake_dir() + "/../../../include",
            "third_party/portaudio/include",
            "asiosdk/common",
            "asiosdk/host",
            "asiosdk/host/pc",
        ],
        libraries=["portaudio_static_x64", "ole32", "user32", "advapi32", "winmm", "setupapi"],
        library_dirs=["third_party/portaudio/lib"],
        define_macros=[
            ("VERSION_INFO", '"2.0.3"'),
        ],
        cxx_std=17,
        language='c++',
    ),
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-p-audio-native", 
    version="2.0.3",
    author="hiroshi-tamura",
    author_email="",
    description="高性能な Python オーディオライブラリ - ネイティブ C++ コア搭載",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hiroshi-tamura/py-p-audio-native",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    packages=["py_p_audio_native"],
    package_dir={"py_p_audio_native": "src/python/py_p_audio_native"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    keywords="audio recording playback WASAPI ASIO native pybind11",
    project_urls={
        "Bug Reports": "https://github.com/hiroshi-tamura/py-p-audio-native/issues",
        "Source": "https://github.com/hiroshi-tamura/py-p-audio-native/",
    },
)