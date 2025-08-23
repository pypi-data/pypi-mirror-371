# py-p-audio-native API Reference

## Overview

py-p-audio-native is a high-performance Python audio library with zero external dependencies, powered by native C++ implementation using PortAudio and ASIO SDK.

## Installation

```bash
pip install py-p-audio-native
```

## Quick Start

```python
import py_p_audio_native as ppa

# List available devices
devices = ppa.list_devices()
print(f"Found {len(devices)} devices")

# Simple recording
ppa.record(duration=5.0, output_file="test.wav")

# System audio recording (loopback)
ppa.record_loopback(duration=3.0, output_file="system_audio.wav")

# Audio playback
ppa.play("test.wav")
```

## High-Level API

### Device Management

#### `list_devices() -> List[AudioDevice]`

List all available audio devices.

```python
devices = ppa.list_devices()
for device in devices:
    print(f"{device.index}: {device.name} ({device.api_name})")
    print(f"  Input channels: {device.max_input_channels}")
    print(f"  Output channels: {device.max_output_channels}")
    print(f"  Default sample rate: {device.default_sample_rate}")
```

#### `get_device_info(device_index: int) -> Optional[AudioDevice]`

Get detailed information about a specific device.

```python
device = ppa.get_device_info(0)
if device:
    print(f"Device: {device.name}")
    print(f"API: {device.api_name}")
```

#### `find_device(name_pattern: str) -> Optional[AudioDevice]`

Find device by name pattern.

```python
device = ppa.find_device("Speakers")
if device:
    print(f"Found speakers: {device.name}")
```

### Simple Recording Functions

#### `record(duration, output_file, device_index=None, sample_rate=44100, channels=2, bit_depth=16) -> bool`

Record audio for specified duration.

**Parameters:**
- `duration` (float): Recording duration in seconds
- `output_file` (str|Path): Output file path
- `device_index` (int, optional): Input device index (None for default)
- `sample_rate` (int): Sample rate in Hz (default: 44100)
- `channels` (int): Number of channels (default: 2)
- `bit_depth` (int): Bit depth - 16, 24, or 32 (default: 16)

**Returns:** True if recording succeeded

```python
# Record 10 seconds from default device
success = ppa.record(10.0, "recording.wav")

# Record from specific device with custom settings
success = ppa.record(
    duration=5.0,
    output_file="high_quality.wav",
    device_index=1,
    sample_rate=48000,
    channels=1,
    bit_depth=24
)
```

#### `record_loopback(duration, output_file, device_index=None, sample_rate=44100, channels=2, bit_depth=16) -> bool`

Record system audio (loopback recording).

**Parameters:** Same as `record()` but `device_index` refers to output device to capture

```python
# Record system audio for 30 seconds
success = ppa.record_loopback(30.0, "system_audio.wav")

# Record from specific output device
success = ppa.record_loopback(
    duration=10.0,
    output_file="speakers.wav", 
    device_index=0  # Output device to capture
)
```

### Simple Playback Functions

#### `play(file_path, device_index=None) -> bool`

Play audio file.

**Parameters:**
- `file_path` (str|Path): Audio file path
- `device_index` (int, optional): Output device index (None for default)

```python
# Play audio file
success = ppa.play("recording.wav")

# Play on specific device
success = ppa.play("music.wav", device_index=1)
```

#### `play_with_callback(file_path, progress_callback, device_index=None) -> bool`

Play audio file with progress monitoring.

```python
def progress_callback(progress: float, status: str):
    print(f"Progress: {progress*100:.1f}% - {status}")

success = ppa.play_with_callback("song.wav", progress_callback)
```

## Advanced Classes

### AudioDevice

Represents an audio device with detailed information.

**Properties:**
- `index` (int): Device index
- `name` (str): Device name  
- `api_name` (str): Audio API name (WASAPI, ASIO, etc.)
- `max_input_channels` (int): Maximum input channels
- `max_output_channels` (int): Maximum output channels
- `default_sample_rate` (float): Default sample rate
- `is_default_input` (bool): True if default input device
- `is_default_output` (bool): True if default output device

### Recorder

Advanced audio recorder with full control.

```python
# Create recorder
recorder = ppa.Recorder(
    device_index=0,
    sample_rate=48000,
    channels=2,
    bit_depth=24,
    buffer_size=512  # Low latency
)

# Start recording
recorder.start_recording("output.wav")

# Monitor recording
while recorder.is_recording():
    time.sleep(0.1)
    peak = recorder.get_peak_level()
    duration = recorder.get_recording_time()
    print(f"Recording: {duration:.1f}s, Peak: {peak:.2f}")
    
    if duration >= 10.0:  # Stop after 10 seconds
        recorder.stop_recording()
        break
```

**Methods:**
- `setup()`: Setup recorder with parameters
- `record(duration, output_file, progress_callback=None) -> bool`: Record for duration
- `start_recording(output_file) -> bool`: Start continuous recording
- `stop_recording()`: Stop recording
- `is_recording() -> bool`: Check if recording
- `get_recording_time() -> float`: Get recording time in seconds
- `get_peak_level() -> float`: Get current peak level (0.0-1.0)
- `set_progress_callback(callback)`: Set progress callback

