"""High-level API for py-p-audio"""

from typing import Optional, Callable, Union, List
from pathlib import Path
import time
import numpy as np

from .core.devices import list_devices, get_device_info, DeviceInfo, DeviceType
from .core.channels import ChannelSpec
from .core.callbacks import CallbackInfo, APIType, create_simple_progress_callback, create_detailed_progress_callback
from .recording.wasapi import WASAPIRecorder
from .recording.asio import ASIORecorder
from .recording.loopback import WASAPILoopbackRecorder
from .playback.wasapi import WASAPIPlayer
from .playback.asio import ASIOPlayer
from .utils.exceptions import PyPAudioError, DeviceError, RecordingError, PlaybackError


class Recorder:
    """Unified recorder class supporting WASAPI and ASIO"""
    
    def __init__(self, device_id: Optional[int] = None, device_name: Optional[str] = None,
                 api_type: Optional[APIType] = None, channels: ChannelSpec = None,
                 sample_rate: int = 44100, bit_depth: int = 16, buffer_size: int = 1024):
        """
        Initialize unified recorder.
        
        Args:
            device_id: Device ID (if None, will use device_name or default)
            device_name: Device name (used if device_id is None)
            api_type: Preferred API type (WASAPI or ASIO)
            channels: Channel specification
            sample_rate: Sample rate in Hz
            bit_depth: Bit depth (16, 24, 32)
            buffer_size: Buffer size in frames
        """
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.buffer_size = buffer_size
        
        # Find device
        self.device_info = self._find_device(device_id, device_name, api_type, DeviceType.INPUT)
        
        # Create appropriate recorder
        self._recorder = self._create_recorder()
    
    def _find_device(self, device_id: Optional[int], device_name: Optional[str],
                    api_type: Optional[APIType], device_type: DeviceType) -> DeviceInfo:
        """Find suitable device"""
        if device_id is not None:
            device_info = get_device_info(device_id)
            if not device_info:
                raise DeviceError(f"Device {device_id} not found")
            return device_info
        
        # Search by name and/or API type
        devices = list_devices(device_type=device_type, api_type=api_type)
        
        if device_name:
            for device in devices:
                if device_name.lower() in device.name.lower():
                    return device
            raise DeviceError(f"Device with name '{device_name}' not found")
        
        # Use default device
        if api_type:
            for device in devices:
                if device.api_type == api_type and (device.is_default_input or device.is_default_output):
                    return device
        
        # Find any suitable device
        if devices:
            return devices[0]
        
        raise DeviceError("No suitable audio device found")
    
    def _create_recorder(self):
        """Create appropriate recorder based on device API"""
        if self.device_info.api_type == APIType.WASAPI:
            return WASAPIRecorder(
                device_id=self.device_info.id,
                channels=self.channels,
                sample_rate=self.sample_rate,
                bit_depth=self.bit_depth,
                buffer_size=self.buffer_size
            )
        elif self.device_info.api_type == APIType.ASIO:
            return ASIORecorder(
                device_id=self.device_info.id,
                channels=self.channels,
                sample_rate=self.sample_rate,
                bit_depth=self.bit_depth,
                buffer_size=self.buffer_size
            )
        else:
            raise DeviceError(f"Unsupported API type: {self.device_info.api_type}")
    
    def set_progress_callback(self, callback: Optional[Callable[[CallbackInfo], None]]):
        """Set progress callback"""
        self._recorder.set_progress_callback(callback)
    
    def set_time_callback(self, callback: Optional[Callable[[float, int, str], None]]):
        """Set time callback"""
        self._recorder.set_time_callback(callback)
    
    def start_recording(self, output_file: Optional[str] = None):
        """Start recording"""
        self._recorder.start_recording(output_file)
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return data"""
        return self._recorder.stop_recording()
    
    def pause(self):
        """Pause recording"""
        self._recorder.pause_recording()
    
    def resume(self):
        """Resume recording"""
        self._recorder.resume_recording()
    
    def is_recording(self) -> bool:
        """Check if recording"""
        return self._recorder.is_recording()
    
    def get_current_time(self) -> float:
        """Get current recording time"""
        return self._recorder.get_current_time()
    
    @property
    def device_name(self) -> str:
        """Get device name"""
        return self.device_info.name
    
    @property
    def api_type(self) -> APIType:
        """Get API type"""
        return self.device_info.api_type
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._recorder, '__exit__'):
            self._recorder.__exit__(exc_type, exc_val, exc_tb)


class LoopbackRecorder:
    """Loopback recorder for system audio capture"""
    
    def __init__(self, device_id: Optional[int] = None, device_name: Optional[str] = None,
                 channels: ChannelSpec = None, sample_rate: int = 44100,
                 bit_depth: int = 16, buffer_size: int = 1024,
                 silence_threshold: float = 0.001):
        """
        Initialize loopback recorder.
        
        Args:
            device_id: Loopback device ID (if None, will use device_name or find one)
            device_name: Device name
            channels: Channel specification
            sample_rate: Sample rate in Hz
            bit_depth: Bit depth
            buffer_size: Buffer size in frames
            silence_threshold: Silence detection threshold
        """
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.buffer_size = buffer_size
        self.silence_threshold = silence_threshold
        
        # Find loopback device
        self.device_info = self._find_loopback_device(device_id, device_name)
        
        # Create loopback recorder
        self._recorder = WASAPILoopbackRecorder(
            device_id=self.device_info.id,
            channels=channels,
            sample_rate=sample_rate,
            bit_depth=bit_depth,
            buffer_size=buffer_size,
            silence_threshold=silence_threshold
        )
    
    def _find_loopback_device(self, device_id: Optional[int], device_name: Optional[str]) -> DeviceInfo:
        """Find loopback device"""
        if device_id is not None:
            device_info = get_device_info(device_id)
            if not device_info:
                raise DeviceError(f"Device {device_id} not found")
            if not device_info.is_loopback:
                raise DeviceError(f"Device {device_id} is not a loopback device")
            return device_info
        
        # Search for loopback devices
        devices = list_devices()
        loopback_devices = [d for d in devices if d.is_loopback]
        
        if device_name:
            for device in loopback_devices:
                if device_name.lower() in device.name.lower():
                    return device
            raise DeviceError(f"Loopback device with name '{device_name}' not found")
        
        # Use first available loopback device
        if loopback_devices:
            return loopback_devices[0]
        
        raise DeviceError("No loopback devices found")
    
    def set_progress_callback(self, callback: Optional[Callable[[CallbackInfo], None]]):
        """Set progress callback"""
        self._recorder.set_progress_callback(callback)
    
    def start_recording(self, output_file: Optional[str] = None):
        """Start loopback recording"""
        self._recorder.start_recording(output_file)
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """Stop recording and return data"""
        return self._recorder.stop_recording()
    
    def is_recording(self) -> bool:
        """Check if recording"""
        return self._recorder.is_recording()
    
    def get_silence_duration(self) -> float:
        """Get current silence duration"""
        return self._recorder.get_silence_duration()
    
    @property
    def device_name(self) -> str:
        """Get device name"""
        return self.device_info.name
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._recorder, '__exit__'):
            self._recorder.__exit__(exc_type, exc_val, exc_tb)


class Player:
    """Unified player class supporting WASAPI and ASIO"""
    
    def __init__(self, device_id: Optional[int] = None, device_name: Optional[str] = None,
                 api_type: Optional[APIType] = None, channels: ChannelSpec = None,
                 sample_rate: Optional[int] = None, bit_depth: int = 16,
                 buffer_size: int = 1024):
        """
        Initialize unified player.
        
        Args:
            device_id: Device ID (if None, will use device_name or default)
            device_name: Device name
            api_type: Preferred API type
            channels: Channel specification
            sample_rate: Sample rate (None for auto-detect)
            bit_depth: Bit depth
            buffer_size: Buffer size in frames
        """
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.buffer_size = buffer_size
        
        # Find device
        self.device_info = self._find_device(device_id, device_name, api_type, DeviceType.OUTPUT)
        
        # Create appropriate player
        self._player = self._create_player()
    
    def _find_device(self, device_id: Optional[int], device_name: Optional[str],
                    api_type: Optional[APIType], device_type: DeviceType) -> DeviceInfo:
        """Find suitable device"""
        if device_id is not None:
            device_info = get_device_info(device_id)
            if not device_info:
                raise DeviceError(f"Device {device_id} not found")
            return device_info
        
        # Search by name and/or API type
        devices = list_devices(device_type=device_type, api_type=api_type)
        
        if device_name:
            for device in devices:
                if device_name.lower() in device.name.lower():
                    return device
            raise DeviceError(f"Device with name '{device_name}' not found")
        
        # Use default device
        if api_type:
            for device in devices:
                if device.api_type == api_type and (device.is_default_input or device.is_default_output):
                    return device
        
        # Find any suitable device
        if devices:
            return devices[0]
        
        raise DeviceError("No suitable audio device found")
    
    def _create_player(self):
        """Create appropriate player based on device API"""
        if self.device_info.api_type == APIType.WASAPI:
            return WASAPIPlayer(
                device_id=self.device_info.id,
                channels=self.channels,
                sample_rate=self.sample_rate,
                bit_depth=self.bit_depth,
                buffer_size=self.buffer_size
            )
        elif self.device_info.api_type == APIType.ASIO:
            return ASIOPlayer(
                device_id=self.device_info.id,
                channels=self.channels,
                sample_rate=self.sample_rate,
                bit_depth=self.bit_depth,
                buffer_size=self.buffer_size
            )
        else:
            raise DeviceError(f"Unsupported API type: {self.device_info.api_type}")
    
    def set_progress_callback(self, callback: Optional[Callable[[CallbackInfo], None]]):
        """Set progress callback"""
        self._player.set_progress_callback(callback)
    
    def load_file(self, file_path: str) -> dict:
        """Load audio file"""
        return self._player.load_file(file_path)
    
    def load_data(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        """Load audio data"""
        return self._player.load_data(audio_data, sample_rate)
    
    def play(self, start_position: float = 0.0):
        """Start playback"""
        self._player.play(start_position)
    
    def stop(self):
        """Stop playback"""
        self._player.stop()
    
    def pause(self):
        """Pause playback"""
        self._player.pause()
    
    def resume(self):
        """Resume playback"""
        self._player.resume()
    
    def seek(self, position: float):
        """Seek to position"""
        self._player.seek(position)
    
    def is_playing(self) -> bool:
        """Check if playing"""
        return self._player.is_playing()
    
    def get_position(self) -> float:
        """Get current position"""
        return self._player.get_position()
    
    def get_duration(self) -> float:
        """Get total duration"""
        return self._player.get_duration()
    
    @property
    def device_name(self) -> str:
        """Get device name"""
        return self.device_info.name
    
    @property
    def api_type(self) -> APIType:
        """Get API type"""
        return self.device_info.api_type
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._player, '__exit__'):
            self._player.__exit__(exc_type, exc_val, exc_tb)


# Convenience functions

def record(device_id: Optional[int] = None, duration: float = 10.0, 
          output_file: Optional[str] = None, channels: ChannelSpec = None,
          sample_rate: int = 44100, api_type: Optional[APIType] = None,
          show_progress: bool = True) -> Optional[np.ndarray]:
    """
    Simple recording function.
    
    Args:
        device_id: Device ID (None for default)
        duration: Recording duration in seconds
        output_file: Output file path (None for in-memory)
        channels: Channel specification
        sample_rate: Sample rate
        api_type: Preferred API type
        show_progress: Show progress display
        
    Returns:
        Audio data if output_file is None
    """
    try:
        with Recorder(device_id=device_id, api_type=api_type, channels=channels,
                     sample_rate=sample_rate) as recorder:
            
            if show_progress:
                recorder.set_progress_callback(create_simple_progress_callback())
            
            print(f"🎤 Recording for {duration}s using {recorder.device_name} ({recorder.api_type.value})")
            recorder.start_recording(output_file)
            
            time.sleep(duration)
            
            data = recorder.stop_recording()
            
            if output_file:
                print(f"\n✅ Recording saved: {output_file}")
            else:
                print(f"\n✅ Recording completed: {data.shape[0]} frames")
            
            return data
            
    except Exception as e:
        print(f"\n❌ Recording failed: {e}")
        return None


def record_system_audio(duration: float = 10.0, output_file: Optional[str] = None,
                       channels: ChannelSpec = None, sample_rate: int = 44100,
                       show_progress: bool = True) -> Optional[np.ndarray]:
    """
    Record system audio (loopback).
    
    Args:
        duration: Recording duration in seconds
        output_file: Output file path (None for in-memory)
        channels: Channel specification
        sample_rate: Sample rate
        show_progress: Show progress display
        
    Returns:
        Audio data if output_file is None
    """
    try:
        with LoopbackRecorder(channels=channels, sample_rate=sample_rate) as recorder:
            
            if show_progress:
                recorder.set_progress_callback(create_simple_progress_callback())
            
            print(f"🔊 Recording system audio for {duration}s using {recorder.device_name}")
            recorder.start_recording(output_file)
            
            time.sleep(duration)
            
            data = recorder.stop_recording()
            
            if output_file:
                print(f"\n✅ System audio saved: {output_file}")
            else:
                print(f"\n✅ System audio recorded: {data.shape[0]} frames")
            
            return data
            
    except Exception as e:
        print(f"\n❌ System audio recording failed: {e}")
        return None


def play(file_path: str, device_id: Optional[int] = None,
         api_type: Optional[APIType] = None, start_position: float = 0.0,
         show_progress: bool = True) -> bool:
    """
    Simple playback function.
    
    Args:
        file_path: Audio file path
        device_id: Device ID (None for default)
        api_type: Preferred API type
        start_position: Start position in seconds
        show_progress: Show progress display
        
    Returns:
        True if successful
    """
    try:
        with Player(device_id=device_id, api_type=api_type) as player:
            
            if show_progress:
                player.set_progress_callback(create_simple_progress_callback(
                    "▶️ {mode} {time:.1f}s / {total_time:.1f}s [{device}]"
                ))
            
            file_info = player.load_file(file_path)
            print(f"▶️ Playing: {Path(file_path).name}")
            print(f"📊 {file_info['duration']:.1f}s | {file_info['channels']}ch | {file_info['sample_rate']}Hz")
            print(f"🔊 Device: {player.device_name} ({player.api_type.value})")
            
            player.play(start_position)
            
            # Wait for completion
            time.sleep(file_info['duration'] - start_position + 0.5)
            
            print("\n✅ Playback completed")
            return True
            
    except Exception as e:
        print(f"\n❌ Playback failed: {e}")
        return False


def list_audio_devices(device_type: Optional[DeviceType] = None,
                      api_type: Optional[APIType] = None) -> List[DeviceInfo]:
    """
    List available audio devices.
    
    Args:
        device_type: Filter by device type
        api_type: Filter by API type
        
    Returns:
        List of device information
    """
    devices = list_devices(device_type=device_type, api_type=api_type)
    
    print(f"\n[*] Available Audio Devices ({len(devices)} found):")
    print("=" * 60)
    
    for device in devices:
        api_icon = "[ASIO]" if device.api_type == APIType.ASIO else "[WASAPI]"
        type_icon = {"input": "[IN]", "output": "[OUT]", "loopback": "[LOOP]"}[device.device_type.value]
        default_mark = " [DEFAULT]" if device.is_default_input or device.is_default_output else ""
        loopback_mark = " [LOOPBACK]" if device.is_loopback else ""
        
        print(f"{api_icon}{type_icon} [{device.id:2d}] {device.name}{default_mark}{loopback_mark}")
        print(f"    API: {device.api_type.value} | Channels: {device.max_channels} | Rate: {device.default_sample_rate}Hz")
        print()
    
    return devices