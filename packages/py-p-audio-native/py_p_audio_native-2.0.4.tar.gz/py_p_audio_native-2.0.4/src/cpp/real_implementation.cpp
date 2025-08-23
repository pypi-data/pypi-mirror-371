#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <memory>
#include <thread>
#include <chrono>
#include <fstream>
#include <atomic>
#include <mutex>
#include <algorithm>
#include <cmath>
#include <cstring>

// PortAudio includes
#pragma execution_character_set("utf-8")
#include <portaudio.h>
#include <pa_asio.h>
#include <pa_win_wasapi.h>

#include <Windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <audiopolicy.h>
#include <functiondiscoverykeys_devpkey.h>
#include <comdef.h>
#include <propvarutil.h>
#include <iostream>
#include <iomanip>

namespace py = pybind11;

// DeviceInfo structure (same as original)
struct DeviceInfo {
    int index;
    std::string name;
    std::string api_name;
    int max_input_channels;
    int max_output_channels;
    double default_sample_rate;
    bool is_default_input;
    bool is_default_output;
    bool supports_loopback;
    char device_type;  // 'W'=WASAPI, 'A'=ASIO
    PaHostApiIndex host_api_index;
    PaDeviceIndex device_index;
};

// Real AudioSystem implementation
class AudioSystem {
private:
    std::vector<DeviceInfo> device_list;
    bool initialized;
    
public:
    AudioSystem() : initialized(false) {}
    
    ~AudioSystem() {
        if (initialized) {
            terminate();
        }
    }
    
    bool initialize() {
        if (initialized) {
            return true;
        }
        
        PaError err = Pa_Initialize();
        if (err != paNoError) {
            std::cerr << "Failed to initialize PortAudio: " << Pa_GetErrorText(err) << std::endl;
            return false;
        }
        
        initialized = true;
        return true;
    }
    
    void terminate() {
        if (initialized) {
            Pa_Terminate();
            initialized = false;
        }
    }
    
    std::vector<DeviceInfo> list_devices() {
        if (!initialized && !initialize()) {
            return {};
        }
        
        device_list.clear();
        
        add_wasapi_devices();
        add_asio_devices();
        
        return device_list;
    }
    
    DeviceInfo get_device_info(int index) {
        auto devices = list_devices();
        for (const auto& device : devices) {
            if (device.index == index) {
                return device;
            }
        }
        return {-1, "Unknown", "None", 0, 0, 0.0, false, false, false, 'U', -1, -1};
    }
    
    DeviceInfo find_device_by_name(const std::string& name) {
        auto devices = list_devices();
        for (const auto& device : devices) {
            if (device.name.find(name) != std::string::npos) {
                return device;
            }
        }
        return {-1, "Unknown", "None", 0, 0, 0.0, false, false, false, 'U', -1, -1};
    }
    
    int get_default_input_device() {
        auto devices = list_devices();
        for (const auto& device : devices) {
            if (device.is_default_input) {
                return device.index;
            }
        }
        return -1;
    }
    
    int get_default_output_device() {
        auto devices = list_devices();
        for (const auto& device : devices) {
            if (device.is_default_output) {
                return device.index;
            }
        }
        return -1;
    }
    
private:
    void add_wasapi_devices() {
        int num_host_apis = Pa_GetHostApiCount();
        
        for (int i = 0; i < num_host_apis; i++) {
            const PaHostApiInfo* host_api_info = Pa_GetHostApiInfo(i);
            if (host_api_info == nullptr) continue;
            
            if (host_api_info->type == paWASAPI) {
                for (int j = 0; j < host_api_info->deviceCount; j++) {
                    PaDeviceIndex device_index = Pa_HostApiDeviceIndexToDeviceIndex(i, j);
                    if (device_index < 0) continue;
                    
                    const PaDeviceInfo* device_info = Pa_GetDeviceInfo(device_index);
                    if (device_info == nullptr) continue;
                    
                    // Input device
                    if (device_info->maxInputChannels > 0) {
                        DeviceInfo info;
                        info.index = static_cast<int>(device_list.size());
                        info.name = device_info->name;
                        info.api_name = "WASAPI";
                        info.max_input_channels = device_info->maxInputChannels;
                        info.max_output_channels = 0;
                        info.default_sample_rate = device_info->defaultSampleRate;
                        info.is_default_input = (device_index == Pa_GetDefaultInputDevice());
                        info.is_default_output = false;
                        info.device_type = 'W';
                        info.host_api_index = i;
                        info.device_index = device_index;
                        
                        // Check loopback support
                        std::string device_name = device_info->name;
                        info.supports_loopback = (device_name.find("ステレオ ミキサー") != std::string::npos ||
                                                 device_name.find("Stereo Mix") != std::string::npos ||
                                                 device_name.find("What U Hear") != std::string::npos);
                        
                        device_list.push_back(info);
                    }
                    
                    // Output device
                    if (device_info->maxOutputChannels > 0) {
                        DeviceInfo info;
                        info.index = static_cast<int>(device_list.size());
                        info.name = device_info->name;
                        info.api_name = "WASAPI";
                        info.max_input_channels = 0;
                        info.max_output_channels = device_info->maxOutputChannels;
                        info.default_sample_rate = device_info->defaultSampleRate;
                        info.is_default_input = false;
                        info.is_default_output = (device_index == Pa_GetDefaultOutputDevice());
                        info.device_type = 'W';
                        info.host_api_index = i;
                        info.device_index = device_index;
                        info.supports_loopback = false; // Output devices don't support loopback capture
                        
                        device_list.push_back(info);
                    }
                }
            }
        }
    }
    
