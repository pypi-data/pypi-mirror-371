#pragma execution_character_set("utf-8")
#include "AudioRecorder.h"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <ctime>
#include <chrono>
#include <cstring>
#include <Windows.h>

AudioRecorder::AudioRecorder() 
    : stream(nullptr), recording(false), recordedSamples(0),
      startChannelIndex(0), endChannelIndex(0), channelCount(2),
      usingWASAPILoopback(false) {
    audioSystem.initialize();
    
    // デフォルトフォーマット
    format.sampleRate = 44100;
    format.channels = 2;
    format.bitDepth = 16;
    format.sampleFormat = paInt16;
}

AudioRecorder::~AudioRecorder() {
    if (recording) {
        stopRecording();
    }
    if (stream) {
        Pa_CloseStream(stream);
    }
}

bool AudioRecorder::setupRecording(const std::string& outputPath) {
    outputFilePath = generateOutputFileName(outputPath);
    
    // デフォルトデバイスを使用
    PaDeviceIndex deviceIndex = Pa_GetDefaultInputDevice();
    if (deviceIndex == paNoDevice) {
        std::cerr << "No default input device found" << std::endl;
        return false;
    }
    
    const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
    if (!deviceInfo) {
        return false;
    }
    
    // デバイスの対応サンプルレートを使用（ただし、44.1kHzか48kHzを優先）
    double deviceSampleRate = deviceInfo->defaultSampleRate;
    if (deviceSampleRate == 48000.0 || deviceSampleRate == 44100.0) {
        format.sampleRate = static_cast<int>(deviceSampleRate);
    } else {
        // デフォルトでは44.1kHzを使用
        format.sampleRate = 44100;
    }
    format.channels = std::min(2, deviceInfo->maxInputChannels);
    channelCount = format.channels;
    startChannelIndex = 0;
    endChannelIndex = format.channels - 1;
    
    std::cout << "Recording setup:" << std::endl;
    std::cout << "  Device: " << deviceInfo->name << std::endl;
    std::cout << "  Sample rate: " << format.sampleRate << " Hz" << std::endl;
    std::cout << "  Channels: " << format.channels << std::endl;
    
    return createOutputFile();
}

bool AudioRecorder::setupRecording(const std::string& outputPath, int deviceIndex, 
                                  int startChannel, int endChannel) {
    outputFilePath = generateOutputFileName(outputPath);
    
    audioSystem.enumerateDevices();
    AudioDeviceInfo* device = audioSystem.getDevice(deviceIndex);
    
    if (!device) {
        std::cerr << "Invalid device index: " << deviceIndex << std::endl;
        return false;
    }
    
    // ユーザー指定は1ベース、内部処理は0ベースに変換
    startChannelIndex = startChannel - 1;  // 1ベース→0ベース変換
    endChannelIndex = endChannel - 1;      // 1ベース→0ベース変換
    channelCount = endChannel - startChannel + 1;
    
    if (!selectDevice(*device)) {
        return false;
    }
    
    std::cout << "Recording setup:" << std::endl;
    std::cout << "  Device: " << device->deviceName << std::endl;
    std::cout << "  Sample rate: " << format.sampleRate << " Hz" << std::endl;
    std::cout << "  Channels: " << startChannel << "-" << endChannel 
              << " (" << channelCount << "ch)" << std::endl;
    
    // WASAPIループバックデバイスの場合はWASAPILoopbackRecorderがファイル作成を管理
    if (device->deviceType == 'W' && device->deviceName.find("WASAPI-Loopback") != std::string::npos) {
        return true;
    }
    
    return createOutputFile();
}

