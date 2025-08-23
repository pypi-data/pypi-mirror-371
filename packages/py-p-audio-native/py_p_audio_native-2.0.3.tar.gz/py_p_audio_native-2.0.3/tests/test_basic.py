"""
Basic functionality tests for py-p-audio-native
"""

import pytest
import tempfile
import os
import time
from pathlib import Path

import py_p_audio_native as ppa


class TestBasicFunctionality:
    """Test basic library functionality"""
    
    def test_import(self):
        """Test that all modules import correctly"""
        assert ppa.__version__ == "2.0.0"
        assert hasattr(ppa, 'list_devices')
        assert hasattr(ppa, 'record')
        assert hasattr(ppa, 'play')
    
    def test_device_listing(self):
        """Test device listing functionality"""
        devices = ppa.list_devices()
        
        # Should have at least one device
        assert len(devices) > 0
        
        # Check device properties
        device = devices[0]
        assert isinstance(device.index, int)
        assert isinstance(device.name, str)
        assert isinstance(device.api_name, str)
        assert isinstance(device.max_input_channels, int)
        assert isinstance(device.max_output_channels, int)
        assert isinstance(device.default_sample_rate, float)
        assert isinstance(device.is_default_input, bool)
        assert isinstance(device.is_default_output, bool)
        
        # String representation
        assert str(device).startswith("AudioDevice(")
        assert repr(device).startswith("AudioDevice(")
    
    def test_device_info(self):
        """Test individual device info retrieval"""
        devices = ppa.list_devices()
        if devices:
            device = ppa.get_device_info(devices[0].index)
            assert device is not None
            assert device.index == devices[0].index
            assert device.name == devices[0].name
    
    def test_find_device(self):
        """Test device finding functionality"""
        devices = ppa.list_devices()
        if devices:
            # Find by partial name
            first_device = devices[0]
            name_part = first_device.name[:5]  # First 5 characters
            found = ppa.find_device(name_part)
            # May or may not find (depends on uniqueness)
            # Just test that function works
            assert found is None or isinstance(found, ppa.AudioDevice)


