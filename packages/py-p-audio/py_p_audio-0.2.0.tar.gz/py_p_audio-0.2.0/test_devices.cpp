#include <iostream>
#include <portaudio.h>
#include <vector>
#include <string>

int main() {
    // PortAudio初期化
    PaError err = Pa_Initialize();
    if (err != paNoError) {
        std::cerr << "PortAudio初期化エラー: " << Pa_GetErrorText(err) << std::endl;
        return 1;
    }

    std::cout << "===== オーディオデバイス列挙テスト =====" << std::endl;
    std::cout << std::endl;

    // ホストAPI情報
    int numHostApis = Pa_GetHostApiCount();
    std::cout << "検出されたホストAPI数: " << numHostApis << std::endl;
    std::cout << std::endl;

    for (int i = 0; i < numHostApis; i++) {
        const PaHostApiInfo* hostApiInfo = Pa_GetHostApiInfo(i);
        if (hostApiInfo == nullptr) continue;

        std::string apiType = "Unknown";
        switch (hostApiInfo->type) {
            case paDirectSound: apiType = "DirectSound"; break;
            case paMME: apiType = "MME"; break;
            case paASIO: apiType = "ASIO"; break;
            case paWDMKS: apiType = "WDMKS"; break;
            case paWASAPI: apiType = "WASAPI"; break;
            default: break;
        }

        std::cout << "ホストAPI[" << i << "]: " << hostApiInfo->name 
                  << " (Type: " << apiType << ")" << std::endl;
        std::cout << "  デバイス数: " << hostApiInfo->deviceCount << std::endl;

        // このホストAPIのデバイスを列挙
        for (int j = 0; j < hostApiInfo->deviceCount; j++) {
            PaDeviceIndex deviceIndex = Pa_HostApiDeviceIndexToDeviceIndex(i, j);
            if (deviceIndex < 0) continue;

            const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
            if (deviceInfo == nullptr) continue;

            std::cout << "    デバイス[" << deviceIndex << "]: " << deviceInfo->name << std::endl;
            std::cout << "      入力Ch: " << deviceInfo->maxInputChannels 
                      << ", 出力Ch: " << deviceInfo->maxOutputChannels << std::endl;
            std::cout << "      デフォルトサンプルレート: " << deviceInfo->defaultSampleRate << " Hz" << std::endl;
            std::cout << "      レイテンシ: 入力=" << deviceInfo->defaultLowInputLatency * 1000 << "ms, "
                      << "出力=" << deviceInfo->defaultLowOutputLatency * 1000 << "ms" << std::endl;
        }
        std::cout << std::endl;
    }

    // ASIO専用の検出
    std::cout << "===== ASIO デバイス専用リスト =====" << std::endl;
    int asioDeviceCount = 0;
    
    for (int i = 0; i < numHostApis; i++) {
        const PaHostApiInfo* hostApiInfo = Pa_GetHostApiInfo(i);
        if (hostApiInfo == nullptr) continue;
        
        if (hostApiInfo->type == paASIO) {
            std::cout << "ASIOホストAPI検出!" << std::endl;
            
            for (int j = 0; j < hostApiInfo->deviceCount; j++) {
                PaDeviceIndex deviceIndex = Pa_HostApiDeviceIndexToDeviceIndex(i, j);
                if (deviceIndex < 0) continue;
                
                const PaDeviceInfo* deviceInfo = Pa_GetDeviceInfo(deviceIndex);
                if (deviceInfo == nullptr) continue;
                
                asioDeviceCount++;
                std::cout << "  ASIO Device " << asioDeviceCount << ": " << deviceInfo->name << std::endl;
                std::cout << "    入力: " << deviceInfo->maxInputChannels << " ch" << std::endl;
                std::cout << "    出力: " << deviceInfo->maxOutputChannels << " ch" << std::endl;
            }
        }
    }
    
    if (asioDeviceCount == 0) {
        std::cout << "ASIOデバイスが検出されませんでした。" << std::endl;
        std::cout << "ASIOドライバーがインストールされているか確認してください。" << std::endl;
    }

    Pa_Terminate();
    
    std::cout << std::endl;
    std::cout << "テスト完了" << std::endl;
    
    return 0;
}