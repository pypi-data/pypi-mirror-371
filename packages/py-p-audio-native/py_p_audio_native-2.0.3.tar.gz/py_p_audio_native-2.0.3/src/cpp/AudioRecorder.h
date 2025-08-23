#pragma once
#pragma execution_character_set("utf-8")

#include "AudioSystem.h"
#include "WASAPILoopbackRecorder.h"
#include <portaudio.h>
#include <string>
#include <atomic>
#include <memory>
#include <thread>
#include <fstream>

// WAVファイルヘッダー
struct WAVHeader {
    char riff[4];           // "RIFF"
    uint32_t fileSize;      // ファイルサイズ - 8
    char wave[4];           // "WAVE"
    char fmt[4];            // "fmt "
    uint32_t fmtSize;       // フォーマットサイズ
    uint16_t audioFormat;   // オーディオフォーマット
    uint16_t channels;      // チャンネル数
    uint32_t sampleRate;    // サンプルレート
    uint32_t byteRate;      // バイトレート
    uint16_t blockAlign;    // ブロックアライン
    uint16_t bitsPerSample; // ビット深度
    char data[4];           // "data"
    uint32_t dataSize;      // データサイズ
};

// 録音用コールバック関数のプロトタイプ
typedef int (*RecordCallback)(const void* inputBuffer, void* outputBuffer,
                             unsigned long frameCount, const PaStreamCallbackTimeInfo* timeInfo,
                             PaStreamCallbackFlags statusFlags, void* userData);

class AudioRecorder {
public:
    AudioRecorder();
    ~AudioRecorder();
    
    // 録音設定
    bool setupRecording(const std::string& outputPath);
    bool setupRecording(const std::string& outputPath, int deviceIndex, int startChannel, int endChannel);
    
    // 録音制御
    void startRecording();
    void stopRecording();
    bool isRecording() const;
    
    // 時間情報
    std::string getCurrentTimeString() const;
    double getCurrentTimeSeconds() const;
    
    // デバイス設定
    bool selectDevice(const AudioDeviceInfo& deviceInfo);
    
private:
    AudioSystem audioSystem;
    PaStream* stream;
    std::atomic<bool> recording;
    std::atomic<int64_t> recordedSamples;
    
    // WASAPIループバック録音用
    std::unique_ptr<WASAPILoopbackRecorder> wasapiLoopbackRecorder;
    bool usingWASAPILoopback;
    
    // 録音設定
    AudioFormat format;
    int startChannelIndex;
    int endChannelIndex;
    int channelCount;
    
    // ファイル出力
    std::string outputFilePath;
    std::unique_ptr<std::ofstream> outputFile;
    WAVHeader wavHeader;
    
    // 内部メソッド
    std::string generateOutputFileName(const std::string& basePath) const;
    std::string formatTime(double timeInSeconds) const;
    bool createOutputFile();
    void updateWAVHeader();
    bool setupWASAPILoopback(const AudioDeviceInfo& device);
    bool setupASIORecording(const AudioDeviceInfo& device);
    
    // コールバック
    static int recordCallbackWASAPI(const void* inputBuffer, void* outputBuffer,
                                   unsigned long frameCount, const PaStreamCallbackTimeInfo* timeInfo,
                                   PaStreamCallbackFlags statusFlags, void* userData);
    
    static int recordCallbackASIO(const void* inputBuffer, void* outputBuffer,
                                 unsigned long frameCount, const PaStreamCallbackTimeInfo* timeInfo,
                                 PaStreamCallbackFlags statusFlags, void* userData);
    
    // データ処理
    void processAudioData(const void* inputBuffer, unsigned long frameCount);
};