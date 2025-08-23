#pragma execution_character_set("utf-8")
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <thread>
#include <chrono>
#include <conio.h>
#include <Windows.h>

#include "AudioSystem.h"
#include "AudioRecorder.h"
#include "AudioPlayer.h"

void printUsage() {
    std::cout << "p-audio.exe - Audio Device Management, Playback & Recording Tool" << std::endl;
    std::cout << std::endl;
    std::cout << "Usage:" << std::endl;
    std::cout << "  p-audio.exe /d                                    - List audio devices" << std::endl;
    std::cout << "  p-audio.exe /p [file path]                       - Play audio file" << std::endl;
    std::cout << "  p-audio.exe /r [output path]                     - Record audio" << std::endl;
    std::cout << "  p-audio.exe /r [output path] /dv [device,ch]     - Record with device/channel spec" << std::endl;
    std::cout << std::endl;
    std::cout << "Channel specification uses 1-based indexing (ch1-ch2):" << std::endl;
    std::cout << "  - ASIO/WASAPI: 1-2 for stereo channels 1&2" << std::endl;
    std::cout << "  - Loopback devices: typically 1-2" << std::endl;
    std::cout << std::endl;
    std::cout << "Examples:" << std::endl;
    std::cout << "  p-audio.exe /d" << std::endl;
    std::cout << "  p-audio.exe /p \"C:\\music\\test.wav\"" << std::endl;
    std::cout << "  p-audio.exe /r \"C:\\recordings\\\"" << std::endl;
    std::cout << "  p-audio.exe /r \"C:\\recordings\\\" /dv 2,1-2    # ASIO channels 1-2" << std::endl;
    std::cout << "  p-audio.exe /r \"C:\\recordings\\\" /dv 5,1-2    # Loopback stereo" << std::endl;
}

bool checkKeyPressed() {
    // Windows Console Input APIを使用してより確実なキー検出
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    if (hStdin == INVALID_HANDLE_VALUE) return false;
    
    INPUT_RECORD inputRecord[128];
    DWORD eventsRead;
    
    if (!PeekConsoleInput(hStdin, inputRecord, 128, &eventsRead)) {
        return false;
    }
    
    for (DWORD i = 0; i < eventsRead; i++) {
        if (inputRecord[i].EventType == KEY_EVENT && 
            inputRecord[i].Event.KeyEvent.bKeyDown) {
            char key = inputRecord[i].Event.KeyEvent.uChar.AsciiChar;
            if (key == 'q' || key == 'Q') {
                // イベントを消費
                ReadConsoleInput(hStdin, inputRecord, eventsRead, &eventsRead);
                return true;
            }
        }
    }
    
    // 他のイベントを消費
    if (eventsRead > 0) {
        ReadConsoleInput(hStdin, inputRecord, eventsRead, &eventsRead);
    }
    
    return false;
}

std::string convertToUtf8(const char* str) {
    // Convert from system codepage to UTF-8
    int wideSize = MultiByteToWideChar(CP_ACP, 0, str, -1, nullptr, 0);
    if (wideSize == 0) return str;
    
    std::vector<wchar_t> wideStr(wideSize);
    MultiByteToWideChar(CP_ACP, 0, str, -1, wideStr.data(), wideSize);
    
    int utf8Size = WideCharToMultiByte(CP_UTF8, 0, wideStr.data(), -1, nullptr, 0, nullptr, nullptr);
    if (utf8Size == 0) return str;
    
    std::vector<char> utf8Str(utf8Size);
    WideCharToMultiByte(CP_UTF8, 0, wideStr.data(), -1, utf8Str.data(), utf8Size, nullptr, nullptr);
    
    return std::string(utf8Str.data());
}