### LoopbackRecorder

Advanced loopback recorder for system audio capture.

```python
# Create loopback recorder
recorder = ppa.LoopbackRecorder(
    device_index=0,  # Output device to capture
    sample_rate=44100,
    channels=2
)

# Setup silence detection
recorder.setup()
recorder.set_silence_threshold(0.01)

# Start recording
recorder.start_recording("system_capture.wav")

# Stop when silence detected for 3 seconds
while recorder.is_recording():
    silence_duration = recorder.get_silence_duration()
    if silence_duration >= 3.0:
        recorder.stop_recording()
        break
    time.sleep(0.1)
```

**Methods:**
- All methods from `Recorder` class
- `set_silence_threshold(threshold)`: Set silence detection threshold (0.0-1.0)
- `get_silence_duration() -> float`: Get current silence duration in seconds

### Player

Advanced audio player with full control.

```python
# Create player
player = ppa.Player(device_index=0, buffer_size=1024)

# Load and play file
player.setup()
player.play("music.wav")

# Control playback
time.sleep(5.0)
player.pause()
time.sleep(2.0)
player.play()  # Resume

# Monitor playback
while player.is_playing():
    position = player.get_position()
    duration = player.get_duration()
    progress = position / duration if duration > 0 else 0
    print(f"Progress: {progress*100:.1f}% ({position:.1f}/{duration:.1f}s)")
    time.sleep(1.0)
```

**Methods:**
- `setup()`: Setup player
- `play(file_path, progress_callback=None) -> bool`: Load and play file
- `pause()`: Pause playback
- `stop()`: Stop playback
- `is_playing() -> bool`: Check if playing
- `is_paused() -> bool`: Check if paused
- `get_position() -> float`: Get playback position in seconds
- `set_position(position)`: Set playback position
- `get_duration() -> float`: Get total duration in seconds
- `set_volume(volume)`: Set volume (0.0-1.0)
- `get_volume() -> float`: Get current volume

## Progress Callbacks

Progress callbacks receive two parameters:

```python
def my_callback(progress: float, status: str):
    """
    Args:
        progress: Progress value 0.0-1.0
        status: Status string (e.g., "Recording", "Playing", "Complete")
    """
    print(f"{status}: {progress*100:.1f}%")
```

## Error Handling

```python
import py_p_audio_native as ppa
from py_p_audio_native import RecordingError, PlaybackError, DeviceError, FileError

try:
    ppa.record(5.0, "test.wav", device_index=999)
except DeviceError as e:
    print(f"Device error: {e}")
except RecordingError as e:
    print(f"Recording error: {e}")
except FileError as e:
    print(f"File error: {e}")
```

**Exception Classes:**
- `PyPAudioNativeError`: Base exception
- `DeviceError`: Device-related errors
- `RecordingError`: Recording-related errors
- `PlaybackError`: Playback-related errors
- `FileError`: File I/O related errors

## Performance Notes

### Zero Dependencies
Unlike other Python audio libraries, py-p-audio-native has no external dependencies:

```bash
# Other libraries
pip install pyaudio sounddevice soundfile numpy  # 50MB+

# py-p-audio-native
pip install py-p-audio-native  # ~5MB total
```

### Native Performance
- **Recording latency**: ~5ms (vs ~50ms for Python-only solutions)
- **Memory usage**: ~5MB (vs ~50MB for dependency-heavy solutions)
- **CPU usage**: Minimal overhead due to native C++ core

### Supported Formats
- **Sample rates**: 8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 192000 Hz
- **Bit depths**: 16, 24, 32-bit
- **Channels**: 1 (mono) to device maximum
- **File format**: WAV (uncompressed PCM)

## Platform Support

### Windows
- **WASAPI**: Full support including loopback recording
- **ASIO**: Professional audio interface support
- **Requirements**: Windows 10/11, Visual C++ Redistributable

### Future Platforms
- macOS and Linux support planned for future releases

## Migration Guide

### From py-p-audio (old version)

The new native version maintains API compatibility while removing dependencies:

```python
# Old version (with dependencies)
import py_p_audio as ppa  # Required: PyAudioWPatch, sounddevice, soundfile, numpy

devices = ppa.list_audio_devices()  # Complex device detection
ppa.record(5.0, "test.wav")         # Multiple library calls

# New native version (zero dependencies)
import py_p_audio_native as ppa  # No dependencies required

devices = ppa.list_devices()     # Native C++ device detection
ppa.record(5.0, "test.wav")      # Single native call
```

**Breaking Changes:**
- Package name: `py_p_audio` → `py_p_audio_native`
- Function name: `list_audio_devices()` → `list_devices()`
- No more Unicode/emoji issues in output
- Device information structure updated

**Benefits:**
- 10x faster performance
- 90% smaller installation size  
- No dependency conflicts
- Better error messages
- Native Windows audio API support