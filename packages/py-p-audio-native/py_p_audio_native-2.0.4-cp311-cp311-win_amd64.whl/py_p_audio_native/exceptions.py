"""
Exception classes for py-p-audio-native
"""


class PyPAudioNativeError(Exception):
    """Base exception for all py-p-audio-native errors"""
    pass


class DeviceError(PyPAudioNativeError):
    """Raised when there are issues with audio devices"""
    pass


class RecordingError(PyPAudioNativeError):
    """Raised when there are issues with audio recording"""
    pass


class PlaybackError(PyPAudioNativeError):
    """Raised when there are issues with audio playback"""
    pass


class FileError(PyPAudioNativeError):
    """Raised when there are issues with audio files"""
    pass