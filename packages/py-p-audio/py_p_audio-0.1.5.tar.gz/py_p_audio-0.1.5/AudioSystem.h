#pragma once
#pragma execution_character_set("utf-8")

#include <portaudio.h>
#include <pa_asio.h>
#include <pa_win_wasapi.h>
#include <vector>
#include <string>
#include <memory>
#include <atomic>

// デバイス情報構造体
struct AudioDeviceInfo {
    int index;
    char deviceType;  // 'W'=WASAPI, 'A'=ASIO
    char inputOutput; // 'I'=Input, 'O'=Output
    std::string deviceName;
    int totalChannels;
    PaHostApiIndex hostApiIndex;
    PaDeviceIndex deviceIndex;
    double defaultSampleRate;
    bool supportsLoopback;
};

// オーディオフォーマット
struct AudioFormat {
    int sampleRate;
    int channels;
    int bitDepth;
    PaSampleFormat sampleFormat;
};

// 基本オーディオシステムクラス
class AudioSystem {
public:
    AudioSystem();
    ~AudioSystem();
    
    // 初期化・終了
    bool initialize();
    void terminate();
    
    // デバイス管理
    void enumerateDevices();
    std::vector<AudioDeviceInfo> getDeviceList() const;
    void printDeviceInfo(const AudioDeviceInfo& device);
    
    // デバイス取得
    AudioDeviceInfo* getDevice(int index);
    
    // システム情報
    void printSystemInfo();
    
private:
    std::vector<AudioDeviceInfo> deviceList;
    bool initialized;
    
    void addWASAPIDevices();
    void addASIODevices();
    void addWASAPILoopbackDevices();  // WASAPIループバック専用デバイス
};