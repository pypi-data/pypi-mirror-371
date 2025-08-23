"""
High-level Python API for py-p-audio-native

Provides convenient wrapper functions around the native C++ core.
"""

import time
from typing import List, Optional, Callable, Union
from pathlib import Path

from . import py_p_audio_core
from .exceptions import DeviceError, RecordingError, PlaybackError, FileError


class AudioDevice:
    """Wrapper for device information with additional Python conveniences"""
    
    def __init__(self, device_info: py_p_audio_core.DeviceInfo):
        self._info = device_info
    
    @property
    def index(self) -> int:
        """Device index"""
        return self._info.index
    
    @property 
    def name(self) -> str:
        """Device name"""
        return self._info.name
    
    @property
    def api_name(self) -> str:
        """Audio API name (WASAPI, ASIO, etc.)"""
        return self._info.api_name
    
    @property
    def max_input_channels(self) -> int:
        """Maximum input channels"""
        return self._info.max_input_channels
    
    @property
    def max_output_channels(self) -> int:
        """Maximum output channels"""
        return self._info.max_output_channels
    
    @property
    def default_sample_rate(self) -> float:
        """Default sample rate"""
        return self._info.default_sample_rate
    
    @property
    def is_default_input(self) -> bool:
        """True if this is the default input device"""
        return self._info.is_default_input
    
    @property
    def is_default_output(self) -> bool:
        """True if this is the default output device"""
        return self._info.is_default_output
    
    def __str__(self):
        return f"AudioDevice({self.index}: {self.name})"
    
    def __repr__(self):
        return f"AudioDevice(index={self.index}, name='{self.name}', api='{self.api_name}')"


class ProgressCallback:
    """Progress callback wrapper for easier Python usage"""
    
    def __init__(self, callback_func: Callable[[float, str], None]):
        self.callback_func = callback_func
    
    def __call__(self, progress: float, status: str):
        """Called by C++ code with progress updates"""
        self.callback_func(progress, status)