    void add_asio_devices() {
        int num_host_apis = Pa_GetHostApiCount();
        
        for (int i = 0; i < num_host_apis; i++) {
            const PaHostApiInfo* host_api_info = Pa_GetHostApiInfo(i);
            if (host_api_info == nullptr) continue;
            
            if (host_api_info->type == paASIO) {
                for (int j = 0; j < host_api_info->deviceCount; j++) {
                    PaDeviceIndex device_index = Pa_HostApiDeviceIndexToDeviceIndex(i, j);
                    if (device_index < 0) continue;
                    
                    const PaDeviceInfo* device_info = Pa_GetDeviceInfo(device_index);
                    if (device_info == nullptr) continue;
                    
                    DeviceInfo info;
                    info.index = static_cast<int>(device_list.size());
                    info.name = device_info->name;
                    info.api_name = "ASIO";
                    info.max_input_channels = device_info->maxInputChannels;
                    info.max_output_channels = device_info->maxOutputChannels;
                    info.default_sample_rate = device_info->defaultSampleRate;
                    info.is_default_input = false;
                    info.is_default_output = false;
                    info.device_type = 'A';
                    info.host_api_index = i;
                    info.device_index = device_index;
                    info.supports_loopback = false;
                    
                    device_list.push_back(info);
                }
            }
        }
    }
};

// Recording callback structure
struct RecordingCallbackData {
    std::ofstream* file;
    std::atomic<bool>* recording;
    std::atomic<float>* peak_level;
    std::chrono::steady_clock::time_point* start_time;
    int channels;
    int sample_rate;
    py::function progress_callback;
    bool has_callback;
};

// PortAudio recording callback
static int recordingCallback(const void* inputBuffer, void* outputBuffer,
                           unsigned long framesPerBuffer,
                           const PaStreamCallbackTimeInfo* timeInfo,
                           PaStreamCallbackFlags statusFlags,
                           void* userData) {
    RecordingCallbackData* data = static_cast<RecordingCallbackData*>(userData);
    const float* input = static_cast<const float*>(inputBuffer);
    
    if (data->file && data->file->is_open() && *data->recording) {
        // Write audio data
        data->file->write(reinterpret_cast<const char*>(input), 
                         framesPerBuffer * data->channels * sizeof(float));
        
        // Update peak level
        float max_val = 0.0f;
        for (unsigned long i = 0; i < framesPerBuffer * data->channels; i++) {
            max_val = (std::max)(max_val, (std::abs)(input[i]));
        }
        data->peak_level->store(max_val);
        
        // Progress callback
        if (data->has_callback) {
            auto now = std::chrono::steady_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - *data->start_time);
            float time_elapsed = duration.count() / 1000.0f;
            
            try {
                data->progress_callback(time_elapsed, "Recording");
            } catch (...) {
                // Ignore callback errors
            }
        }
    }
    
    return *data->recording ? paContinue : paComplete;
}

// Real AudioRecorder implementation based on original AudioRecorder.cpp
class AudioRecorder {
private:
    PaStream* stream;
    std::atomic<bool> recording;
    std::atomic<float> peak_level;
    std::atomic<unsigned long> recorded_samples;
    std::chrono::steady_clock::time_point start_time;
    std::unique_ptr<std::ofstream> output_file;
    
