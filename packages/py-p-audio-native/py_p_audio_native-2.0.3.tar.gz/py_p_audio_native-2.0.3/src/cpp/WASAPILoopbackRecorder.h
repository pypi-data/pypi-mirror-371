#pragma once
#pragma execution_character_set("utf-8")

#include <Windows.h>
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <audiopolicy.h>
#include <functiondiscoverykeys_devpkey.h>
#include <string>
#include <vector>
#include <memory>
#include <thread>
#include <atomic>
#include <fstream>

// COM初期化RAII
class COMInitializer {
public:
    COMInitializer();
    ~COMInitializer();
    bool isInitialized() const { return initialized; }

private:
    bool initialized;
};

// WASAPIループバック録音クラス
class WASAPILoopbackRecorder {
public:
    WASAPILoopbackRecorder();
    ~WASAPILoopbackRecorder();

    // デバイス列挙
    bool enumerateRenderDevices();
    void printRenderDevices();
    std::vector<std::wstring> getRenderDeviceNames() const;

    // 録音機能
    bool initialize(int deviceIndex = -1);  // -1 = default device
    bool startRecording(const std::string& filename);
    void stopRecording();
    bool isRecording() const { return recording.load(); }

    // エラー情報
    std::string getLastError() const { return lastError; }

private:
    // COM関連
    COMInitializer comInit;
    
    // Core Audio API インターフェース
    IMMDeviceEnumerator* deviceEnumerator;
    IMMDevice* renderDevice;
    IAudioClient* audioClient;
    IAudioCaptureClient* captureClient;
    
    // デバイス情報
    struct RenderDeviceInfo {
        std::wstring id;
        std::wstring name;
        std::wstring description;
    };
    std::vector<RenderDeviceInfo> renderDevices;
    
    // 録音状態
    std::atomic<bool> recording;
    std::thread recordingThread;
    
    // オーディオフォーマット
    WAVEFORMATEX* mixFormat;
    UINT32 bufferFrameCount;
    
    // ファイル出力
    std::unique_ptr<std::ofstream> outputFile;
    std::string outputFilename;
    
    // エラー処理
    std::string lastError;
    void setError(const std::string& error);
    
    // 内部メソッド
    bool initializeCoreAudio();
    void cleanup();
    void recordingLoop();
    bool createWAVFile(const std::string& filename);
    void writeWAVHeader();
    void updateWAVHeader();
    void writeAudioData(BYTE* data, UINT32 frameCount);
    
    // WAVヘッダー情報
    struct WAVHeader {
        char riff[4] = {'R', 'I', 'F', 'F'};
        uint32_t fileSize = 0;
        char wave[4] = {'W', 'A', 'V', 'E'};
        char fmt[4] = {'f', 'm', 't', ' '};
        uint32_t fmtSize = 16;
        uint16_t audioFormat = 1;  // PCM
        uint16_t channels = 2;
        uint32_t sampleRate = 44100;
        uint32_t byteRate = 0;
        uint16_t blockAlign = 0;
        uint16_t bitsPerSample = 16;
        char data[4] = {'d', 'a', 't', 'a'};
        uint32_t dataSize = 0;
    };
    
    WAVHeader wavHeader;
    uint32_t totalBytesWritten;
};