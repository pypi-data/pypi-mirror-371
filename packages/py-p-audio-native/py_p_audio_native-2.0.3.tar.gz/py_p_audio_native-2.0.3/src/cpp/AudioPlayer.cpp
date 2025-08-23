#pragma execution_character_set("utf-8")
#include "AudioPlayer.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <cstring>
#include <algorithm>
#include <Windows.h>

AudioPlayer::AudioPlayer() 
    : stream(nullptr), playing(false), currentDevice(nullptr) {
    audioSystem.initialize();
    
    // デフォルトフォーマット
    outputFormat.sampleRate = 44100;
    outputFormat.channels = 2;
    outputFormat.bitDepth = 16;
    outputFormat.sampleFormat = paFloat32;  // 内部処理はfloatで行う
}

AudioPlayer::~AudioPlayer() {
    if (playing) {
        stopPlayback();
    }
    if (stream) {
        Pa_CloseStream(stream);
    }
}

bool AudioPlayer::loadFile(const std::string& filePath) {
    SetConsoleOutputCP(CP_UTF8);
    
    // 既存のデータをクリア
    unloadFile();
    
    // WAVファイル読み込み
    if (!loadWAVFile(filePath)) {
        return false;
    }
    
    std::cout << "File Info:" << std::endl;
    std::cout << "  Sample Rate: " << audioData->sampleRate << " Hz" << std::endl;
    std::cout << "  Channels: " << audioData->channels << std::endl;
    std::cout << "  Duration: " << formatTime(getTotalTimeSeconds()) << std::endl;
    
    return true;
}

bool AudioPlayer::loadWAVFile(const std::string& filePath) {
    std::ifstream file(filePath, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "File not found: " << filePath << std::endl;
        return false;
    }
    
    // WAVヘッダー読み込み
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
        std::cerr << "Failed to read WAV header" << std::endl;
        return false;
    }
    
    // WAVファイルチェック
    if (std::memcmp(header.riff, "RIFF", 4) != 0 ||
        std::memcmp(header.wave, "WAVE", 4) != 0 ||
        std::memcmp(header.fmt, "fmt ", 4) != 0) {
        std::cerr << "Invalid WAV file format" << std::endl;
        std::cout << "RIFF: " << std::string(header.riff, 4) << std::endl;
        std::cout << "WAVE: " << std::string(header.wave, 4) << std::endl;
        std::cout << "fmt : " << std::string(header.fmt, 4) << std::endl;
        return false;
    }
    
    std::cout << "WAV Header:" << std::endl;
    std::cout << "  Format: " << header.audioFormat << std::endl;
    std::cout << "  Channels: " << header.channels << std::endl;
    std::cout << "  Sample Rate: " << header.sampleRate << std::endl;
    std::cout << "  Bits per Sample: " << header.bitsPerSample << std::endl;
    
    // フォーマットチェック
    if (header.audioFormat != 1) {  // PCMのみサポート
        std::cerr << "Unsupported audio format (only PCM supported)" << std::endl;
        return false;
    }
    
    // 残りのfmtチャンクをスキップ
    if (header.fmtSize > 16) {
        file.seekg(header.fmtSize - 16, std::ios::cur);
    }
    
    // データチャンク探索
    char chunkId[4];
    uint32_t chunkSize = 0;
    bool dataChunkFound = false;
    
    std::cout << "Searching for data chunk..." << std::endl;
    
    while (file.read(chunkId, 4)) {
        file.read(reinterpret_cast<char*>(&chunkSize), 4);
        
        std::cout << "Found chunk: " << std::string(chunkId, 4) 
                  << ", size: " << chunkSize << std::endl;
        
        if (std::memcmp(chunkId, "data", 4) == 0) {
            // データチャンク発見
            dataChunkFound = true;
            break;
        }
        
        // 他のチャンクはスキップ
        file.seekg(chunkSize, std::ios::cur);
        
        if (file.eof()) {
            std::cout << "Reached end of file" << std::endl;
            break;
        }
    }
    
    if (!dataChunkFound || chunkSize == 0) {
        std::cerr << "Data chunk not found or empty. Found=" << dataChunkFound 
                  << ", size=" << chunkSize << std::endl;
        return false;
    }
    
    std::cout << "Data chunk size: " << chunkSize << " bytes" << std::endl;
    
    // オーディオデータ作成
    audioData = std::make_unique<WAVFileData>();
    audioData->channels = header.channels;
    audioData->sampleRate = header.sampleRate;
    audioData->currentPosition = 0;
    
    // サンプル数計算
    int bytesPerSample = header.bitsPerSample / 8;
    int totalSamples = chunkSize / bytesPerSample;
    audioData->totalSamples = totalSamples / header.channels;
    
    std::cout << "Bytes per sample: " << bytesPerSample << std::endl;
    std::cout << "Total samples: " << totalSamples << std::endl;
    std::cout << "Samples per channel: " << audioData->totalSamples << std::endl;
    
    // データ読み込み（floatに変換）
    audioData->audioData.resize(totalSamples);
    
    if (header.bitsPerSample == 16) {
        // 16ビットPCM
        std::vector<int16_t> tempData(totalSamples);
        file.read(reinterpret_cast<char*>(tempData.data()), chunkSize);
        
        // float変換
        for (size_t i = 0; i < tempData.size(); i++) {
            audioData->audioData[i] = tempData[i] / 32768.0f;
        }
    }
    else if (header.bitsPerSample == 24) {
        // 24ビットPCM
        std::vector<uint8_t> tempData(chunkSize);
        file.read(reinterpret_cast<char*>(tempData.data()), chunkSize);
        
        for (size_t i = 0, j = 0; i < audioData->audioData.size(); i++, j += 3) {
            int32_t sample = (tempData[j] | (tempData[j+1] << 8) | (tempData[j+2] << 16));
            if (sample & 0x800000) {  // 符号拡張
                sample |= 0xFF000000;
            }
            audioData->audioData[i] = sample / 8388608.0f;
        }
    }
    else if (header.bitsPerSample == 32) {
        // 32ビットPCM
        std::vector<int32_t> tempData(totalSamples);
        file.read(reinterpret_cast<char*>(tempData.data()), chunkSize);
        
        for (size_t i = 0; i < tempData.size(); i++) {
            audioData->audioData[i] = tempData[i] / 2147483648.0f;
        }
    }
    else {
        std::cerr << "Unsupported bit depth: " << header.bitsPerSample << std::endl;
        return false;
    }
    
    file.close();
    return true;
}