bool AudioRecorder::selectDevice(const AudioDeviceInfo& deviceInfo) {
    if (stream) {
        Pa_CloseStream(stream);
        stream = nullptr;
    }
    
    // WASAPIループバックデバイス（デバイス名にWASAPI-Loopbackが含まれる）の場合
    if (deviceInfo.deviceType == 'W' && deviceInfo.deviceName.find("WASAPI-Loopback") != std::string::npos) {
        std::cout << "Using native WASAPI Loopback recorder for device: " << deviceInfo.deviceName << std::endl;
        
        // WASAPILoopbackRecorderを作成
        wasapiLoopbackRecorder = std::make_unique<WASAPILoopbackRecorder>();
        
        // デバイスを列挙
        if (!wasapiLoopbackRecorder->enumerateRenderDevices()) {
            std::cerr << "Failed to enumerate WASAPI render devices" << std::endl;
            return false;
        }
        
        // デバイスインデックスから初期化（deviceInfo.deviceIndexは0ベース）
        if (!wasapiLoopbackRecorder->initialize(static_cast<int>(deviceInfo.deviceIndex) + 1)) {
            std::cerr << "Failed to initialize WASAPI loopback recorder" << std::endl;
            return false;
        }
        
        usingWASAPILoopback = true;
        format.sampleRate = 44100;  // WASAPILoopbackRecorderのデフォルト
        format.channels = 2;
        format.bitDepth = 16;
        channelCount = format.channels;
        
        return true;
    }
    
    // 従来のPortAudioデバイスの場合
    usingWASAPILoopback = false;
    wasapiLoopbackRecorder.reset();
    
    const PaDeviceInfo* paDeviceInfo = Pa_GetDeviceInfo(deviceInfo.deviceIndex);
    if (!paDeviceInfo) {
        std::cerr << "Device not found" << std::endl;
        return false;
    }
    
    format.sampleRate = static_cast<int>(deviceInfo.defaultSampleRate);
    if (format.sampleRate == 0) {
        format.sampleRate = 44100;  // フォールバック
    }
    
    // ストリームパラメータ設定
    PaStreamParameters inputParams;
    inputParams.device = deviceInfo.deviceIndex;
    inputParams.channelCount = channelCount;
    inputParams.sampleFormat = format.sampleFormat;
    inputParams.suggestedLatency = paDeviceInfo->defaultLowInputLatency;
    inputParams.hostApiSpecificStreamInfo = nullptr;
    
    // WASAPIループバック録音の場合
    if (deviceInfo.deviceType == 'W' && deviceInfo.inputOutput == 'O' && 
        deviceInfo.supportsLoopback) {
        return setupWASAPILoopback(deviceInfo);
    }
    // ASIO録音の場合
    else if (deviceInfo.deviceType == 'A') {
        return setupASIORecording(deviceInfo);
    }
    // 通常の入力録音
    else {
        PaError err = Pa_OpenStream(
            &stream,
            &inputParams,
            nullptr,  // 出力なし
            format.sampleRate,
            256,  // framesPerBuffer
            paClipOff,
            recordCallbackWASAPI,
            this
        );
        
        if (err != paNoError) {
            std::cerr << "Failed to open stream: " << Pa_GetErrorText(err) << std::endl;
            return false;
        }
    }
    
    return true;
}

