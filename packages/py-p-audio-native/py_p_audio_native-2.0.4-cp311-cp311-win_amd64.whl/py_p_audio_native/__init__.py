"""
py-p-audio-native: High-performance Python audio library with native C++ core

This library provides professional-grade audio recording and playback capabilities
with zero external dependencies, powered by native C++ implementation using
PortAudio and ASIO SDK.
"""

__version__ = "2.0.0"
__author__ = "hiroshi-tamura"

# Import native C++ module
try:
    from . import py_p_audio_core
except ImportError as e:
    raise ImportError(
        "Failed to import native module. Please ensure the library was installed correctly. "
        f"Error: {e}"
    )

# High-level API imports
from .api import (
    # Device management
    list_devices, get_device_info, find_device,
    
    # Simple recording functions
    record, record_loopback,
    
    # Simple playback functions
    play, play_with_callback,
    
    # Device classes
    AudioDevice,
    
    # Recorder classes
    Recorder, LoopbackRecorder,
    
    # Player class
    Player,
    
    # Utility classes
    ProgressCallback,
)

# Core classes (direct access to C++ objects)
from .py_p_audio_core import (
    AudioSystem,
    AudioRecorder, 
    AudioPlayer,
    WASAPILoopbackRecorder,
    DeviceInfo,
)

# Exceptions
from .exceptions import (
    PyPAudioNativeError,
    DeviceError,
    RecordingError,
    PlaybackError,
    FileError,
)

__all__ = [
    # Version info
    "__version__", "__author__",
    
    # High-level API
    "list_devices", "get_device_info", "find_device",
    "record", "record_loopback", 
    "play", "play_with_callback",
    
    # Classes
    "AudioDevice", "Recorder", "LoopbackRecorder", "Player",
    "ProgressCallback",
    
    # Core C++ classes
    "AudioSystem", "AudioRecorder", "AudioPlayer", 
    "WASAPILoopbackRecorder", "DeviceInfo",
    
    # Exceptions
    "PyPAudioNativeError", "DeviceError", "RecordingError",
    "PlaybackError", "FileError",
]