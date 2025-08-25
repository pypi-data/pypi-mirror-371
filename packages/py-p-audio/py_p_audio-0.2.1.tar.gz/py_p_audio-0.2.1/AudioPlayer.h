#pragma once
#pragma execution_character_set("utf-8")

#include "AudioSystem.h"
#include <portaudio.h>
#include <string>
#include <atomic>
#include <memory>
#include <vector>

// WAVファイル読み込み用
struct WAVFileData {
    std::vector<float> audioData;
    int channels;
    int sampleRate;
    int totalSamples;
    int currentPosition;
};

class AudioPlayer {
public:
    AudioPlayer();
    ~AudioPlayer();
    
    // ファイル操作
    bool loadFile(const std::string& filePath);
    void unloadFile();
    
    // 再生制御
    void startPlayback();
    void stopPlayback();
    bool isPlaying() const;
    
    // 時間情報
    std::string getCurrentTimeString() const;
    double getCurrentTimeSeconds() const;
    double getTotalTimeSeconds() const;
    std::string formatTime(double timeInSeconds) const;
    
    // 設定
    bool setOutputDevice(int deviceIndex);
    
private:
    AudioSystem audioSystem;
    PaStream* stream;
    std::atomic<bool> playing;
    
    // オーディオデータ
    std::unique_ptr<WAVFileData> audioData;
    
    // 再生設定
    AudioFormat outputFormat;
    AudioDeviceInfo* currentDevice;
    
    // 内部メソッド
    bool loadWAVFile(const std::string& filePath);
    bool setupOutputStream();
    
    // コールバック
    static int playbackCallback(const void* inputBuffer, void* outputBuffer,
                               unsigned long frameCount, const PaStreamCallbackTimeInfo* timeInfo,
                               PaStreamCallbackFlags statusFlags, void* userData);
    
    // データ処理
    void fillOutputBuffer(float* outputBuffer, unsigned long frameCount);
};