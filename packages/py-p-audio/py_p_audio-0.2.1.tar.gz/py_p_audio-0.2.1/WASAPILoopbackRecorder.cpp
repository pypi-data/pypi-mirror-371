#include "WASAPILoopbackRecorder.h"
#pragma execution_character_set("utf-8")
#include <iostream>
#include <iomanip>
#include <sstream>
#include <chrono>
#include <comdef.h>
#include <propvarutil.h>

// COM初期化RAII実装
COMInitializer::COMInitializer() : initialized(false) {
    // 最初にAPARTMENTTHREADEDを試す
    HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(hr)) {
        // 失敗した場合はMULTITHREADEDを試す
        hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    }
    
    // S_OKまたはS_FALSE（既に初期化済み）の場合も成功とする
    if (SUCCEEDED(hr) || hr == RPC_E_CHANGED_MODE) {
        initialized = true;
    }
}

COMInitializer::~COMInitializer() {
    if (initialized) {
        CoUninitialize();
    }
}

// WASAPILoopbackRecorder実装
WASAPILoopbackRecorder::WASAPILoopbackRecorder() 
    : deviceEnumerator(nullptr)
    , renderDevice(nullptr)
    , audioClient(nullptr)
    , captureClient(nullptr)
    , recording(false)
    , mixFormat(nullptr)
    , bufferFrameCount(0)
    , totalBytesWritten(0) {
}

WASAPILoopbackRecorder::~WASAPILoopbackRecorder() {
    stopRecording();
    cleanup();
}

void WASAPILoopbackRecorder::cleanup() {
    if (captureClient) {
        captureClient->Release();
        captureClient = nullptr;
    }
    
    if (audioClient) {
        audioClient->Release();
        audioClient = nullptr;
    }
    
    if (renderDevice) {
        renderDevice->Release();
        renderDevice = nullptr;
    }
    
    if (deviceEnumerator) {
        deviceEnumerator->Release();
        deviceEnumerator = nullptr;
    }
    
    if (mixFormat) {
        CoTaskMemFree(mixFormat);
        mixFormat = nullptr;
    }
    
    if (outputFile && outputFile->is_open()) {
        updateWAVHeader();
        outputFile->close();
    }
}

void WASAPILoopbackRecorder::setError(const std::string& error) {
    lastError = error;
    std::cerr << "WASAPILoopbackRecorder Error: " << error << std::endl;
}

bool WASAPILoopbackRecorder::enumerateRenderDevices() {
    if (!comInit.isInitialized()) {
        setError("COM初期化に失敗しました");
        return false;
    }
    
    // デバイス列挙器を作成
    HRESULT hr = CoCreateInstance(
        __uuidof(MMDeviceEnumerator),
        nullptr,
        CLSCTX_ALL,
        __uuidof(IMMDeviceEnumerator),
        reinterpret_cast<void**>(&deviceEnumerator)
    );
    
    if (FAILED(hr)) {
        setError("デバイス列挙器の作成に失敗しました");
        return false;
    }
    
    // レンダリングデバイスを列挙
    IMMDeviceCollection* deviceCollection = nullptr;
    hr = deviceEnumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, &deviceCollection);
    
    if (FAILED(hr)) {
        setError("レンダリングデバイスの列挙に失敗しました");
        return false;
    }
    
    UINT deviceCount = 0;
    deviceCollection->GetCount(&deviceCount);
    
    renderDevices.clear();
    
    for (UINT i = 0; i < deviceCount; i++) {
        IMMDevice* device = nullptr;
        hr = deviceCollection->Item(i, &device);
        
        if (SUCCEEDED(hr)) {
            RenderDeviceInfo info;
            
            // デバイスIDを取得
            LPWSTR deviceId = nullptr;
            if (SUCCEEDED(device->GetId(&deviceId))) {
                info.id = deviceId;
                CoTaskMemFree(deviceId);
            }
            
            // デバイス名を取得
            IPropertyStore* propertyStore = nullptr;
            if (SUCCEEDED(device->OpenPropertyStore(STGM_READ, &propertyStore))) {
                PROPVARIANT friendlyName;
                PropVariantInit(&friendlyName);
                
                if (SUCCEEDED(propertyStore->GetValue(PKEY_Device_FriendlyName, &friendlyName))) {
                    if (friendlyName.vt == VT_LPWSTR) {
                        info.name = friendlyName.pwszVal;
                    }
                }
                
                PropVariantClear(&friendlyName);
                propertyStore->Release();
            }
            
            // デバイス説明を取得
            PROPVARIANT deviceDesc;
            PropVariantInit(&deviceDesc);
            IPropertyStore* store = nullptr;
            if (SUCCEEDED(device->OpenPropertyStore(STGM_READ, &store))) {
                if (SUCCEEDED(store->GetValue(PKEY_Device_DeviceDesc, &deviceDesc))) {
                    if (deviceDesc.vt == VT_LPWSTR) {
                        info.description = deviceDesc.pwszVal;
                    }
                }
                PropVariantClear(&deviceDesc);
                store->Release();
            }
            
            renderDevices.push_back(info);
            device->Release();
        }
    }
    
    deviceCollection->Release();
    return true;
}