class TestRecording:
    """Test audio recording functionality"""
    
    def test_simple_recording(self):
        """Test simple recording function"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Record for 0.5 seconds
            success = ppa.record(0.5, tmp_path)
            assert success is True
            
            # Check file was created
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 44  # Should be larger than WAV header
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_recording_with_parameters(self):
        """Test recording with custom parameters"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Record with custom settings
            success = ppa.record(
                duration=0.2,
                output_file=tmp_path,
                sample_rate=48000,
                channels=1,
                bit_depth=16
            )
            assert success is True
            assert os.path.exists(tmp_path)
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_recorder_class(self):
        """Test advanced Recorder class"""
        recorder = ppa.Recorder(
            sample_rate=44100,
            channels=2,
            bit_depth=16
        )
        
        # Test setup
        recorder.setup()
        
        # Test recorder properties before recording
        assert not recorder.is_recording()
        assert recorder.get_recording_time() == 0.0
        assert recorder.get_peak_level() >= 0.0
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Test continuous recording
            success = recorder.start_recording(tmp_path)
            assert success is True
            assert recorder.is_recording()
            
            # Record for short time
            time.sleep(0.2)
            
            # Check recording state
            assert recorder.get_recording_time() > 0.0
            
            # Stop recording
            recorder.stop_recording()
            assert not recorder.is_recording()
            assert os.path.exists(tmp_path)
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_loopback_recording(self):
        """Test loopback recording functionality"""
        # Find output devices for loopback
        devices = ppa.list_devices()
        output_devices = [d for d in devices if d.max_output_channels > 0]
        
        if not output_devices:
            pytest.skip("No output devices available for loopback test")
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Test simple loopback recording
            success = ppa.record_loopback(
                duration=0.2,
                output_file=tmp_path,
                device_index=output_devices[0].index
            )
            assert success is True
            assert os.path.exists(tmp_path)
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_loopback_recorder_class(self):
        """Test LoopbackRecorder class"""
        devices = ppa.list_devices()
        output_devices = [d for d in devices if d.max_output_channels > 0]
        
        if not output_devices:
            pytest.skip("No output devices available for loopback test")
        
        recorder = ppa.LoopbackRecorder(device_index=output_devices[0].index)
        recorder.setup()
        
        # Test silence detection
        recorder.set_silence_threshold(0.01)
        assert recorder.get_silence_duration() >= 0.0
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            success = recorder.start_recording(tmp_path)
            assert success is True
            
            time.sleep(0.1)
            
            recorder.stop_recording()
            assert os.path.exists(tmp_path)
            
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestPlayback:
    """Test audio playback functionality"""
    
    @pytest.fixture
    def sample_audio_file(self):
        """Create a sample audio file for testing"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Record a short sample
        ppa.record(0.2, tmp_path)
        yield tmp_path
        
        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    def test_simple_playback(self, sample_audio_file):
        """Test simple playback function"""
        success = ppa.play(sample_audio_file)
        assert success is True
        
        # Give it time to start playing
        time.sleep(0.1)
    
    def test_playback_with_callback(self, sample_audio_file):
        """Test playback with progress callback"""
        callback_called = False
        
        def progress_callback(progress: float, status: str):
            nonlocal callback_called
            callback_called = True
            assert isinstance(progress, float)
            assert isinstance(status, str)
            assert 0.0 <= progress <= 1.0
        
        success = ppa.play_with_callback(sample_audio_file, progress_callback)
        assert success is True
        
        time.sleep(0.1)
        assert callback_called
    
    def test_player_class(self, sample_audio_file):
        """Test advanced Player class"""
        player = ppa.Player()
        player.setup()
        
        # Test initial state
        assert not player.is_playing()
        assert not player.is_paused()
        
        # Test playback
        success = player.play(sample_audio_file)
        assert success is True
        
        # Give time to start
        time.sleep(0.05)
        
        # Test state during playback
        if player.is_playing():
            assert player.get_position() >= 0.0
            assert player.get_duration() > 0.0
            
            # Test volume control
            original_volume = player.get_volume()
            player.set_volume(0.5)
            assert abs(player.get_volume() - 0.5) < 0.1
            player.set_volume(original_volume)
            
            # Test pause/resume
            player.pause()
            time.sleep(0.02)
            assert player.is_paused()
            
            player.play(sample_audio_file)  # Resume
            time.sleep(0.02)
            
        # Test stop
        player.stop()
        time.sleep(0.02)
        assert not player.is_playing()


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_device_index(self):
        """Test handling of invalid device indices"""
        with pytest.raises(ppa.DeviceError):
            ppa.record(0.1, "test.wav", device_index=9999)
    
    def test_invalid_file_path(self):
        """Test handling of invalid file paths"""
        with pytest.raises((ppa.FileError, ppa.PlaybackError)):
            ppa.play("/nonexistent/file.wav")
    
    def test_invalid_recording_parameters(self):
        """Test handling of invalid recording parameters"""
        recorder = ppa.Recorder(sample_rate=0)  # Invalid sample rate
        
        with pytest.raises(ppa.RecordingError):
            recorder.setup()


class TestPerformance:
    """Performance and stress tests"""
    
    def test_multiple_short_recordings(self):
        """Test multiple short recordings in sequence"""
        for i in range(5):
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                success = ppa.record(0.1, tmp_path)
                assert success is True
                assert os.path.exists(tmp_path)
                
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    def test_device_enumeration_performance(self):
        """Test that device enumeration is reasonably fast"""
        start_time = time.time()
        
        for _ in range(10):
            devices = ppa.list_devices()
            assert len(devices) > 0
        
        elapsed = time.time() - start_time
        # Should complete 10 enumerations in under 1 second
        assert elapsed < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])