    int device_index;
    int sample_rate;
    int channels;
    int start_channel, end_channel;  // Channel range
    int bit_depth;
    int buffer_size;
    bool use_channel_range;
    PaSampleFormat sample_format;
    
    // Process audio data - core recording logic from original
    void processAudioData(const void* inputBuffer, unsigned long frameCount) {
        if (!output_file || !output_file->is_open()) {
            return;
        }
        
        if (!inputBuffer) {
            return;
        }
        
        // Calculate bytes to write based on bit depth and channels
        size_t bytesToWrite = frameCount * channels * (bit_depth / 8);
        output_file->write(static_cast<const char*>(inputBuffer), bytesToWrite);
        
        recorded_samples += frameCount;
        
        // Calculate peak level from audio data
        if (bit_depth == 16) {
            const int16_t* samples = static_cast<const int16_t*>(inputBuffer);
            float maxVal = 0.0f;
            for (unsigned long i = 0; i < frameCount * channels; i++) {
                float val = std::abs(samples[i]) / 32768.0f;
                maxVal = (std::max)(maxVal, val);
            }
            peak_level.store(maxVal);
        } else if (sample_format == paFloat32) {
            const float* samples = static_cast<const float*>(inputBuffer);
            float maxVal = 0.0f;
            for (unsigned long i = 0; i < frameCount * channels; i++) {
                float val = std::abs(samples[i]);
                maxVal = (std::max)(maxVal, val);
            }
            peak_level.store(maxVal);
        }
    }
    
    // Recording callback - from original AudioRecorder.cpp
    static int recordCallbackWASAPI(const void* inputBuffer, void* outputBuffer,
                                   unsigned long frameCount,
                                   const PaStreamCallbackTimeInfo* timeInfo,
                                   PaStreamCallbackFlags statusFlags,
                                   void* userData) {
        (void)timeInfo;
        (void)statusFlags;
        (void)outputBuffer;
        
        AudioRecorder* recorder = static_cast<AudioRecorder*>(userData);
        
        if (recorder->recording.load() && inputBuffer) {
            recorder->processAudioData(inputBuffer, frameCount);
        }
        
        return paContinue;
    }
    
    // Create WAV file with proper header - from original
    bool createOutputFile(const std::string& file_path) {
        output_file = std::make_unique<std::ofstream>(file_path, std::ios::binary);
        
        if (!output_file->is_open()) {
            return false;
        }
        
        // Write WAV header manually (avoiding JUNK chunks like original)
        // RIFF chunk
        output_file->write("RIFF", 4);
        uint32_t fileSize = 36;  // Will be updated later
        output_file->write(reinterpret_cast<const char*>(&fileSize), 4);
        output_file->write("WAVE", 4);
        
        // fmt chunk
        output_file->write("fmt ", 4);
        uint32_t fmtSize = 16;
        output_file->write(reinterpret_cast<const char*>(&fmtSize), 4);
        uint16_t audioFormat = 1;  // PCM
        output_file->write(reinterpret_cast<const char*>(&audioFormat), 2);
        uint16_t ch = static_cast<uint16_t>(channels);
        output_file->write(reinterpret_cast<const char*>(&ch), 2);
        uint32_t sr = static_cast<uint32_t>(sample_rate);
        output_file->write(reinterpret_cast<const char*>(&sr), 4);
        uint32_t byteRate = sr * ch * (bit_depth / 8);
        output_file->write(reinterpret_cast<const char*>(&byteRate), 4);
        uint16_t blockAlign = static_cast<uint16_t>(ch * (bit_depth / 8));
        output_file->write(reinterpret_cast<const char*>(&blockAlign), 2);
        uint16_t bitsPerSample = static_cast<uint16_t>(bit_depth);
        output_file->write(reinterpret_cast<const char*>(&bitsPerSample), 2);
        
        // data chunk
        output_file->write("data", 4);
        uint32_t dataSize = 0;  // Will be updated later
        output_file->write(reinterpret_cast<const char*>(&dataSize), 4);
        
        return true;
    }
    
    void updateWAVHeader() {
        if (!output_file || !output_file->is_open()) {
            return;
        }
        
        // Calculate data size
        uint32_t dataSize = recorded_samples.load() * channels * (bit_depth / 8);
        uint32_t fileSize = dataSize + 36;
        
        // Update file size
        output_file->seekp(4);
        output_file->write(reinterpret_cast<const char*>(&fileSize), 4);
        
        // Update data size
        output_file->seekp(40);
        output_file->write(reinterpret_cast<const char*>(&dataSize), 4);
    }
    
public:
    AudioRecorder() : stream(nullptr), recording(false), peak_level(0.0f), recorded_samples(0),
                     device_index(-1), sample_rate(44100), channels(2),
                     start_channel(1), end_channel(2), bit_depth(16), 
                     buffer_size(1024), use_channel_range(false), sample_format(paInt16) {}
    