void WASAPILoopbackRecorder::printRenderDevices() {
    SetConsoleOutputCP(CP_UTF8);
    
    std::wcout << L"=== WASAPI レンダリングデバイス (ループバック録音対応) ===" << std::endl;
    
    for (size_t i = 0; i < renderDevices.size(); i++) {
        std::wcout << L"デバイス " << (i + 1) << L": " << renderDevices[i].name;
        std::wcout << L" (ループバック録音対応)" << std::endl;
        if (!renderDevices[i].description.empty()) {
            std::wcout << L"  説明: " << renderDevices[i].description << std::endl;
        }
    }
    
    if (renderDevices.empty()) {
        std::wcout << L"レンダリングデバイスが見つかりませんでした。" << std::endl;
    }
}

std::vector<std::wstring> WASAPILoopbackRecorder::getRenderDeviceNames() const {
    std::vector<std::wstring> names;
    for (const auto& device : renderDevices) {
        names.push_back(device.name);
    }
    return names;
}

bool WASAPILoopbackRecorder::initialize(int deviceIndex) {
    if (!comInit.isInitialized()) {
        setError("COM初期化に失敗しました");
        return false;
    }
    
    cleanup();
    
    if (!initializeCoreAudio()) {
        return false;
    }
    
    // デバイスを選択
    HRESULT hr;
    if (deviceIndex == -1) {
        // デフォルトレンダリングデバイスを取得
        hr = deviceEnumerator->GetDefaultAudioEndpoint(eRender, eConsole, &renderDevice);
    } else {
        // 指定されたデバイスを取得
        if (deviceIndex < 1 || deviceIndex > static_cast<int>(renderDevices.size())) {
            setError("無効なデバイスインデックスです");
            return false;
        }
        
        hr = deviceEnumerator->GetDevice(renderDevices[deviceIndex - 1].id.c_str(), &renderDevice);
    }
    
    if (FAILED(hr)) {
        setError("レンダリングデバイスの取得に失敗しました");
        return false;
    }
    
    // AudioClientを取得
    hr = renderDevice->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr, reinterpret_cast<void**>(&audioClient));
    if (FAILED(hr)) {
        setError("AudioClientの取得に失敗しました");
        return false;
    }
    
    // ミックスフォーマットを取得
    hr = audioClient->GetMixFormat(&mixFormat);
    if (FAILED(hr)) {
        setError("ミックスフォーマットの取得に失敗しました");
        return false;
    }
    
    // ループバックモードでAudioClientを初期化
    hr = audioClient->Initialize(
        AUDCLNT_SHAREMODE_SHARED,
        AUDCLNT_STREAMFLAGS_LOOPBACK,  // ここが重要！ループバックフラグ
        0,
        0,
        mixFormat,
        nullptr
    );
    
    if (FAILED(hr)) {
        std::stringstream ss;
        ss << "AudioClientの初期化に失敗しました (HRESULT: 0x" << std::hex << hr << ")";
        setError(ss.str());
        return false;
    }
    
    // バッファサイズを取得
    hr = audioClient->GetBufferSize(&bufferFrameCount);
    if (FAILED(hr)) {
        setError("バッファサイズの取得に失敗しました");
        return false;
    }
    
    // CaptureClientを取得
    hr = audioClient->GetService(__uuidof(IAudioCaptureClient), reinterpret_cast<void**>(&captureClient));
    if (FAILED(hr)) {
        setError("CaptureClientの取得に失敗しました");
        return false;
    }
    
    std::cout << "WASAPIループバック録音の初期化に成功しました" << std::endl;
    std::cout << "サンプルレート: " << mixFormat->nSamplesPerSec << " Hz" << std::endl;
    std::cout << "チャンネル数: " << mixFormat->nChannels << std::endl;
    std::cout << "ビット深度: " << mixFormat->wBitsPerSample << " bit" << std::endl;
    std::cout << "バッファサイズ: " << bufferFrameCount << " フレーム" << std::endl;
    
    return true;
}