class Recorder:
    """High-level audio recorder with Python conveniences"""
    
    def __init__(self, device_index: Optional[int] = None, 
                 sample_rate: int = 44100, channels: int = 2, 
                 bit_depth: int = 16, buffer_size: int = 1024):
        """
        Initialize recorder.
        
        Args:
            device_index: Input device index (None for default)
            sample_rate: Sample rate in Hz
            channels: Number of channels
            bit_depth: Bit depth (16, 24, 32)
            buffer_size: Buffer size in frames
        """
        self._recorder = py_p_audio_core.AudioRecorder()
        self._device_index = device_index or -1
        self._sample_rate = sample_rate
        self._channels = channels
        self._bit_depth = bit_depth
        self._buffer_size = buffer_size
        self._is_setup = False
    
    def setup(self):
        """Setup the recorder with specified parameters"""
        success = self._recorder.setup_recording(
            self._device_index, self._sample_rate, self._channels, 
            self._bit_depth, self._buffer_size
        )
        if not success:
            raise RecordingError("Failed to setup recording parameters")
        self._is_setup = True
    
    def record(self, duration: float, output_file: Union[str, Path], 
               progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        """
        Record audio for specified duration.
        
        Args:
            duration: Recording duration in seconds
            output_file: Output file path
            progress_callback: Optional progress callback function
            
        Returns:
            True if recording succeeded
        """
        if not self._is_setup:
            self.setup()
        
        if progress_callback:
            self._recorder.set_progress_callback(ProgressCallback(progress_callback))
        
        # Start recording
        success = self._recorder.start_recording(str(output_file))
        if not success:
            raise RecordingError("Failed to start recording")
        
        # Wait for duration
        time.sleep(duration)
        
        # Stop recording
        self._recorder.stop_recording()
        return True
    
    def start_recording(self, output_file: Union[str, Path]) -> bool:
        """Start continuous recording"""
        if not self._is_setup:
            self.setup()
        
        success = self._recorder.start_recording(str(output_file))
        if not success:
            raise RecordingError("Failed to start recording")
        return True
    
    def stop_recording(self):
        """Stop continuous recording"""
        self._recorder.stop_recording()
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._recorder.is_recording()
    
    def get_recording_time(self) -> float:
        """Get current recording time in seconds"""
        return self._recorder.get_recording_time()
    
    def get_peak_level(self) -> float:
        """Get current peak level (0.0-1.0)"""
        return self._recorder.get_peak_level()
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Set progress callback function"""
        self._recorder.set_progress_callback(ProgressCallback(callback))


class LoopbackRecorder:
    """High-level loopback recorder for system audio capture"""
    
    def __init__(self, device_index: Optional[int] = None,
                 sample_rate: int = 44100, channels: int = 2,
                 bit_depth: int = 16, buffer_size: int = 1024):
        """
        Initialize loopback recorder.
        
        Args:
            device_index: Output device index to capture (None for default)
            sample_rate: Sample rate in Hz  
            channels: Number of channels
            bit_depth: Bit depth (16, 24, 32)
            buffer_size: Buffer size in frames
        """
        self._recorder = py_p_audio_core.WASAPILoopbackRecorder()
        self._device_index = device_index or -1
        self._sample_rate = sample_rate
        self._channels = channels
        self._bit_depth = bit_depth
        self._buffer_size = buffer_size
        self._is_setup = False
    
    def setup(self):
        """Setup the loopback recorder"""
        success = self._recorder.setup_recording(
            self._device_index, self._sample_rate, self._channels,
            self._bit_depth, self._buffer_size
        )
        if not success:
            raise RecordingError("Failed to setup loopback recording")
        self._is_setup = True
    
    def record(self, duration: float, output_file: Union[str, Path],
               progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        """Record system audio for specified duration"""
        if not self._is_setup:
            self.setup()
        
        if progress_callback:
            self._recorder.set_progress_callback(ProgressCallback(progress_callback))
        
        success = self._recorder.start_recording(str(output_file))
        if not success:
            raise RecordingError("Failed to start loopback recording")
        
        time.sleep(duration)
        self._recorder.stop_recording()
        return True
    
    def start_recording(self, output_file: Union[str, Path]) -> bool:
        """Start continuous loopback recording"""
        if not self._is_setup:
            self.setup()
        
        success = self._recorder.start_recording(str(output_file))
        if not success:
            raise RecordingError("Failed to start loopback recording")
        return True
    
    def stop_recording(self):
        """Stop loopback recording"""
        self._recorder.stop_recording()
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._recorder.is_recording()
    
    def get_recording_time(self) -> float:
        """Get current recording time in seconds"""
        return self._recorder.get_recording_time()
    
    def set_silence_threshold(self, threshold: float):
        """Set silence detection threshold (0.0-1.0)"""
        self._recorder.set_silence_threshold(threshold)
    
    def get_silence_duration(self) -> float:
        """Get current silence duration in seconds"""
        return self._recorder.get_silence_duration()
    
    def get_peak_level(self) -> float:
        """Get current peak level (0.0-1.0)"""
        return self._recorder.get_peak_level()


class Player:
    """High-level audio player"""
    
    def __init__(self, device_index: Optional[int] = None, buffer_size: int = 1024):
        """
        Initialize audio player.
        
        Args:
            device_index: Output device index (None for default)
            buffer_size: Buffer size in frames
        """
        self._player = py_p_audio_core.AudioPlayer()
        self._device_index = device_index or -1
        self._buffer_size = buffer_size
        self._is_setup = False
    
    def setup(self):
        """Setup the audio player"""
        success = self._player.setup_playback(self._device_index, self._buffer_size)
        if not success:
            raise PlaybackError("Failed to setup audio playback")
        self._is_setup = True
    
    def play(self, file_path: Union[str, Path], 
             progress_callback: Optional[Callable[[float, str], None]] = None) -> bool:
        """
        Play audio file.
        
        Args:
            file_path: Audio file to play
            progress_callback: Optional progress callback
            
        Returns:
            True if playback succeeded
        """
        if not self._is_setup:
            self.setup()
        
        # Load file
        success = self._player.load_file(str(file_path))
        if not success:
            raise FileError(f"Failed to load audio file: {file_path}")
        
        if progress_callback:
            self._player.set_progress_callback(ProgressCallback(progress_callback))
        
        # Start playback
        success = self._player.play()
        if not success:
            raise PlaybackError("Failed to start playback")
        
        return True
    
    def pause(self):
        """Pause playback"""
        self._player.pause()
    
    def stop(self):
        """Stop playback"""
        self._player.stop()
    
    def is_playing(self) -> bool:
        """Check if currently playing"""
        return self._player.is_playing()
    
    def is_paused(self) -> bool:
        """Check if currently paused"""
        return self._player.is_paused()
    
    def get_position(self) -> float:
        """Get current playback position in seconds"""
        return self._player.get_position()
    
    def set_position(self, position: float):
        """Set playback position in seconds"""
        self._player.set_position(position)
    
    def get_duration(self) -> float:
        """Get total duration in seconds"""
        return self._player.get_duration()
    
    def set_volume(self, volume: float):
        """Set playback volume (0.0-1.0)"""
        self._player.set_volume(volume)
    
    def get_volume(self) -> float:
        """Get current playback volume"""
        return self._player.get_volume()


# High-level convenience functions

def list_devices() -> List[AudioDevice]:
    """List all available audio devices"""
    py_p_audio_core.initialize_audio_system()
    system = py_p_audio_core.AudioSystem()
    system.initialize()
    
    try:
        device_infos = system.list_devices()
        return [AudioDevice(info) for info in device_infos]
    finally:
        system.terminate()


def get_device_info(device_index: int) -> Optional[AudioDevice]:
    """Get information about specific device"""
    py_p_audio_core.initialize_audio_system()
    system = py_p_audio_core.AudioSystem()
    system.initialize()
    
    try:
        info = system.get_device_info(device_index)
        return AudioDevice(info) if info else None
    finally:
        system.terminate()


def find_device(name_pattern: str) -> Optional[AudioDevice]:
    """Find device by name pattern"""
    py_p_audio_core.initialize_audio_system()
    system = py_p_audio_core.AudioSystem()
    system.initialize()
    
    try:
        info = system.find_device_by_name(name_pattern)
        return AudioDevice(info) if info else None
    finally:
        system.terminate()


def record(duration: float, output_file: Union[str, Path], 
           device_index: Optional[int] = None, sample_rate: int = 44100,
           channels: int = 2, bit_depth: int = 16) -> bool:
    """
    Simple audio recording function.
    
    Args:
        duration: Recording duration in seconds
        output_file: Output file path
        device_index: Input device index (None for default)
        sample_rate: Sample rate in Hz
        channels: Number of channels
        bit_depth: Bit depth
        
    Returns:
        True if recording succeeded
    """
    recorder = Recorder(device_index, sample_rate, channels, bit_depth)
    return recorder.record(duration, output_file)


def record_loopback(duration: float, output_file: Union[str, Path],
                    device_index: Optional[int] = None, sample_rate: int = 44100,
                    channels: int = 2, bit_depth: int = 16) -> bool:
    """
    Simple loopback recording function.
    
    Args:
        duration: Recording duration in seconds
        output_file: Output file path
        device_index: Output device index to capture (None for default)
        sample_rate: Sample rate in Hz
        channels: Number of channels  
        bit_depth: Bit depth
        
    Returns:
        True if recording succeeded
    """
    recorder = LoopbackRecorder(device_index, sample_rate, channels, bit_depth)
    return recorder.record(duration, output_file)


def play(file_path: Union[str, Path], device_index: Optional[int] = None) -> bool:
    """
    Simple audio playback function.
    
    Args:
        file_path: Audio file to play
        device_index: Output device index (None for default)
        
    Returns:
        True if playback succeeded
    """
    player = Player(device_index)
    return player.play(file_path)


def play_with_callback(file_path: Union[str, Path], 
                      progress_callback: Callable[[float, str], None],
                      device_index: Optional[int] = None) -> bool:
    """
    Play audio file with progress callback.
    
    Args:
        file_path: Audio file to play
        progress_callback: Progress callback function
        device_index: Output device index (None for default)
        
    Returns:
        True if playback succeeded
    """
    player = Player(device_index)
    return player.play(file_path, progress_callback)