bool AudioRecorder::setupWASAPILoopback(const AudioDeviceInfo& device) {
    std::cout << "Setting up WASAPI loopback for device: " << device.deviceName << std::endl;
    
    // ループバックデバイスであることを確認（デバイス名による判定）
    std::cout << "Attempting to set up loopback recording for: " << device.deviceName << std::endl;
    
    // WASAPIループバック用のストリーム情報設定（フラグは不要）
    PaWasapiStreamInfo wasapiInfo;
    wasapiInfo.size = sizeof(PaWasapiStreamInfo);
    wasapiInfo.hostApiType = paWASAPI;
    wasapiInfo.version = 1;
    wasapiInfo.flags = 0;  // ループバック用の特別なフラグは存在しない
    
    const PaDeviceInfo* paDeviceInfo = Pa_GetDeviceInfo(device.deviceIndex);
    if (!paDeviceInfo) {
        std::cerr << "Cannot get device info for index: " << device.deviceIndex << std::endl;
        return false;
    }
    
    std::cout << "Device info:" << std::endl;
    std::cout << "  Max input channels: " << paDeviceInfo->maxInputChannels << std::endl;
    std::cout << "  Max output channels: " << paDeviceInfo->maxOutputChannels << std::endl;
    std::cout << "  Default sample rate: " << paDeviceInfo->defaultSampleRate << std::endl;
    
    // WASAPIループバック録音: 出力デバイスを入力として設定
    // ループバックでは出力デバイスでもチャンネル数を強制的に設定
    PaStreamParameters inputParams;
    inputParams.device = device.deviceIndex;
    // ループバックデバイスでは、maxInputChannelsが0でも強制的にチャンネル数を設定
    inputParams.channelCount = std::min(2, std::max(paDeviceInfo->maxOutputChannels, 2));
    inputParams.sampleFormat = paFloat32;  // PortAudioのWASAPIループバックではfloat32推奨
    inputParams.suggestedLatency = paDeviceInfo->defaultLowOutputLatency;  // 出力レイテンシを使用
    inputParams.hostApiSpecificStreamInfo = &wasapiInfo;
    
    // チャンネル設定とフォーマット同期
    channelCount = inputParams.channelCount;
    format.channels = channelCount;
    format.sampleFormat = inputParams.sampleFormat;
    
    std::cout << "Opening WASAPI loopback stream with " << channelCount << " channels" << std::endl;
    
    // ループバック録音ストリームを開く（ブロッキング読み取り方式）
    PaError err = Pa_OpenStream(
        &stream,
        &inputParams,  // WASAPIループバックは入力パラメータとして設定
        nullptr,       // 出力なし
        format.sampleRate,
        paFramesPerBufferUnspecified,  // ブロッキング読み取りでは任意サイズ
        paClipOff,
        nullptr,       // コールバックなし（ブロッキング読み取り）
        nullptr        // ユーザーデータ不要
    );
    
    if (err != paNoError) {
        std::cerr << "Failed to open WASAPI loopback stream: " << Pa_GetErrorText(err) << std::endl;
        
        // チャンネル数を減らして再試行
        if (channelCount > 2) {
            std::cout << "Retrying with stereo (2 channels)" << std::endl;
            inputParams.channelCount = 2;
            channelCount = 2;
            format.channels = 2;
            
            err = Pa_OpenStream(
                &stream,
                &inputParams,
                nullptr,
                format.sampleRate,
                256,
                paClipOff,
                recordCallbackWASAPI,
                this
            );
        }
        
        if (err != paNoError) {
            std::cerr << "WASAPI loopback recording failed: " << Pa_GetErrorText(err) << std::endl;
            return false;
        }
    }
    
    std::cout << "WASAPI loopback stream opened successfully" << std::endl;
    return true;
}

bool AudioRecorder::setupASIORecording(const AudioDeviceInfo& device) {
    // ASIO固有の設定
    PaAsioStreamInfo asioInfo;
    asioInfo.size = sizeof(PaAsioStreamInfo);
    asioInfo.hostApiType = paASIO;
    asioInfo.version = 1;
    asioInfo.flags = paAsioUseChannelSelectors;
    
    // チャンネルセレクタ設定
    int* channelSelectors = new int[channelCount];
    for (int i = 0; i < channelCount; i++) {
        channelSelectors[i] = startChannelIndex + i;
    }
    asioInfo.channelSelectors = channelSelectors;
    
    PaStreamParameters inputParams;
    inputParams.device = device.deviceIndex;
    inputParams.channelCount = channelCount;
    inputParams.sampleFormat = format.sampleFormat;
    inputParams.suggestedLatency = Pa_GetDeviceInfo(device.deviceIndex)->defaultLowInputLatency;
    inputParams.hostApiSpecificStreamInfo = &asioInfo;
    
    PaError err = Pa_OpenStream(
        &stream,
        device.inputOutput == 'I' ? &inputParams : nullptr,
        device.inputOutput == 'O' ? &inputParams : nullptr,
        format.sampleRate,
        256,
        paClipOff,
        recordCallbackASIO,
        this
    );
    
    delete[] channelSelectors;
    
    if (err != paNoError) {
        std::cerr << "Failed to open ASIO stream: " << Pa_GetErrorText(err) << std::endl;
        return false;
    }
    
    std::cout << "ASIO recording configured" << std::endl;
    return true;
}