void AudioPlayer::unloadFile() {
    if (playing) {
        stopPlayback();
    }
    audioData.reset();
}

void AudioPlayer::startPlayback() {
    if (!audioData || audioData->audioData.empty()) {
        std::cerr << "No audio data loaded" << std::endl;
        return;
    }
    
    // ストリーム設定
    if (!setupOutputStream()) {
        return;
    }
    
    // 再生位置リセット
    audioData->currentPosition = 0;
    playing = true;
    
    PaError err = Pa_StartStream(stream);
    if (err != paNoError) {
        std::cerr << "Failed to start stream: " << Pa_GetErrorText(err) << std::endl;
        playing = false;
    }
}

bool AudioPlayer::setupOutputStream() {
    if (stream) {
        Pa_CloseStream(stream);
        stream = nullptr;
    }
    
    // デフォルト出力デバイス取得
    PaDeviceIndex deviceIndex = Pa_GetDefaultOutputDevice();
    if (deviceIndex == paNoDevice) {
        std::cerr << "No default output device" << std::endl;
        return false;
    }
    
    const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
    if (!deviceInfo) {
        return false;
    }
    
    // 出力パラメータ設定
    PaStreamParameters outputParams;
    outputParams.device = deviceIndex;
    outputParams.channelCount = 2;  // ステレオ出力
    outputParams.sampleFormat = paFloat32;
    outputParams.suggestedLatency = deviceInfo->defaultLowOutputLatency;
    outputParams.hostApiSpecificStreamInfo = nullptr;
    
    // デバイスのサンプルレート取得
    double deviceSampleRate = deviceInfo->defaultSampleRate;
    if (deviceSampleRate == 0) {
        deviceSampleRate = 44100;
    }
    
    PaError err = Pa_OpenStream(
        &stream,
        nullptr,  // 入力なし
        &outputParams,
        deviceSampleRate,
        256,  // framesPerBuffer
        paClipOff,
        playbackCallback,
        this
    );
    
    if (err != paNoError) {
        std::cerr << "Failed to open stream: " << Pa_GetErrorText(err) << std::endl;
        return false;
    }
    
    outputFormat.sampleRate = static_cast<int>(deviceSampleRate);
    return true;
}

void AudioPlayer::stopPlayback() {
    if (!stream) {
        return;
    }
    
    playing = false;
    Pa_StopStream(stream);
}

bool AudioPlayer::isPlaying() const {
    if (!playing.load() || !audioData) {
        return false;
    }
    
    return audioData->currentPosition < audioData->totalSamples;
}

std::string AudioPlayer::getCurrentTimeString() const {
    return formatTime(getCurrentTimeSeconds());
}

double AudioPlayer::getCurrentTimeSeconds() const {
    if (!audioData) {
        return 0.0;
    }
    return static_cast<double>(audioData->currentPosition) / audioData->sampleRate;
}