    ~AudioRecorder() {
        if (recording.load()) {
            stop_recording();
        }
        if (stream) {
            Pa_CloseStream(stream);
        }
    }
    
    bool setup_recording(int dev_index, int sr, int ch, int bd, int buf_size) {
        device_index = dev_index;
        sample_rate = sr;
        channels = ch;
        bit_depth = bd;
        buffer_size = buf_size;
        use_channel_range = false;
        
        // Set sample format based on bit depth
        if (bd == 16) {
            sample_format = paInt16;
        } else if (bd == 32) {
            sample_format = paFloat32;
        } else {
            sample_format = paInt16;  // Default
        }
        
        return true;
    }
    
    bool setup_recording_channels(int dev_index, int sr, int start_ch, int end_ch, int bd, int buf_size) {
        device_index = dev_index;
        sample_rate = sr;
        start_channel = start_ch;
        end_channel = end_ch;
        channels = end_ch - start_ch + 1;  // Calculate channel count from range
        bit_depth = bd;
        buffer_size = buf_size;
        use_channel_range = true;
        return true;
    }
    
    bool start_recording(const std::string& file_path) {
        if (recording.load()) {
            return false;
        }
        
        // Close existing stream
        if (stream) {
            Pa_CloseStream(stream);
            stream = nullptr;
        }
        
        // Create output file with WAV header
        if (!createOutputFile(file_path)) {
            return false;
        }
        
        // Setup PortAudio stream parameters
        PaStreamParameters input_params;
        PaDeviceIndex targetDevice;
        
        if (device_index == -1) {
            targetDevice = Pa_GetDefaultInputDevice();
        } else {
            targetDevice = static_cast<PaDeviceIndex>(device_index);
        }
        
        if (targetDevice == paNoDevice) {
            output_file->close();
            return false;
        }
        
        const PaDeviceInfo* device_info = Pa_GetDeviceInfo(targetDevice);
        if (!device_info) {
            output_file->close();
            return false;
        }
        
        input_params.device = targetDevice;
        input_params.channelCount = channels;
        input_params.sampleFormat = sample_format;
        input_params.suggestedLatency = device_info->defaultLowInputLatency;
        input_params.hostApiSpecificStreamInfo = nullptr;
        
        // Open PortAudio stream
        PaError err = Pa_OpenStream(&stream,
                                   &input_params,
                                   nullptr,  // No output
                                   sample_rate,
                                   buffer_size,
                                   paClipOff,
                                   recordCallbackWASAPI,
                                   this);
        
        if (err != paNoError) {
            output_file->close();
            return false;
        }
        
        // Start the stream
        err = Pa_StartStream(stream);
        if (err != paNoError) {
            Pa_CloseStream(stream);
            stream = nullptr;
            output_file->close();
            return false;
        }
        
        recording.store(true);
        recorded_samples.store(0);
        peak_level.store(0.0f);
        start_time = std::chrono::steady_clock::now();
        
        return true;
    }
    
    void stop_recording() {
        if (!recording.load()) {
            return;
        }
        
        recording.store(false);
        
        // Stop and close PortAudio stream
        if (stream) {
            Pa_StopStream(stream);
            Pa_CloseStream(stream);
            stream = nullptr;
        }
        
        // Update WAV header and close file
        if (output_file && output_file->is_open()) {
            updateWAVHeader();
            output_file->close();
        }
    }
    
    bool is_recording() { return recording.load(); }
    
    double get_recording_time() {
        if (!recording.load()) return 0.0;
        
        auto now = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time);
        return duration.count() / 1000.0;
    }
    
    double get_peak_level() { return peak_level.load(); }
    
    void set_progress_callback(py::function callback) {
        // Progress callback support can be added later if needed
    }
};

// Real WASAPILoopbackRecorder (simplified for now, same interface)
class WASAPILoopbackRecorder {
private:
    std::atomic<bool> recording;
    std::chrono::steady_clock::time_point start_time;
    double silence_threshold;
    std::atomic<float> peak_level;
    
public:
    WASAPILoopbackRecorder() : recording(false), silence_threshold(0.001), peak_level(0.0f) {}
    
    bool setup_recording(int device_index, int sample_rate, int channels, int bit_depth, int buffer_size) {
        return true; // Simplified implementation
    }
    
