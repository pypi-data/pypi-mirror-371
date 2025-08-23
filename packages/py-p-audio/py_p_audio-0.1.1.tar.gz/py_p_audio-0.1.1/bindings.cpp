#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "AudioSystem.h"
#include "AudioPlayer.h"
#include "AudioRecorder.h"

namespace py = pybind11;

PYBIND11_MODULE(paudio, m) {
    m.doc() = "Python bindings for p-audio (Audio Device Management, Playback & Recording Tool)";

    // クラス: Player（非ブロッキング再生制御用）
    py::class_<AudioPlayer>(m, "Player")
        .def(py::init<>())
        .def("load", &AudioPlayer::loadFile, py::arg("file_path"))
        .def("start", &AudioPlayer::startPlayback)
        .def("stop", &AudioPlayer::stopPlayback)
        .def("is_playing", &AudioPlayer::isPlaying)
        .def("current_time", &AudioPlayer::getCurrentTimeSeconds)
        .def("total_time", &AudioPlayer::getTotalTimeSeconds)
        .def("format_time", &AudioPlayer::formatTime, py::arg("seconds"));

    // クラス: Recorder（非ブロッキング録音制御用）
    py::class_<AudioRecorder>(m, "Recorder")
        .def(py::init<>())
        .def("setup",
            [](AudioRecorder &self, const std::string &outputPath) {
                return self.setupRecording(outputPath);
            },
            py::arg("output_path"))
        .def("setup",
            [](AudioRecorder &self, const std::string &outputPath, int deviceIndex, std::pair<int,int> channels) {
                return self.setupRecording(outputPath, deviceIndex, channels.first, channels.second);
            },
            py::arg("output_path"), py::arg("device_index"), py::arg("channels"))
        .def("start", &AudioRecorder::startRecording)
        .def("stop", &AudioRecorder::stopRecording)
        .def("is_recording", &AudioRecorder::isRecording)
        .def("current_time", &AudioRecorder::getCurrentTimeSeconds);

    // デバイス列挙
    m.def("list_devices", []() {
        AudioSystem sys;
        sys.initialize();
        sys.enumerateDevices();
        sys.printSystemInfo();
    }, "List available audio devices");

    // 再生
    m.def("play", [](const std::string &filePath) {
        AudioPlayer player;
        if (!player.loadFile(filePath)) {
            throw std::runtime_error("Failed to load file: " + filePath);
        }
        player.startPlayback();
        while (player.isPlaying()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }, "Play an audio file");

    // 録音 (デフォルトデバイス)
    m.def("record", [](const std::string &outputPath,
                       int deviceIndex = -1,
                       std::pair<int,int> channels = {-1,-1}) {
        AudioRecorder recorder;
        bool ok = false;
        if (deviceIndex >= 1 && channels.first >= 0 && channels.second >= 0) {
            ok = recorder.setupRecording(outputPath, deviceIndex, channels.first, channels.second);
        } else {
            ok = recorder.setupRecording(outputPath);
        }
        if (!ok) {
            throw std::runtime_error("Failed to setup recording");
        }
        recorder.startRecording();
        while (recorder.isRecording()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    },
    py::arg("output_path"),
    py::arg("deviceIndex") = -1,
    py::arg("channels") = std::pair<int,int>{-1,-1},
    "Record audio to the given path, optionally specifying device and channels");
}