void AudioRecorder::startRecording() {
    // WASAPILoopbackRecorderを使用する場合
    if (usingWASAPILoopback && wasapiLoopbackRecorder) {
        if (!wasapiLoopbackRecorder->startRecording(outputFilePath)) {
            std::cerr << "Failed to start WASAPI loopback recording" << std::endl;
            return;
        }
        recording = true;
        recordedSamples = 0;
        return;
    }
    
    // 従来のPortAudio録音の場合
    if (!stream || !outputFile) {
        return;
    }
    
    recording = true;
    recordedSamples = 0;
    
    PaError err = Pa_StartStream(stream);
    if (err != paNoError) {
        std::cerr << "Failed to start stream: " << Pa_GetErrorText(err) << std::endl;
        recording = false;
        return;
    }
    
    // ブロッキング読み取りによる録音ループ
    const unsigned long framesPerRead = 1024;
    std::vector<float> buffer(framesPerRead * channelCount, 0.0f);
    
    std::cout << "Starting blocking read recording loop..." << std::endl;
    
    while (recording) {
        PaError readErr = Pa_ReadStream(stream, buffer.data(), framesPerRead);
        
        if (readErr == paInputOverflowed) {
            std::cerr << "[Warning] Input overflowed" << std::endl;
            readErr = paNoError;  // 継続
        }
        
        if (readErr != paNoError) {
            std::cerr << "Pa_ReadStream failed: " << Pa_GetErrorText(readErr) << std::endl;
            break;
        }
        
        // データをファイルに書き込み
        processAudioData(buffer.data(), framesPerRead);
        
        // 進捗表示を無効化（main.cppのタイムカウンターと競合するため）
        // static int progressCount = 0;
        // if (++progressCount % 100 == 0) {
        //     // 進捗表示処理はコメントアウト  
        // }
    }
    
    std::cout << "Recording loop ended" << std::endl;
}

void AudioRecorder::stopRecording() {
    recording = false;
    
    // WASAPILoopbackRecorderを使用する場合
    if (usingWASAPILoopback && wasapiLoopbackRecorder) {
        wasapiLoopbackRecorder->stopRecording();
        return;
    }
    
    // 従来のPortAudio録音の場合
    if (!stream) {
        return;
    }
    
    Pa_StopStream(stream);
    
    // WAVヘッダーを更新（ファイルを閉じる前に）
    if (outputFile && outputFile->is_open()) {
        // ファイルバッファを確実にフラッシュ
        outputFile->flush();
        updateWAVHeader();
        outputFile->flush();
        
        outputFile->close();
        outputFile.reset();
    }
}

bool AudioRecorder::isRecording() const {
    if (usingWASAPILoopback && wasapiLoopbackRecorder) {
        return wasapiLoopbackRecorder->isRecording();
    }
    return recording.load();
}

std::string AudioRecorder::getCurrentTimeString() const {
    return formatTime(getCurrentTimeSeconds());
}

double AudioRecorder::getCurrentTimeSeconds() const {
    if (usingWASAPILoopback && wasapiLoopbackRecorder) {
        // WASAPILoopbackRecorderの場合、録音開始からの経過時間を使用
        if (wasapiLoopbackRecorder->isRecording()) {
            // 簡易的な経過時間計算（実際の録音時間）
            static auto startTime = std::chrono::steady_clock::now();
            static bool initialized = false;
            if (!initialized && wasapiLoopbackRecorder->isRecording()) {
                startTime = std::chrono::steady_clock::now();
                initialized = true;
            }
            if (initialized) {
                auto now = std::chrono::steady_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - startTime).count();
                return static_cast<double>(elapsed);
            }
        }
        return 0.0;
    }
    return static_cast<double>(recordedSamples.load()) / format.sampleRate;
}