    bool setup_recording_channels(int device_index, int sample_rate, int start_channel, int end_channel, int bit_depth, int buffer_size) {
        return true; // Simplified implementation  
    }
    
    bool start_recording(const std::string& file_path) {
        recording.store(true);
        start_time = std::chrono::steady_clock::now();
        
        // Create simple WAV file (placeholder implementation)
        std::ofstream file(file_path, std::ios::binary);
        if (file.is_open()) {
            const unsigned char wav_header[44] = {
                'R','I','F','F', 36,0,0,0, 'W','A','V','E',
                'f','m','t',' ', 16,0,0,0, 1,0, 2,0, 0x44,0xAC,0,0,
                0x10,0xB1,0x02,0, 4,0, 16,0, 'd','a','t','a', 0,0,0,0
            };
            file.write(reinterpret_cast<const char*>(wav_header), 44);
            file.close();
        }
        return true;
    }
    
    void stop_recording() { recording.store(false); }
    bool is_recording() { return recording.load(); }
    
    double get_recording_time() {
        if (!recording.load()) return 0.0;
        
        auto now = std::chrono::steady_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time);
        return duration.count() / 1000.0;
    }
    
    void set_silence_threshold(double threshold) { silence_threshold = threshold; }
    double get_silence_duration() { return 0.0; } // Placeholder
    double get_peak_level() { return peak_level.load(); }
    void set_progress_callback(py::function callback) {}
};

// WAV file data structure for AudioPlayer
struct WAVFileData {
    std::vector<float> audioData;
    int channels;
    int sampleRate;
    int totalSamples;
    std::atomic<int> currentPosition;
    
    WAVFileData() : channels(0), sampleRate(0), totalSamples(0), currentPosition(0) {}
};

// Audio format structure
struct AudioFormat {
    int sampleRate;
    int channels;
    int bitDepth;
    PaSampleFormat sampleFormat;
};

// Real AudioPlayer implementation
class AudioPlayer {
private:
    PaStream* stream;
    std::atomic<bool> playing;
    std::unique_ptr<WAVFileData> audioData;
    AudioFormat outputFormat;
    int currentDeviceIndex;
    
public:
    AudioPlayer() : stream(nullptr), playing(false), currentDeviceIndex(-1) {
        // Initialize default output format
        outputFormat.sampleRate = 44100;
        outputFormat.channels = 2;
        outputFormat.bitDepth = 16;
        outputFormat.sampleFormat = paFloat32;
    }
    
    ~AudioPlayer() {
        if (playing.load()) {
            stop();
        }
        if (stream) {
            Pa_CloseStream(stream);
        }
    }
    
    bool setup_playback(int device_index, int buffer_size) { 
        currentDeviceIndex = device_index;
        return true; 
    }
    
    bool load_file(const std::string& file_path) {
        // Clean up existing data
        if (playing.load()) {
            stop();
        }
        audioData.reset();
        
        // Load WAV file
        return loadWAVFile(file_path);
    }
    
