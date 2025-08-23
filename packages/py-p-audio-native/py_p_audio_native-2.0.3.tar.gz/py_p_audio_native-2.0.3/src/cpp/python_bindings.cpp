#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>

#include "AudioSystem.h"
#include "AudioRecorder.h"
#include "AudioPlayer.h"
#include "WASAPILoopbackRecorder.h"

namespace py = pybind11;

// Progress callback wrapper
class ProgressCallbackWrapper {
public:
    ProgressCallbackWrapper(py::function callback) : callback_(callback) {}
    
    void operator()(double progress, const std::string& status) {
        callback_(progress, status);
    }
    
private:
    py::function callback_;
};

PYBIND11_MODULE(py_p_audio_core, m) {
    m.doc() = "py-p-audio-native: High-performance audio library with native C++ core";
    
    // Device information structure
    py::class_<AudioSystem::DeviceInfo>(m, "DeviceInfo")
        .def_readonly("index", &AudioSystem::DeviceInfo::index)
        .def_readonly("name", &AudioSystem::DeviceInfo::name)
        .def_readonly("api_name", &AudioSystem::DeviceInfo::apiName)
        .def_readonly("max_input_channels", &AudioSystem::DeviceInfo::maxInputChannels)
        .def_readonly("max_output_channels", &AudioSystem::DeviceInfo::maxOutputChannels)
        .def_readonly("default_sample_rate", &AudioSystem::DeviceInfo::defaultSampleRate)
        .def_readonly("is_default_input", &AudioSystem::DeviceInfo::isDefaultInput)
        .def_readonly("is_default_output", &AudioSystem::DeviceInfo::isDefaultOutput)
        .def("__repr__", [](const AudioSystem::DeviceInfo &info) {
            return "<DeviceInfo index=" + std::to_string(info.index) + 
                   " name='" + info.name + "'>";
        });
    
    // AudioSystem class
    py::class_<AudioSystem>(m, "AudioSystem")
        .def(py::init<>())
        .def("initialize", &AudioSystem::initialize, 
             "Initialize PortAudio system")
        .def("terminate", &AudioSystem::terminate,
             "Terminate PortAudio system")
        .def("list_devices", &AudioSystem::listDevices,
             "Get list of all available audio devices")
        .def("get_device_info", &AudioSystem::getDeviceInfo,
             "Get detailed information about specific device",
             py::arg("device_index"))
        .def("find_device_by_name", &AudioSystem::findDeviceByName,
             "Find device by name pattern",
             py::arg("name_pattern"))
        .def("get_default_input_device", &AudioSystem::getDefaultInputDevice,
             "Get default input device index")
        .def("get_default_output_device", &AudioSystem::getDefaultOutputDevice,
             "Get default output device index");
    
    // AudioRecorder class
    py::class_<AudioRecorder>(m, "AudioRecorder")
        .def(py::init<>())
        .def("setup_recording", &AudioRecorder::setupRecording,
             "Setup recording parameters",
             py::arg("device_index") = -1,
             py::arg("sample_rate") = 44100,
             py::arg("channels") = 2,
             py::arg("bit_depth") = 16,
             py::arg("buffer_size") = 1024)
        .def("start_recording", &AudioRecorder::startRecording,
             "Start recording to file",
             py::arg("output_path"))
        .def("stop_recording", &AudioRecorder::stopRecording,
             "Stop recording and save file")
        .def("is_recording", &AudioRecorder::isRecording,
             "Check if currently recording")
        .def("get_recording_time", &AudioRecorder::getRecordingTime,
             "Get current recording time in seconds")
        .def("set_progress_callback", [](AudioRecorder& self, py::function callback) {
            self.setProgressCallback([callback](double progress, const std::string& status) {
                callback(progress, status);
            });
        }, "Set progress callback function")
        .def("get_peak_level", &AudioRecorder::getPeakLevel,
             "Get current peak audio level (0.0-1.0)");
    
    // WASAPILoopbackRecorder class
    py::class_<WASAPILoopbackRecorder>(m, "WASAPILoopbackRecorder")
        .def(py::init<>())
        .def("setup_recording", &WASAPILoopbackRecorder::setupRecording,
             "Setup loopback recording parameters",
             py::arg("device_index") = -1,
             py::arg("sample_rate") = 44100,
             py::arg("channels") = 2,
             py::arg("bit_depth") = 16,
             py::arg("buffer_size") = 1024)
        .def("start_recording", &WASAPILoopbackRecorder::startRecording,
             "Start loopback recording to file",
             py::arg("output_path"))
        .def("stop_recording", &WASAPILoopbackRecorder::stopRecording,
             "Stop loopback recording")
        .def("is_recording", &WASAPILoopbackRecorder::isRecording,
             "Check if currently recording")
        .def("get_recording_time", &WASAPILoopbackRecorder::getRecordingTime,
             "Get current recording time in seconds")
        .def("set_silence_threshold", &WASAPILoopbackRecorder::setSilenceThreshold,
             "Set silence detection threshold (0.0-1.0)",
             py::arg("threshold"))
        .def("get_silence_duration", &WASAPILoopbackRecorder::getSilenceDuration,
             "Get current silence duration in seconds")
        .def("set_progress_callback", [](WASAPILoopbackRecorder& self, py::function callback) {
            self.setProgressCallback([callback](double progress, const std::string& status) {
                callback(progress, status);
            });
        }, "Set progress callback function")
        .def("get_peak_level", &WASAPILoopbackRecorder::getPeakLevel,
             "Get current peak audio level (0.0-1.0)");
    
    // AudioPlayer class  
    py::class_<AudioPlayer>(m, "AudioPlayer")
        .def(py::init<>())
        .def("setup_playback", &AudioPlayer::setupPlayback,
             "Setup playback parameters",
             py::arg("device_index") = -1,
             py::arg("buffer_size") = 1024)
        .def("load_file", &AudioPlayer::loadFile,
             "Load audio file for playback",
             py::arg("file_path"))
        .def("play", &AudioPlayer::play,
             "Start playback")
        .def("pause", &AudioPlayer::pause,
             "Pause playback")
        .def("stop", &AudioPlayer::stop,
             "Stop playback")
        .def("is_playing", &AudioPlayer::isPlaying,
             "Check if currently playing")
        .def("is_paused", &AudioPlayer::isPaused,
             "Check if currently paused")
        .def("get_position", &AudioPlayer::getPosition,
             "Get current playback position in seconds")
        .def("set_position", &AudioPlayer::setPosition,
             "Set playback position in seconds",
             py::arg("position"))
        .def("get_duration", &AudioPlayer::getDuration,
             "Get total duration in seconds")
        .def("set_volume", &AudioPlayer::setVolume,
             "Set playback volume (0.0-1.0)",
             py::arg("volume"))
        .def("get_volume", &AudioPlayer::getVolume,
             "Get current playback volume")
        .def("set_progress_callback", [](AudioPlayer& self, py::function callback) {
            self.setProgressCallback([callback](double progress, const std::string& status) {
                callback(progress, status);
            });
        }, "Set progress callback function");
    
    // Utility functions
    m.def("get_version", []() {
        return "2.0.0";
    }, "Get library version");
    
    m.def("initialize_audio_system", []() {
        static AudioSystem system;
        return system.initialize();
    }, "Initialize global audio system");
    
    m.def("terminate_audio_system", []() {
        static AudioSystem system;
        system.terminate();
    }, "Terminate global audio system");
}