int AudioRecorder::recordCallbackWASAPI(const void* inputBuffer, void* outputBuffer,
                                       unsigned long frameCount,
                                       const PaStreamCallbackTimeInfo* timeInfo,
                                       PaStreamCallbackFlags statusFlags,
                                       void* userData) {
    (void)timeInfo;
    (void)statusFlags;
    
    AudioRecorder* recorder = static_cast<AudioRecorder*>(userData);
    
    // ループバック録音の場合、outputBufferから録音
    const void* dataToRecord = inputBuffer ? inputBuffer : outputBuffer;
    
    if (recorder->recording && dataToRecord) {
        recorder->processAudioData(dataToRecord, frameCount);
    }
    
    // 出力バッファをクリア（必要な場合）
    if (outputBuffer && !inputBuffer) {
        memset(outputBuffer, 0, frameCount * recorder->channelCount * sizeof(float));
    }
    
    return paContinue;
}

int AudioRecorder::recordCallbackASIO(const void* inputBuffer, void* outputBuffer,
                                     unsigned long frameCount,
                                     const PaStreamCallbackTimeInfo* timeInfo,
                                     PaStreamCallbackFlags statusFlags,
                                     void* userData) {
    return recordCallbackWASAPI(inputBuffer, outputBuffer, frameCount, timeInfo, statusFlags, userData);
}

void AudioRecorder::processAudioData(const void* inputBuffer, unsigned long frameCount) {
    if (!outputFile || !outputFile->is_open()) {
        std::cout << "Error: Output file not open" << std::endl;
        return;
    }
    
    if (!inputBuffer) {
        std::cout << "Warning: No input data received" << std::endl;
        return;
    }
    
    size_t bytesToWrite = frameCount * channelCount * (format.bitDepth / 8);
    outputFile->write(static_cast<const char*>(inputBuffer), bytesToWrite);
    
    recordedSamples += frameCount;
    
    // デバッグ情報（最初の数回のみ出力）
    static int debugCount = 0;
    if (debugCount < 5) {
        std::cout << "Audio data written: " << frameCount << " frames, " 
                  << bytesToWrite << " bytes, total samples: " 
                  << recordedSamples.load() << std::endl;
        debugCount++;
    }
}

bool AudioRecorder::createOutputFile() {
    outputFile = std::make_unique<std::ofstream>(outputFilePath, std::ios::binary);
    
    if (!outputFile->is_open()) {
        std::cerr << "Failed to create output file: " << outputFilePath << std::endl;
        return false;
    }
    
    // WAVヘッダーを手動で書き込み（JUNKチャンク回避）
    // RIFF チャンク
    outputFile->write("RIFF", 4);
    uint32_t fileSize = 36;  // 後で更新
    outputFile->write(reinterpret_cast<const char*>(&fileSize), 4);
    outputFile->write("WAVE", 4);
    
    // fmt チャンク
    outputFile->write("fmt ", 4);
    uint32_t fmtSize = 16;
    outputFile->write(reinterpret_cast<const char*>(&fmtSize), 4);
    uint16_t audioFormat = 1;  // PCM
    outputFile->write(reinterpret_cast<const char*>(&audioFormat), 2);
    uint16_t channels = static_cast<uint16_t>(channelCount);
    outputFile->write(reinterpret_cast<const char*>(&channels), 2);
    uint32_t sampleRate = format.sampleRate;
    outputFile->write(reinterpret_cast<const char*>(&sampleRate), 4);
    uint32_t byteRate = sampleRate * channels * (format.bitDepth / 8);
    outputFile->write(reinterpret_cast<const char*>(&byteRate), 4);
    uint16_t blockAlign = static_cast<uint16_t>(channels * (format.bitDepth / 8));
    outputFile->write(reinterpret_cast<const char*>(&blockAlign), 2);
    uint16_t bitsPerSample = static_cast<uint16_t>(format.bitDepth);
    outputFile->write(reinterpret_cast<const char*>(&bitsPerSample), 2);
    
    // data チャンク
    outputFile->write("data", 4);
    uint32_t dataSize = 0;  // 後で更新
    outputFile->write(reinterpret_cast<const char*>(&dataSize), 4);
    
    outputFile->flush();
    
    std::cout << "Output file: " << outputFilePath << std::endl;
    std::cout << "WAV header written manually (44 bytes)" << std::endl;
    return true;
}

