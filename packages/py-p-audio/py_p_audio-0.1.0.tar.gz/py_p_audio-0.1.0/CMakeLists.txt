cmake_minimum_required(VERSION 3.10)
project(p-audio VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# PortAudioの設定
set(PORTAUDIO_ROOT "C:/portaudio_install")

# インクルードディレクトリ
include_directories("${PORTAUDIO_ROOT}/include")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/asiosdk/common")
include_directories("${CMAKE_CURRENT_SOURCE_DIR}/asiosdk/host")

# ソースファイル
set(SOURCES
    main.cpp
    AudioSystem.cpp
    AudioRecorder.cpp
    AudioPlayer.cpp
    WASAPILoopbackRecorder.cpp
)

# ヘッダーファイル
set(HEADERS
    AudioSystem.h
    AudioRecorder.h
    AudioPlayer.h
    WASAPILoopbackRecorder.h
)

# PyBind11 Python module
find_package(pybind11 REQUIRED)

set(BINDING_SOURCES
    bindings.cpp
    AudioSystem.cpp
    AudioRecorder.cpp
    AudioPlayer.cpp
    WASAPILoopbackRecorder.cpp
)

pybind11_add_module(paudio ${BINDING_SOURCES})

target_include_directories(paudio PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${PORTAUDIO_ROOT}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/asiosdk/common
    ${CMAKE_CURRENT_SOURCE_DIR}/asiosdk/host
)

target_link_libraries(paudio
    "${PORTAUDIO_ROOT}/lib/portaudio_static_x86.lib"
    ole32
    winmm
    dsound
    uuid
    setupapi
)

if(WIN32)
    target_compile_definitions(paudio PRIVATE
        WIN32_LEAN_AND_MEAN
        NOMINMAX
        _CRT_SECURE_NO_WARNINGS
    )
endif()

if(MSVC)
    target_compile_options(paudio PRIVATE /W4 /MT /utf-8)
    set_property(TARGET paudio PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
else()
    target_compile_options(paudio PRIVATE -Wall -Wextra)
endif()

# 実行ファイル
add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# ライブラリリンク
target_link_libraries(${PROJECT_NAME} 
    "${PORTAUDIO_ROOT}/lib/portaudio_static_x86.lib"
    ole32
    winmm
    dsound
    uuid
    setupapi
    # Windows Core Audio API用ライブラリ（実際はOLE32とUUIDに含まれている）
)

# Windows特有の定義
if(WIN32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE 
        WIN32_LEAN_AND_MEAN
        NOMINMAX
        _CRT_SECURE_NO_WARNINGS
    )
endif()

# コンパイラフラグ
if(MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE /W4 /MT /utf-8)
    set_property(TARGET ${PROJECT_NAME} PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
else()
    target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra)
endif()

# デバッグとリリースの設定
set_target_properties(${PROJECT_NAME} PROPERTIES
    DEBUG_POSTFIX "_d"
    RELEASE_POSTFIX ""
)