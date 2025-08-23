"""Callback management and information classes"""

import time
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, Dict
from enum import Enum


class AudioMode(Enum):
    """Audio operation mode"""
    RECORDING = "recording"
    PLAYBACK = "playback"
    DUPLEX = "duplex"


class AudioStatus(Enum):
    """Audio operation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class APIType(Enum):
    """Audio API type"""
    WASAPI = "WASAPI"
    ASIO = "ASIO"
    AUTO = "AUTO"


@dataclass
class CallbackInfo:
    """
    Comprehensive information passed to callbacks.
    
    This class contains all information about the current audio operation
    that might be useful for monitoring, display, or control purposes.
    """
    # Time information
    current_time: float  # Current time in seconds
    total_time: Optional[float] = None  # Total time (for playback)
    position: Optional[float] = None  # Position 0.0-1.0 (for playback)
    
    # Device information
    device_name: str = "Unknown"
    api_type: APIType = APIType.AUTO
    mode: AudioMode = AudioMode.RECORDING
    status: AudioStatus = AudioStatus.ACTIVE
    
    # Audio format information
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    buffer_size: Optional[int] = None
    
    # Level information
    peak_levels: List[float] = None  # Peak levels per channel
    rms_levels: List[float] = None   # RMS levels per channel
    
    # Performance information
    latency: Optional[float] = None  # Latency in milliseconds (ASIO)
    cpu_usage: Optional[float] = None  # CPU usage percentage
    buffer_usage: Optional[float] = None  # Buffer usage percentage
    
    # Recording-specific
    file_size: Optional[int] = None  # File size in bytes
    elapsed_samples: Optional[int] = None  # Total samples recorded
    is_silent: Optional[bool] = None  # Silent detection (loopback)
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.peak_levels is None:
            self.peak_levels = [0.0] * self.channels
        if self.rms_levels is None:
            self.rms_levels = [0.0] * self.channels
        if self.warnings is None:
            self.warnings = []
    
    @property
    def max_peak_level(self) -> float:
        """Maximum peak level across all channels"""
        return max(self.peak_levels) if self.peak_levels else 0.0
    
    @property
    def max_rms_level(self) -> float:
        """Maximum RMS level across all channels"""
        return max(self.rms_levels) if self.rms_levels else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'current_time': self.current_time,
            'total_time': self.total_time,
            'position': self.position,
            'device_name': self.device_name,
            'api_type': self.api_type.value,
            'mode': self.mode.value,
            'status': self.status.value,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'bit_depth': self.bit_depth,
            'buffer_size': self.buffer_size,
            'peak_levels': self.peak_levels,
            'rms_levels': self.rms_levels,
            'latency': self.latency,
            'cpu_usage': self.cpu_usage,
            'buffer_usage': self.buffer_usage,
            'file_size': self.file_size,
            'elapsed_samples': self.elapsed_samples,
            'is_silent': self.is_silent,
            'error_message': self.error_message,
            'warnings': self.warnings,
        }


class CallbackManager:
    """Manages callbacks and handles callback invocation"""
    
    def __init__(self):
        self.progress_callback: Optional[Callable[[CallbackInfo], None]] = None
        self.time_callback: Optional[Callable[[float, int, str], None]] = None
        self.error_callback: Optional[Callable[[str, Optional[str]], None]] = None
        self.event_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        self.callback_interval: float = 0.1  # Default 100ms
        self.last_callback_time: float = 0.0
        self.start_time: Optional[float] = None
        
    def set_progress_callback(self, callback: Optional[Callable[[CallbackInfo], None]]):
        """Set progress callback function"""
        self.progress_callback = callback
    
    def set_time_callback(self, callback: Optional[Callable[[float, int, str], None]]):
        """Set simple time callback function (legacy compatibility)"""
        self.time_callback = callback
    
    def set_error_callback(self, callback: Optional[Callable[[str, Optional[str]], None]]):
        """Set error callback function"""
        self.error_callback = callback
    
    def set_event_callback(self, callback: Optional[Callable[[str, Dict[str, Any]], None]]):
        """Set event callback function"""
        self.event_callback = callback
    
    def set_interval(self, interval: float):
        """Set callback interval in seconds"""
        self.callback_interval = max(0.01, interval)  # Minimum 10ms
    
    def start_timing(self):
        """Start timing for callbacks"""
        self.start_time = time.time()
        self.last_callback_time = 0.0
    
    def should_trigger_callback(self, current_time: Optional[float] = None) -> bool:
        """Check if callback should be triggered based on interval"""
        if current_time is None:
            if self.start_time is None:
                return False
            current_time = time.time() - self.start_time
        
        if current_time - self.last_callback_time >= self.callback_interval:
            self.last_callback_time = current_time
            return True
        return False
    
    def trigger_progress_callback(self, info: CallbackInfo):
        """Trigger progress callback if set and interval elapsed"""
        if self.progress_callback and self.should_trigger_callback(info.current_time):
            try:
                self.progress_callback(info)
            except Exception as e:
                self.trigger_error_callback(f"Progress callback error: {e}", info.device_name)
    
    def trigger_time_callback(self, current_time: float, total_samples: int, status: str):
        """Trigger simple time callback if set"""
        if self.time_callback and self.should_trigger_callback(current_time):
            try:
                self.time_callback(current_time, total_samples, status)
            except Exception as e:
                self.trigger_error_callback(f"Time callback error: {e}")
    
    def trigger_error_callback(self, message: str, device_name: Optional[str] = None):
        """Trigger error callback if set"""
        if self.error_callback:
            try:
                self.error_callback(message, device_name)
            except Exception:
                pass  # Don't let error callback errors propagate
    
    def trigger_event_callback(self, event_type: str, data: Dict[str, Any]):
        """Trigger event callback if set"""
        if self.event_callback:
            try:
                self.event_callback(event_type, data)
            except Exception as e:
                self.trigger_error_callback(f"Event callback error: {e}")


def create_simple_progress_callback(format_string: str = "⏺️ {mode} {time:.1f}s [{device}]") -> Callable[[CallbackInfo], None]:
    """
    Create a simple progress callback that prints formatted progress.
    
    Args:
        format_string: Format string with placeholders for CallbackInfo fields
        
    Returns:
        Progress callback function
    """
    def callback(info: CallbackInfo):
        try:
            message = format_string.format(
                mode=info.mode.value,
                time=info.current_time,
                device=info.device_name,
                api=info.api_type.value,
                status=info.status.value,
                peak=info.max_peak_level,
                rms=info.max_rms_level,
                channels=info.channels,
                sample_rate=info.sample_rate,
                latency=info.latency or 0,
                file_size=info.file_size or 0,
            )
            print(f"\r{message}", end="", flush=True)
        except Exception:
            print(f"\r⏺️ {info.current_time:.1f}s", end="", flush=True)
    
    return callback


def create_detailed_progress_callback() -> Callable[[CallbackInfo], None]:
    """Create a detailed progress callback with level meters and performance info"""
    
    def callback(info: CallbackInfo):
        # Clear line and create progress display
        api_icon = "🎵" if info.api_type == APIType.ASIO else "🔊"
        mode_icon = {"recording": "⏺️", "playback": "▶️", "duplex": "🔄"}[info.mode.value]
        
        # Level meter
        peak = info.max_peak_level
        level_bar = "█" * int(peak * 10) + "░" * (10 - int(peak * 10))
        
        # Status
        status_icon = {"active": "✅", "paused": "⏸️", "stopped": "⏹️", "error": "❌"}[info.status.value]
        
        message = (f"\r{api_icon}{mode_icon} {info.device_name} | "
                  f"{info.current_time:.1f}s | "
                  f"[{level_bar}] {peak:.2f} | "
                  f"{info.sample_rate}Hz {status_icon}")
        
        if info.latency:
            message += f" | {info.latency:.1f}ms"
        
        print(message, end="", flush=True)
    
    return callback