double AudioPlayer::getTotalTimeSeconds() const {
    if (!audioData) {
        return 0.0;
    }
    return static_cast<double>(audioData->totalSamples) / audioData->sampleRate;
}

bool AudioPlayer::setOutputDevice(int deviceIndex) {
    audioSystem.enumerateDevices();
    AudioDeviceInfo* device = audioSystem.getDevice(deviceIndex);
    
    if (!device || device->inputOutput != 'O') {
        std::cerr << "Invalid output device index" << std::endl;
        return false;
    }
    
    currentDevice = device;
    
    // 再生中の場合は再起動
    if (playing) {
        stopPlayback();
        startPlayback();
    }
    
    return true;
}

int AudioPlayer::playbackCallback(const void* inputBuffer, void* outputBuffer,
                                 unsigned long frameCount,
                                 const PaStreamCallbackTimeInfo* timeInfo,
                                 PaStreamCallbackFlags statusFlags,
                                 void* userData) {
    (void)inputBuffer;
    (void)timeInfo;
    (void)statusFlags;
    
    AudioPlayer* player = static_cast<AudioPlayer*>(userData);
    float* out = static_cast<float*>(outputBuffer);
    
    if (player->playing && player->audioData) {
        player->fillOutputBuffer(out, frameCount);
    } else {
        // 無音出力
        std::memset(out, 0, frameCount * 2 * sizeof(float));
    }
    
    return paContinue;
}

void AudioPlayer::fillOutputBuffer(float* outputBuffer, unsigned long frameCount) {
    if (!audioData) {
        return;
    }
    
    // サンプルレート変換比率
    double ratio = static_cast<double>(audioData->sampleRate) / outputFormat.sampleRate;
    
    for (unsigned long frame = 0; frame < frameCount; frame++) {
        if (audioData->currentPosition >= audioData->totalSamples) {
            // ファイル終端
            outputBuffer[frame * 2] = 0.0f;
            outputBuffer[frame * 2 + 1] = 0.0f;
            continue;
        }
        
        // サンプルレート変換が必要かチェック
        if (std::abs(ratio - 1.0) < 0.001) {
            // サンプルレートが同じ場合は直接コピー
            for (int ch = 0; ch < 2; ch++) {
                int sourceCh = std::min(ch, audioData->channels - 1);
                int idx = audioData->currentPosition * audioData->channels + sourceCh;
                
                if (idx < static_cast<int>(audioData->audioData.size())) {
                    outputBuffer[frame * 2 + ch] = audioData->audioData[idx];
                } else {
                    outputBuffer[frame * 2 + ch] = 0.0f;
                }
            }
        } else {
            // サンプルレート変換（高品質線形補間）
            double sourcePos = audioData->currentPosition * ratio;
            int sourcePosInt = static_cast<int>(sourcePos);
            double frac = sourcePos - sourcePosInt;
            
            if (sourcePosInt >= audioData->totalSamples - 1) {
                outputBuffer[frame * 2] = 0.0f;
                outputBuffer[frame * 2 + 1] = 0.0f;
                audioData->currentPosition = audioData->totalSamples;
                continue;
            }
            
            // 高品質線形補間
            for (int ch = 0; ch < 2; ch++) {
                int sourceCh = std::min(ch, audioData->channels - 1);
                
                int idx1 = sourcePosInt * audioData->channels + sourceCh;
                int idx2 = (sourcePosInt + 1) * audioData->channels + sourceCh;
                
                float sample1 = 0.0f, sample2 = 0.0f;
                
                if (idx1 < static_cast<int>(audioData->audioData.size())) {
                    sample1 = audioData->audioData[idx1];
                }
                if (idx2 < static_cast<int>(audioData->audioData.size())) {
                    sample2 = audioData->audioData[idx2];
                }
                
                // Hermite補間（滑らかな補間）
                float hermite = sample1 + (sample2 - sample1) * static_cast<float>(frac) * static_cast<float>(frac) * (3.0f - 2.0f * static_cast<float>(frac));
                outputBuffer[frame * 2 + ch] = hermite;
            }
        }
        
        audioData->currentPosition++;
    }
}

std::string AudioPlayer::formatTime(double timeInSeconds) const {
    int hours = static_cast<int>(timeInSeconds) / 3600;
    int minutes = (static_cast<int>(timeInSeconds) % 3600) / 60;
    int seconds = static_cast<int>(timeInSeconds) % 60;
    
    std::ostringstream oss;
    oss << std::setfill('0') << std::setw(2) << hours << ":"
        << std::setfill('0') << std::setw(2) << minutes << ":"
        << std::setfill('0') << std::setw(2) << seconds;
    
    return oss.str();
}