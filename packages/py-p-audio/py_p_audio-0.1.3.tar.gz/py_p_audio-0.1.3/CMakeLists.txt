cmake_minimum_required(VERSION 3.15)
set(CMAKE_POLICY_VERSION_MINIMUM 3.5)
project(p-audio VERSION 1.0.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(BUILD_CLI "Build CLI executable (p-audio)" ON)

# PortAudioの設定（PORTAUDIO_ROOTが無い場合はFetchContentで取得）
set(PORTAUDIO_ROOT "C:/portaudio_install" CACHE PATH "Path to PortAudio root (optional)")
include(FetchContent)
set(USE_FETCH_PORTAUDIO OFF)
if(NOT EXISTS "${PORTAUDIO_ROOT}/include" OR NOT EXISTS "${PORTAUDIO_ROOT}/lib")
    set(USE_FETCH_PORTAUDIO ON)
endif()
if(DEFINED SKBUILD)
    # Wheelビルドでは常に同梱ビルドに切り替える
    set(USE_FETCH_PORTAUDIO ON)
endif()

# インクルードディレクトリ
if(USE_FETCH_PORTAUDIO)
    # PortAudioを取得してビルド
    FetchContent_Declare(
        portaudio
        GIT_REPOSITORY https://github.com/PortAudio/portaudio.git
        GIT_TAG v19.7.0
        GIT_SHALLOW TRUE
    )
    # 静的ライブラリのみをビルド（配布Wheelに同梱しやすくする）
    set(PA_BUILD_SHARED OFF CACHE BOOL "" FORCE)
    set(PA_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(PA_BUILD_TESTS OFF CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(portaudio)
    # PortAudioターゲット名の解決
    if(TARGET portaudio_static)
        set(PORTAUDIO_TARGET portaudio_static)
    elseif(TARGET portaudio)
        set(PORTAUDIO_TARGET portaudio)
    else()
        message(FATAL_ERROR "PortAudio target not found after FetchContent")
    endif()
else()
    include_directories("${PORTAUDIO_ROOT}/include")
endif()

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
set(PYBIND11_FINDPYTHON ON)
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
    ${CMAKE_CURRENT_SOURCE_DIR}/asiosdk/common
    ${CMAKE_CURRENT_SOURCE_DIR}/asiosdk/host
)
if(NOT USE_FETCH_PORTAUDIO)
    target_include_directories(paudio PRIVATE ${PORTAUDIO_ROOT}/include)
endif()

if(USE_FETCH_PORTAUDIO)
    target_link_libraries(paudio PRIVATE ${PORTAUDIO_TARGET})
else()
    target_link_libraries(paudio PRIVATE
        "${PORTAUDIO_ROOT}/lib/portaudio_static_x86.lib"
    )
endif()
target_link_libraries(paudio PRIVATE ole32 winmm dsound uuid setupapi propsys)

if(WIN32)
    target_compile_definitions(paudio PRIVATE
        WIN32_LEAN_AND_MEAN
        NOMINMAX
        _CRT_SECURE_NO_WARNINGS
    )
endif()

if(MSVC)
    target_compile_options(paudio PRIVATE /W4 /utf-8)
else()
    target_compile_options(paudio PRIVATE -Wall -Wextra)
endif()

# 実行ファイル
if(BUILD_CLI)
    add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})
    if(USE_FETCH_PORTAUDIO)
        target_link_libraries(${PROJECT_NAME} PRIVATE ${PORTAUDIO_TARGET})
    else()
        target_link_libraries(${PROJECT_NAME} PRIVATE "${PORTAUDIO_ROOT}/lib/portaudio_static_x86.lib")
    endif()
    target_link_libraries(${PROJECT_NAME} PRIVATE ole32 winmm dsound uuid setupapi)
endif()

if(TARGET ${PROJECT_NAME})
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
        target_compile_options(${PROJECT_NAME} PRIVATE /W4 /utf-8)
        set_property(TARGET ${PROJECT_NAME} PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    else()
        target_compile_options(${PROJECT_NAME} PRIVATE -Wall -Wextra)
    endif()

    # デバッグとリリースの設定
    set_target_properties(${PROJECT_NAME} PROPERTIES
        DEBUG_POSTFIX "_d"
        RELEASE_POSTFIX ""
    )
endif()