bool WASAPILoopbackRecorder::initializeCoreAudio() {
    // デバイス列挙器を作成（まだ作成されていない場合）
    if (!deviceEnumerator) {
        HRESULT hr = CoCreateInstance(
            __uuidof(MMDeviceEnumerator),
            nullptr,
            CLSCTX_ALL,
            __uuidof(IMMDeviceEnumerator),
            reinterpret_cast<void**>(&deviceEnumerator)
        );
        
        if (FAILED(hr)) {
            setError("デバイス列挙器の作成に失敗しました");
            return false;
        }
    }
    
    return true;
}

bool WASAPILoopbackRecorder::createWAVFile(const std::string& filename) {
    outputFile = std::make_unique<std::ofstream>(filename, std::ios::binary);
    if (!outputFile->is_open()) {
        setError("出力ファイルの作成に失敗しました: " + filename);
        return false;
    }
    
    outputFilename = filename;
    totalBytesWritten = 0;
    
    // WAVヘッダーを設定
    wavHeader.channels = mixFormat->nChannels;
    wavHeader.sampleRate = mixFormat->nSamplesPerSec;
    wavHeader.bitsPerSample = mixFormat->wBitsPerSample;
    wavHeader.byteRate = wavHeader.sampleRate * wavHeader.channels * (wavHeader.bitsPerSample / 8);
    wavHeader.blockAlign = wavHeader.channels * (wavHeader.bitsPerSample / 8);
    
    // Float32の場合はIEEE floatフォーマットを設定
    if (mixFormat->wFormatTag == WAVE_FORMAT_IEEE_FLOAT || 
        (mixFormat->wFormatTag == WAVE_FORMAT_EXTENSIBLE && mixFormat->wBitsPerSample == 32)) {
        wavHeader.audioFormat = 3;  // IEEE float
    }
    
    writeWAVHeader();
    return true;
}

void WASAPILoopbackRecorder::writeWAVHeader() {
    if (!outputFile) return;
    
    outputFile->seekp(0);
    outputFile->write(reinterpret_cast<const char*>(&wavHeader), sizeof(WAVHeader));
    outputFile->flush();
}

void WASAPILoopbackRecorder::updateWAVHeader() {
    if (!outputFile) return;
    
    wavHeader.dataSize = totalBytesWritten;
    wavHeader.fileSize = 36 + totalBytesWritten;
    
    writeWAVHeader();
}

void WASAPILoopbackRecorder::writeAudioData(BYTE* data, UINT32 frameCount) {
    if (!outputFile || !data) return;
    
    UINT32 bytesToWrite = frameCount * mixFormat->nBlockAlign;
    outputFile->write(reinterpret_cast<const char*>(data), bytesToWrite);
    totalBytesWritten += bytesToWrite;
}

