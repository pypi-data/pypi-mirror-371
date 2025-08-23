"""Exception definitions for py-p-audio"""

from typing import Optional


class PyPAudioError(Exception):
    """Base exception for all py-p-audio errors"""
    
    def __init__(self, message: str, device_name: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.device_name = device_name


class DeviceError(PyPAudioError):
    """Exception raised for device-related errors"""
    pass


class RecordingError(PyPAudioError):
    """Exception raised for recording-related errors"""
    pass


class PlaybackError(PyPAudioError):
    """Exception raised for playback-related errors"""
    pass


class ChannelError(PyPAudioError):
    """Exception raised for channel specification errors"""
    pass


class FormatError(PyPAudioError):
    """Exception raised for audio format errors"""
    pass


class FileError(PyPAudioError):
    """Exception raised for file I/O errors"""
    pass