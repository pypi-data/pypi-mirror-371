#include "AudioSystem.h"
#include "WASAPILoopbackRecorder.h"
#pragma execution_character_set("utf-8")
#include <iostream>
#include <iomanip>
#include <Windows.h>

AudioSystem::AudioSystem() : initialized(false) {
}

AudioSystem::~AudioSystem() {
    if (initialized) {
        terminate();
    }
}

bool AudioSystem::initialize() {
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

void AudioSystem::terminate() {
    if (initialized) {
        Pa_Terminate();
        initialized = false;
    }
}

void AudioSystem::enumerateDevices() {
    SetConsoleOutputCP(CP_UTF8);
    
    if (!initialized && !initialize()) {
        return;
    }
    
    deviceList.clear();
    
    addWASAPIDevices();
    addASIODevices();
    addWASAPILoopbackDevices();
    
    // デバイスリストを出力
    for (const auto& device : deviceList) {
        printDeviceInfo(device);
    }
}

void AudioSystem::addWASAPIDevices() {
    int numHostApis = Pa_GetHostApiCount();
    
    for (int i = 0; i < numHostApis; i++) {
        const PaHostApiInfo* hostApiInfo = Pa_GetHostApiInfo(i);
        if (hostApiInfo == nullptr) continue;
        
        // WASAPIのみを探す
        if (hostApiInfo->type == paWASAPI) {
            
            // このホストAPIのデバイスを列挙
            for (int j = 0; j < hostApiInfo->deviceCount; j++) {
                PaDeviceIndex deviceIndex = Pa_HostApiDeviceIndexToDeviceIndex(i, j);
                if (deviceIndex < 0) continue;
                
                const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
                if (deviceInfo == nullptr) continue;
                
                // 入力デバイス
                if (deviceInfo->maxInputChannels > 0) {
                    AudioDeviceInfo info;
                    info.index = static_cast<int>(deviceList.size()) + 1;
                    info.deviceType = 'W';  // WASAPI/Windows
                    info.inputOutput = 'I';
                    info.deviceName = deviceInfo->name;
                    info.totalChannels = deviceInfo->maxInputChannels;
                    info.hostApiIndex = i;
                    info.deviceIndex = deviceIndex;
                    info.defaultSampleRate = deviceInfo->defaultSampleRate;
                    // ループバック対応チェック（デバイス名による検出）
                    info.supportsLoopback = false;
                    if (hostApiInfo->type == paWASAPI) {
                        std::string deviceName = deviceInfo->name;
                        // ループバックデバイス検出（デバイス名とプロパティによる判定）
                        // WASAPIループバックデバイスは通常 "(loopback)" や特定のパターンを含む
                        if (deviceName.find("(loopback)") != std::string::npos ||
                            deviceName.find("ステレオ ミキサー") != std::string::npos ||
                            deviceName.find("Stereo Mix") != std::string::npos ||
                            deviceName.find("What U Hear") != std::string::npos ||
                            deviceName.find("スピーカー") != std::string::npos ||
                            deviceName.find("Speaker") != std::string::npos) {
                            info.supportsLoopback = true;
                        }
                    }
                    deviceList.push_back(info);
                }
                
                // 出力デバイス（PortAudio経由のWASAPIループバックは動作しないため除外）
                // Windows Core Audio API直接実装のみ使用
            }
        }
    }
}

void AudioSystem::addASIODevices() {
    int numHostApis = Pa_GetHostApiCount();
    
    for (int i = 0; i < numHostApis; i++) {
        const PaHostApiInfo* hostApiInfo = Pa_GetHostApiInfo(i);
        if (hostApiInfo == nullptr) continue;
        
        // ASIOを探す
        if (hostApiInfo->type == paASIO) {
            // このホストAPIのデバイスを列挙
            for (int j = 0; j < hostApiInfo->deviceCount; j++) {
                PaDeviceIndex deviceIndex = Pa_HostApiDeviceIndexToDeviceIndex(i, j);
                if (deviceIndex < 0) continue;
                
                const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
                if (deviceInfo == nullptr) continue;
                
                // ASIO入力デバイス
                if (deviceInfo->maxInputChannels > 0) {
                    AudioDeviceInfo info;
                    info.index = static_cast<int>(deviceList.size()) + 1;
                    info.deviceType = 'A';  // ASIO
                    info.inputOutput = 'I';
                    info.deviceName = deviceInfo->name;
                    info.totalChannels = deviceInfo->maxInputChannels;
                    info.hostApiIndex = i;
                    info.deviceIndex = deviceIndex;
                    info.defaultSampleRate = deviceInfo->defaultSampleRate;
                    info.supportsLoopback = false;
                    deviceList.push_back(info);
                }
                
                // ASIO出力デバイス
                if (deviceInfo->maxOutputChannels > 0) {
                    AudioDeviceInfo info;
                    info.index = static_cast<int>(deviceList.size()) + 1;
                    info.deviceType = 'A';  // ASIO
                    info.inputOutput = 'O';
                    info.deviceName = deviceInfo->name;
                    info.totalChannels = deviceInfo->maxOutputChannels;
                    info.hostApiIndex = i;
                    info.deviceIndex = deviceIndex;
                    info.defaultSampleRate = deviceInfo->defaultSampleRate;
                    info.supportsLoopback = false;
                    deviceList.push_back(info);
                }
            }
        }
    }
}

void AudioSystem::printDeviceInfo(const AudioDeviceInfo& device) {
    std::cout << device.index << ","
              << device.deviceType << ","
              << device.inputOutput << ","
              << device.deviceName << ","
              << device.totalChannels;
    
    if (device.supportsLoopback) {
        std::cout << ",LOOPBACK";
    }
    
    std::cout << std::endl;
}

std::vector<AudioDeviceInfo> AudioSystem::getDeviceList() const {
    return deviceList;
}

AudioDeviceInfo* AudioSystem::getDevice(int index) {
    if (index < 1 || index > static_cast<int>(deviceList.size())) {
        return nullptr;
    }
    return &deviceList[index - 1];
}

void AudioSystem::addWASAPILoopbackDevices() {
    // WASAPILoopbackRecorderを使用してネイティブなループバックデバイスを列挙
    WASAPILoopbackRecorder loopbackRecorder;
    
    if (loopbackRecorder.enumerateRenderDevices()) {
        std::vector<std::wstring> renderDeviceNames = loopbackRecorder.getRenderDeviceNames();
        
        for (size_t i = 0; i < renderDeviceNames.size(); i++) {
            AudioDeviceInfo info;
            info.index = static_cast<int>(deviceList.size()) + 1;
            info.deviceType = 'W';  // W = WASAPI（Core Audio API実装でもWASAPIなのでW）
            info.inputOutput = 'O'; // 物理的には出力デバイス（スピーカー等）
            
            // wstringからstringに変換
            std::wstring wDeviceName = renderDeviceNames[i];
            int size = WideCharToMultiByte(CP_UTF8, 0, wDeviceName.c_str(), -1, nullptr, 0, nullptr, nullptr);
            if (size > 0) {
                std::vector<char> utf8Buffer(size);
                WideCharToMultiByte(CP_UTF8, 0, wDeviceName.c_str(), -1, utf8Buffer.data(), size, nullptr, nullptr);
                info.deviceName = std::string(utf8Buffer.data()) + " (WASAPI-Loopback)";
            } else {
                info.deviceName = "Unknown WASAPI Loopback Device";
            }
            
            info.totalChannels = 2;  // 通常はステレオ
            info.hostApiIndex = -1;  // Core Audio API直接実装のため-1
            info.deviceIndex = static_cast<PaDeviceIndex>(i);  // WASAPILoopbackRecorder内のインデックス
            info.defaultSampleRate = 44100.0;
            info.supportsLoopback = true;  // 常にループバック対応
            
            deviceList.push_back(info);
        }
    }
}

void AudioSystem::printSystemInfo() {
    std::cout << "PortAudio version: " << Pa_GetVersionText() << std::endl;
    std::cout << "Host APIs available:" << std::endl;
    
    int numHostApis = Pa_GetHostApiCount();
    for (int i = 0; i < numHostApis; i++) {
        const PaHostApiInfo* info = Pa_GetHostApiInfo(i);
        if (info) {
            std::cout << "  " << i << ": " << info->name 
                      << " (devices: " << info->deviceCount << ")" << std::endl;
        }
    }
    
    std::cout << std::endl;
    std::cout << "Windows Core Audio API (WASAPI Loopback) も利用可能です" << std::endl;
}