bool WASAPILoopbackRecorder::startRecording(const std::string& filename) {
    if (recording.load()) {
        setError("既に録音中です");
        return false;
    }
    
    if (!audioClient || !captureClient) {
        setError("AudioClientまたはCaptureClientが初期化されていません");
        return false;
    }
    
    if (!createWAVFile(filename)) {
        return false;
    }
    
    // 録音開始
    HRESULT hr = audioClient->Start();
    if (FAILED(hr)) {
        setError("録音の開始に失敗しました");
        return false;
    }
    
    recording.store(true);
    recordingThread = std::thread(&WASAPILoopbackRecorder::recordingLoop, this);
    
    std::cout << "WASAPIループバック録音を開始しました: " << filename << std::endl;
    return true;
}

void WASAPILoopbackRecorder::stopRecording() {
    if (!recording.load()) {
        return;
    }
    
    recording.store(false);
    
    if (recordingThread.joinable()) {
        recordingThread.join();
    }
    
    if (audioClient) {
        audioClient->Stop();
    }
    
    if (outputFile && outputFile->is_open()) {
        updateWAVHeader();
        outputFile->close();
        std::cout << "録音を停止しました: " << outputFilename << std::endl;
        std::cout << "録音データサイズ: " << totalBytesWritten << " バイト" << std::endl;
    }
}

void WASAPILoopbackRecorder::recordingLoop() {
    const DWORD timeoutMs = 100;
    auto lastWriteTime = std::chrono::steady_clock::now();
    
    std::cout << "Recording loop started" << std::endl;
    
    while (recording.load()) {
        UINT32 packetLength = 0;
        HRESULT hr = captureClient->GetNextPacketSize(&packetLength);
        
        if (FAILED(hr)) {
            setError("パケットサイズの取得に失敗しました");
            break;
        }
        
        // パケットがある場合は処理
        bool dataWritten = false;
        while (packetLength > 0 && recording.load()) {
            BYTE* data = nullptr;
            UINT32 frameCount = 0;
            DWORD flags = 0;
            
            hr = captureClient->GetBuffer(&data, &frameCount, &flags, nullptr, nullptr);
            
            if (SUCCEEDED(hr)) {
                if (!(flags & AUDCLNT_BUFFERFLAGS_SILENT)) {
                    writeAudioData(data, frameCount);
                } else {
                    // 無音データの場合は0で埋める
                    std::vector<BYTE> silentData(frameCount * mixFormat->nBlockAlign, 0);
                    writeAudioData(silentData.data(), frameCount);
                }
                dataWritten = true;
                lastWriteTime = std::chrono::steady_clock::now();
                
                captureClient->ReleaseBuffer(frameCount);
            } else {
                setError("バッファの取得に失敗しました");
                break;
            }
            
            hr = captureClient->GetNextPacketSize(&packetLength);
            if (FAILED(hr)) {
                break;
            }
        }
        
        // パケットがない場合でも、一定時間経過したら無音データを書き込む
        if (!dataWritten) {
            auto now = std::chrono::steady_clock::now();
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - lastWriteTime).count();
            
            // 100ms経過したら無音データを書き込む
            if (elapsed >= timeoutMs) {
                // 100ms分の無音データを書き込み
                UINT32 silentFrames = (mixFormat->nSamplesPerSec * timeoutMs) / 1000;
                std::vector<BYTE> silentData(silentFrames * mixFormat->nBlockAlign, 0);
                writeAudioData(silentData.data(), silentFrames);
                lastWriteTime = now;
                
                // 進捗表示を無効化（main.cppのタイムカウンターと競合するため）
                // if (++loopCount % 10 == 0) {
                //     // 進捗表示処理はコメントアウト
                // }
            }
        }
        
        Sleep(10);  // CPU使用率を下げるため短いスリープ
    }
}