void AudioRecorder::updateWAVHeader() {
    if (!outputFile || !outputFile->is_open()) {
        return;
    }
    
    // データサイズを計算
    uint32_t dataSize = static_cast<uint32_t>(recordedSamples.load()) * channelCount * (format.bitDepth / 8);
    uint32_t fileSize = dataSize + 36;  // WAVヘッダー44バイト - 8バイト(RIFF+filesize) = 36
    
    std::cout << "Updating WAV header: samples=" << recordedSamples.load() 
              << ", channels=" << channelCount 
              << ", bitDepth=" << format.bitDepth << std::endl;
    std::cout << "Calculated: dataSize=" << dataSize << ", fileSize=" << fileSize << std::endl;
    std::cout << "WAVHeader size=" << sizeof(WAVHeader) << ", dataSize offset=" << (sizeof(WAVHeader) - sizeof(uint32_t)) << std::endl;
    
    // ファイルサイズを更新（RIFF chunk size）- 位置4
    outputFile->seekp(4, std::ios::beg);
    outputFile->write(reinterpret_cast<const char*>(&fileSize), 4);
    
    // データサイズを更新（data chunk size）- 位置40（0x28）
    outputFile->seekp(40, std::ios::beg);
    outputFile->write(reinterpret_cast<const char*>(&dataSize), 4);
    
    // ファイルをフラッシュ
    outputFile->flush();
    
    std::cout << "WAV header updated successfully" << std::endl;
}

std::string AudioRecorder::generateOutputFileName(const std::string& basePath) const {
    // ファイル名生成ロジック
    size_t lastDot = basePath.find_last_of('.');
    size_t lastSlash = basePath.find_last_of("\\/");
    
    // 拡張子がある場合はそのまま使用
    if (lastDot != std::string::npos && 
        (lastSlash == std::string::npos || lastDot > lastSlash)) {
        return basePath;
    }
    
    // ディレクトリの場合はタイムスタンプ付きファイル名を生成
    if (basePath.empty() || basePath.back() == '\\' || basePath.back() == '/') {
        auto now = std::time(nullptr);
        auto tm = *std::localtime(&now);
        
        std::ostringstream oss;
        oss << basePath;
        if (!basePath.empty() && basePath.back() != '\\' && basePath.back() != '/') {
            oss << "\\";
        }
        oss << "recording_" << std::put_time(&tm, "%Y%m%d_%H%M%S") << ".wav";
        return oss.str();
    }
    
    // それ以外は.wavを追加
    return basePath + ".wav";
}

std::string AudioRecorder::formatTime(double timeInSeconds) const {
    int hours = static_cast<int>(timeInSeconds) / 3600;
    int minutes = (static_cast<int>(timeInSeconds) % 3600) / 60;
    int seconds = static_cast<int>(timeInSeconds) % 60;
    
    std::ostringstream oss;
    oss << std::setfill('0') << std::setw(2) << hours << ":"
        << std::setfill('0') << std::setw(2) << minutes << ":"
        << std::setfill('0') << std::setw(2) << seconds;
    
    return oss.str();
}