int main(int argc, char* argv[]) {
    // Set console codepages for proper character handling
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);

    if (argc < 2) {
        printUsage();
        return 1;
    }

    std::string command = argv[1];
    std::transform(command.begin(), command.end(), command.begin(), [](unsigned char c) -> char { return static_cast<char>(std::tolower(c)); });

    // Handle MSYS2 path conversion issues
    bool isDeviceCommand = (command == "/d" || command == "d:/" || 
                           command.find("/d") != std::string::npos);
    bool isPlayCommand = (command == "/p" || command == "p:/" || 
                         command.find("/p") != std::string::npos);
    bool isRecordCommand = (command == "/r" || command == "r:/" || 
                           command.find("/r") != std::string::npos);

    if (isDeviceCommand) {
        // デバイス列挙
        AudioSystem audioSystem;
        audioSystem.initialize();
        audioSystem.enumerateDevices();
        audioSystem.printSystemInfo();
        return 0;
    }
    else if (isPlayCommand) {
        // オーディオ再生
        if (argc < 3) {
            std::cout << "Error: File path not specified." << std::endl;
            printUsage();
            return 1;
        }

        std::string filePath = convertToUtf8(argv[2]);
        AudioPlayer player;
        
        if (!player.loadFile(filePath)) {
            std::cout << "Error: Failed to load file: " << filePath << std::endl;
            return 1;
        }

        std::cout << "Playing: " << filePath << std::endl;
        std::cout << "[q] key to stop" << std::endl;
        
        player.startPlayback();

        while (player.isPlaying()) {
            if (checkKeyPressed()) {
                player.stopPlayback();
                break;
            }
            
            // Windows APIを使用した安全なコンソール更新
            HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
            CONSOLE_SCREEN_BUFFER_INFO csbi;
            GetConsoleScreenBufferInfo(hConsole, &csbi);
            
            std::string timeDisplay = "Playing... " + player.getCurrentTimeString() 
                                    + " / " + player.formatTime(player.getTotalTimeSeconds()) 
                                    + " [q] to stop";
            
            // 現在行をクリアしてから表示
            SetConsoleCursorPosition(hConsole, {0, csbi.dwCursorPosition.Y});
            DWORD written;
            FillConsoleOutputCharacterA(hConsole, ' ', csbi.dwSize.X, csbi.dwCursorPosition, &written);
            SetConsoleCursorPosition(hConsole, {0, csbi.dwCursorPosition.Y});
            WriteConsoleA(hConsole, timeDisplay.c_str(), static_cast<DWORD>(timeDisplay.length()), &written, nullptr);
            
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        std::cout << std::endl << "Playback finished" << std::endl;
        return 0;
    }
    else if (isRecordCommand) {
        // オーディオ録音
        if (argc < 3) {
            std::cout << "Error: Output path not specified." << std::endl;
            printUsage();
            return 1;
        }

        std::string outputPath = convertToUtf8(argv[2]);
        AudioRecorder recorder;
        
        // デバイス指定の確認
        int deviceIndex = -1;
        int startChannel = -1;
        int endChannel = -1;
        
        // /dvパラメータの解析
        for (int i = 3; i < argc - 1; i++) {
            std::string arg = argv[i];
            std::transform(arg.begin(), arg.end(), arg.begin(), [](unsigned char c) -> char { return static_cast<char>(std::tolower(c)); });
            
            if (arg == "/dv" || arg == "dv:/" || arg.find("/dv") != std::string::npos) {
                if (i + 1 < argc) {
                    std::string deviceSpec = argv[i + 1];
                    size_t commaPos = deviceSpec.find(',');
                    if (commaPos != std::string::npos) {
                        deviceIndex = std::stoi(deviceSpec.substr(0, commaPos));
                        std::string channelSpec = deviceSpec.substr(commaPos + 1);
                        size_t dashPos = channelSpec.find('-');
                        if (dashPos != std::string::npos) {
                            startChannel = std::stoi(channelSpec.substr(0, dashPos));
                            endChannel = std::stoi(channelSpec.substr(dashPos + 1));
                        }
                    }
                    break;
                }
            }
        }

        // 録音設定
        if (deviceIndex >= 1 && startChannel >= 0 && endChannel >= 0) {
            if (!recorder.setupRecording(outputPath, deviceIndex, startChannel, endChannel)) {
                std::cout << "Error: Failed to setup recording." << std::endl;
                return 1;
            }
            std::cout << "Recording started: Device " << deviceIndex 
                      << ", Channels " << startChannel << "-" << endChannel << std::endl;
        }
        else {
            if (!recorder.setupRecording(outputPath)) {
                std::cout << "Error: Failed to setup recording." << std::endl;
                return 1;
            }
            std::cout << "Recording started: Default device" << std::endl;
        }
        
        std::cout << "[q] key to stop" << std::endl;
        recorder.startRecording();

        while (recorder.isRecording()) {
            if (checkKeyPressed()) {
                recorder.stopRecording();
                break;
            }
            
            // Windows APIを使用した安全なコンソール更新
            HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
            CONSOLE_SCREEN_BUFFER_INFO csbi;
            GetConsoleScreenBufferInfo(hConsole, &csbi);
            
            std::string timeDisplay = "Recording... " + recorder.getCurrentTimeString() + " [q] to stop";
            
            // 現在行をクリアしてから表示
            SetConsoleCursorPosition(hConsole, {0, csbi.dwCursorPosition.Y});
            DWORD written;
            FillConsoleOutputCharacterA(hConsole, ' ', csbi.dwSize.X, csbi.dwCursorPosition, &written);
            SetConsoleCursorPosition(hConsole, {0, csbi.dwCursorPosition.Y});
            WriteConsoleA(hConsole, timeDisplay.c_str(), static_cast<DWORD>(timeDisplay.length()), &written, nullptr);
            
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        std::cout << std::endl << "Recording finished" << std::endl;
        return 0;
    }
    else {
        std::cout << "Error: Invalid command." << std::endl;
        printUsage();
        return 1;
    }
}