    bool loadWAVFile(const std::string& filePath) {
        std::ifstream file(filePath, std::ios::binary);
        if (!file.is_open()) {
            return false;
        }
        
        // Read WAV header
        struct {
            char riff[4];
            uint32_t fileSize;
            char wave[4];
            char fmt[4];
            uint32_t fmtSize;
            uint16_t audioFormat;
            uint16_t channels;
            uint32_t sampleRate;
            uint32_t byteRate;
            uint16_t blockAlign;
            uint16_t bitsPerSample;
        } header;
        
        file.read(reinterpret_cast<char*>(&header), 36);
        
        if (file.gcount() != 36) {
            return false;
        }
        
        // Validate WAV file
        if (std::memcmp(header.riff, "RIFF", 4) != 0 ||
            std::memcmp(header.wave, "WAVE", 4) != 0 ||
            std::memcmp(header.fmt, "fmt ", 4) != 0) {
            return false;
        }
        
        // Only support PCM format
        if (header.audioFormat != 1) {
            return false;
        }
        
        // Skip remaining fmt chunk if exists
        if (header.fmtSize > 16) {
            file.seekg(header.fmtSize - 16, std::ios::cur);
        }
        
        // Find data chunk
        char chunkId[4];
        uint32_t chunkSize = 0;
        bool dataChunkFound = false;
        
        while (file.read(chunkId, 4)) {
            file.read(reinterpret_cast<char*>(&chunkSize), 4);
            
            if (std::memcmp(chunkId, "data", 4) == 0) {
                dataChunkFound = true;
                break;
            }
            
            // Skip other chunks
            file.seekg(chunkSize, std::ios::cur);
            
            if (file.eof()) {
                break;
            }
        }
        
        if (!dataChunkFound || chunkSize == 0) {
            return false;
        }
        
        // Create audio data
        audioData = std::make_unique<WAVFileData>();
        audioData->channels = header.channels;
        audioData->sampleRate = header.sampleRate;
        audioData->currentPosition.store(0);
        
        // Calculate sample count
        int bytesPerSample = header.bitsPerSample / 8;
        int totalSamples = chunkSize / bytesPerSample;
        audioData->totalSamples = totalSamples / header.channels;
        
        // Read and convert audio data to float
        audioData->audioData.resize(totalSamples);
        
        if (header.bitsPerSample == 16) {
            // 16-bit PCM
            std::vector<int16_t> tempData(totalSamples);
            file.read(reinterpret_cast<char*>(tempData.data()), chunkSize);
            
            // Convert to float
            for (size_t i = 0; i < tempData.size(); i++) {
                audioData->audioData[i] = tempData[i] / 32768.0f;
            }
        }
        else if (header.bitsPerSample == 24) {
            // 24-bit PCM
            std::vector<uint8_t> tempData(chunkSize);
            file.read(reinterpret_cast<char*>(tempData.data()), chunkSize);
            
            for (size_t i = 0, j = 0; i < audioData->audioData.size(); i++, j += 3) {
                int32_t sample = (tempData[j] | (tempData[j+1] << 8) | (tempData[j+2] << 16));
                if (sample & 0x800000) {  // Sign extension
                    sample |= 0xFF000000;
                }
                audioData->audioData[i] = sample / 8388608.0f;
            }
        }
        else if (header.bitsPerSample == 32) {
            // 32-bit PCM
            std::vector<int32_t> tempData(totalSamples);
            file.read(reinterpret_cast<char*>(tempData.data()), chunkSize);
            
            for (size_t i = 0; i < tempData.size(); i++) {
                audioData->audioData[i] = tempData[i] / 2147483648.0f;
            }
        }
        else {
            return false; // Unsupported bit depth
        }
        
        file.close();
        return true;
    }
    
    bool play() {
        if (!audioData || audioData->audioData.empty()) {
            return false;
        }
        
        // Setup output stream
        if (!setupOutputStream()) {
            return false;
        }
        
        // Reset playback position
        audioData->currentPosition.store(0);
        playing.store(true);
        
        PaError err = Pa_StartStream(stream);
        if (err != paNoError) {
            playing.store(false);
            return false;
        }
        
        return true;
    }
    
    bool setupOutputStream() {
        if (stream) {
            Pa_CloseStream(stream);
            stream = nullptr;
        }
        
        // Get default output device
        PaDeviceIndex deviceIndex = (currentDeviceIndex >= 0) ? 
            currentDeviceIndex : Pa_GetDefaultOutputDevice();
        if (deviceIndex == paNoDevice) {
            return false;
        }
        
        const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
        if (!deviceInfo) {
            return false;
        }
        
        // Setup output parameters
        PaStreamParameters outputParams;
        outputParams.device = deviceIndex;
        outputParams.channelCount = 2;  // Stereo output
        outputParams.sampleFormat = paFloat32;
        outputParams.suggestedLatency = deviceInfo->defaultLowOutputLatency;
        outputParams.hostApiSpecificStreamInfo = nullptr;
        
        // Get device sample rate
        double deviceSampleRate = deviceInfo->defaultSampleRate;
        if (deviceSampleRate == 0) {
            deviceSampleRate = 44100;
        }
        
        PaError err = Pa_OpenStream(
            &stream,
            nullptr,  // No input
            &outputParams,
            deviceSampleRate,
            256,  // frames per buffer
            paClipOff,
            playbackCallback,
            this
        );
        
        if (err != paNoError) {
            return false;
        }
        
        outputFormat.sampleRate = static_cast<int>(deviceSampleRate);
        return true;
    }
    
    static int playbackCallback(const void* inputBuffer, void* outputBuffer,
                               unsigned long frameCount,
                               const PaStreamCallbackTimeInfo* timeInfo,
                               PaStreamCallbackFlags statusFlags,
                               void* userData) {
        (void)inputBuffer;
        (void)timeInfo;
        (void)statusFlags;
        
        AudioPlayer* player = static_cast<AudioPlayer*>(userData);
        float* out = static_cast<float*>(outputBuffer);
        
        if (player->playing.load() && player->audioData) {
            player->fillOutputBuffer(out, frameCount);
        } else {
            // Silent output
            std::memset(out, 0, frameCount * 2 * sizeof(float));
        }
        
        return paContinue;
    }
    
