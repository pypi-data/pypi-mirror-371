"""
py-p-audio: Professional Python audio library with WASAPI/ASIO support for Windows

This library provides comprehensive audio recording and playback capabilities
with support for WASAPI (including loopback) and ASIO devices on Windows.
"""

__version__ = "1.0.0"
__author__ = "hiroshi-tamura"

# High-level API
from .api import (
    Recorder, LoopbackRecorder, Player,
    record, record_system_audio, play,
    list_audio_devices
)

# Core functionality
from .core.devices import list_devices, get_device_info, DeviceInfo, DeviceType
from .core.callbacks import APIType, AudioMode, AudioStatus, CallbackInfo
from .core.channels import ChannelSpec, parse_channels

# Low-level recording classes
from .recording.wasapi import WASAPIRecorder
from .recording.asio import ASIORecorder
from .recording.loopback import WASAPILoopbackRecorder

# Low-level playback classes
from .playback.wasapi import WASAPIPlayer
from .playback.asio import ASIOPlayer

# Exceptions
from .utils.exceptions import (
    PyPAudioError, DeviceError, RecordingError, 
    PlaybackError, ChannelError, FormatError, FileError
)

# Convenience imports for callback creation
from .core.callbacks import (
    create_simple_progress_callback,
    create_detailed_progress_callback
)

__all__ = [
    # High-level API
    "Recorder", "LoopbackRecorder", "Player",
    "record", "record_system_audio", "play",
    "list_audio_devices",
    
    # Core types
    "DeviceInfo", "DeviceType", "APIType", "AudioMode", "AudioStatus",
    "CallbackInfo", "ChannelSpec",
    
    # Device management
    "list_devices", "get_device_info", "parse_channels",
    
    # Low-level classes
    "WASAPIRecorder", "ASIORecorder", "WASAPILoopbackRecorder",
    "WASAPIPlayer", "ASIOPlayer",
    
    # Exceptions
    "PyPAudioError", "DeviceError", "RecordingError", 
    "PlaybackError", "ChannelError", "FormatError", "FileError",
    
    # Callback helpers
    "create_simple_progress_callback", "create_detailed_progress_callback",
]