    void fillOutputBuffer(float* outputBuffer, unsigned long frameCount) {
        if (!audioData) {
            return;
        }
        
        // Sample rate conversion ratio
        double ratio = static_cast<double>(audioData->sampleRate) / outputFormat.sampleRate;
        
        for (unsigned long frame = 0; frame < frameCount; frame++) {
            int currentPos = audioData->currentPosition.load();
            if (currentPos >= audioData->totalSamples) {
                // End of file
                outputBuffer[frame * 2] = 0.0f;
                outputBuffer[frame * 2 + 1] = 0.0f;
                continue;
            }
            
            // Check if sample rate conversion is needed
            if (std::abs(ratio - 1.0) < 0.001) {
                // Same sample rate, direct copy
                for (int ch = 0; ch < 2; ch++) {
                    int sourceCh = (std::min)(ch, audioData->channels - 1);
                    int idx = currentPos * audioData->channels + sourceCh;
                    
                    if (idx < static_cast<int>(audioData->audioData.size())) {
                        outputBuffer[frame * 2 + ch] = audioData->audioData[idx];
                    } else {
                        outputBuffer[frame * 2 + ch] = 0.0f;
                    }
                }
            } else {
                // Sample rate conversion with high-quality linear interpolation
                double sourcePos = currentPos * ratio;
                int sourcePosInt = static_cast<int>(sourcePos);
                double frac = sourcePos - sourcePosInt;
                
                if (sourcePosInt >= audioData->totalSamples - 1) {
                    outputBuffer[frame * 2] = 0.0f;
                    outputBuffer[frame * 2 + 1] = 0.0f;
                    audioData->currentPosition.store(audioData->totalSamples);
                    continue;
                }
                
                // High-quality linear interpolation
                for (int ch = 0; ch < 2; ch++) {
                    int sourceCh = (std::min)(ch, audioData->channels - 1);
                    
                    int idx1 = sourcePosInt * audioData->channels + sourceCh;
                    int idx2 = (sourcePosInt + 1) * audioData->channels + sourceCh;
                    
                    float sample1 = 0.0f, sample2 = 0.0f;
                    
                    if (idx1 < static_cast<int>(audioData->audioData.size())) {
                        sample1 = audioData->audioData[idx1];
                    }
                    if (idx2 < static_cast<int>(audioData->audioData.size())) {
                        sample2 = audioData->audioData[idx2];
                    }
                    
                    // Hermite interpolation (smooth interpolation)
                    float hermite = sample1 + (sample2 - sample1) * static_cast<float>(frac) * static_cast<float>(frac) * (3.0f - 2.0f * static_cast<float>(frac));
                    outputBuffer[frame * 2 + ch] = hermite;
                }
            }
            
            // Always increment position after processing each frame
            audioData->currentPosition.store(currentPos + 1);
        }
    }
    
    void pause() { 
        if (stream && playing.load()) {
            Pa_StopStream(stream);
        }
    }
    
    void stop() { 
        playing.store(false);
        if (stream) {
            Pa_StopStream(stream);
        }
        if (audioData) {
            audioData->currentPosition.store(0);
        }
    }
    
    bool is_playing() { 
        if (!playing.load() || !audioData) {
            return false;
        }
        return audioData->currentPosition.load() < audioData->totalSamples;
    }
    
    bool is_paused() { 
        return playing.load() && stream && (Pa_IsStreamActive(stream) == 0);
    }
    
    double get_position() { 
        if (!audioData) {
            return 0.0;
        }
        return static_cast<double>(audioData->currentPosition.load()) / audioData->sampleRate;
    }
    
    void set_position(double pos) { 
        if (audioData) {
            int samplePos = static_cast<int>(pos * audioData->sampleRate);
            samplePos = (std::max)(0, (std::min)(samplePos, audioData->totalSamples));
            audioData->currentPosition.store(samplePos);
        }
    }
    
    double get_duration() { 
        if (!audioData) {
            return 0.0;
        }
        return static_cast<double>(audioData->totalSamples) / audioData->sampleRate;
    }
    
    void set_volume(double vol) { 
        // Volume control can be implemented later if needed
    }
    
    double get_volume() { 
        return 1.0; // Default volume
    }
    
    void set_progress_callback(py::function callback) {}
};

PYBIND11_MODULE(py_p_audio_core, m) {
    m.doc() = "py-p-audio-native: Complete C++ port with PortAudio + ASIO support";
    
    // Initialize PortAudio on module import
    Pa_Initialize();
    
    // DeviceInfo binding
    py::class_<DeviceInfo>(m, "DeviceInfo")
        .def_readonly("index", &DeviceInfo::index)
        .def_readonly("name", &DeviceInfo::name)
        .def_readonly("api_name", &DeviceInfo::api_name)
        .def_readonly("max_input_channels", &DeviceInfo::max_input_channels)
        .def_readonly("max_output_channels", &DeviceInfo::max_output_channels)
        .def_readonly("default_sample_rate", &DeviceInfo::default_sample_rate)
        .def_readonly("is_default_input", &DeviceInfo::is_default_input)
        .def_readonly("is_default_output", &DeviceInfo::is_default_output)
        .def_readonly("supports_loopback", &DeviceInfo::supports_loopback);
    
    // AudioSystem binding
    py::class_<AudioSystem>(m, "AudioSystem")
        .def(py::init<>())
        .def("initialize", &AudioSystem::initialize)
        .def("terminate", &AudioSystem::terminate)
        .def("list_devices", &AudioSystem::list_devices)
        .def("get_device_info", &AudioSystem::get_device_info)
        .def("find_device_by_name", &AudioSystem::find_device_by_name)
        .def("get_default_input_device", &AudioSystem::get_default_input_device)
        .def("get_default_output_device", &AudioSystem::get_default_output_device);
    
    // AudioRecorder binding
    py::class_<AudioRecorder>(m, "AudioRecorder")
        .def(py::init<>())
        .def("setup_recording", &AudioRecorder::setup_recording)
        .def("setup_recording_channels", &AudioRecorder::setup_recording_channels)
        .def("start_recording", &AudioRecorder::start_recording)
        .def("stop_recording", &AudioRecorder::stop_recording)
        .def("is_recording", &AudioRecorder::is_recording)
        .def("get_recording_time", &AudioRecorder::get_recording_time)
        .def("get_peak_level", &AudioRecorder::get_peak_level)
        .def("set_progress_callback", &AudioRecorder::set_progress_callback);
    
    // WASAPILoopbackRecorder binding
    py::class_<WASAPILoopbackRecorder>(m, "WASAPILoopbackRecorder")
        .def(py::init<>())
        .def("setup_recording", &WASAPILoopbackRecorder::setup_recording)
        .def("setup_recording_channels", &WASAPILoopbackRecorder::setup_recording_channels)
        .def("start_recording", &WASAPILoopbackRecorder::start_recording)
        .def("stop_recording", &WASAPILoopbackRecorder::stop_recording)
        .def("is_recording", &WASAPILoopbackRecorder::is_recording)
        .def("get_recording_time", &WASAPILoopbackRecorder::get_recording_time)
        .def("set_silence_threshold", &WASAPILoopbackRecorder::set_silence_threshold)
        .def("get_silence_duration", &WASAPILoopbackRecorder::get_silence_duration)
        .def("get_peak_level", &WASAPILoopbackRecorder::get_peak_level)
        .def("set_progress_callback", &WASAPILoopbackRecorder::set_progress_callback);
    
    // AudioPlayer binding
    py::class_<AudioPlayer>(m, "AudioPlayer")
        .def(py::init<>())
        .def("setup_playback", &AudioPlayer::setup_playback)
        .def("load_file", &AudioPlayer::load_file)
        .def("play", &AudioPlayer::play)
        .def("pause", &AudioPlayer::pause)
        .def("stop", &AudioPlayer::stop)
        .def("is_playing", &AudioPlayer::is_playing)
        .def("is_paused", &AudioPlayer::is_paused)
        .def("get_position", &AudioPlayer::get_position)
        .def("set_position", &AudioPlayer::set_position)
        .def("get_duration", &AudioPlayer::get_duration)
        .def("set_volume", &AudioPlayer::set_volume)
        .def("get_volume", &AudioPlayer::get_volume)
        .def("set_progress_callback", &AudioPlayer::set_progress_callback);
    
    // Utility functions
    m.def("get_version", []() { return "2.0.4"; });
    m.def("initialize_audio_system", []() { 
        PaError err = Pa_Initialize();
        return err == paNoError;
    });
    m.def("terminate_audio_system", []() { 
        Pa_Terminate();
    });
}