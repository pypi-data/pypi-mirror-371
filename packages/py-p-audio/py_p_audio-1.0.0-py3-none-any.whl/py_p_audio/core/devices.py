"""Device management and enumeration"""

import pyaudiowpatch as pyaudio
import sounddevice as sd
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from ..utils.exceptions import DeviceError
from .callbacks import APIType


class DeviceType(Enum):
    """Device type classification"""
    INPUT = "input"
    OUTPUT = "output"
    LOOPBACK = "loopback"


@dataclass
class DeviceInfo:
    """Unified device information"""
    # Basic info
    id: int
    name: str
    api_type: APIType
    device_type: DeviceType
    
    # Audio capabilities
    max_input_channels: int = 0
    max_output_channels: int = 0
    default_sample_rate: float = 44100.0
    supported_sample_rates: List[float] = None
    
    # PyAudio/PyAudioWPatch specific
    pyaudio_index: Optional[int] = None
    host_api: Optional[str] = None
    
    # SoundDevice specific  
    sounddevice_index: Optional[int] = None
    
    # Additional properties
    is_default_input: bool = False
    is_default_output: bool = False
    is_loopback: bool = False
    
    def __post_init__(self):
        if self.supported_sample_rates is None:
            self.supported_sample_rates = [44100.0, 48000.0]
    
    @property
    def max_channels(self) -> int:
        """Maximum channels for this device"""
        if self.device_type == DeviceType.INPUT:
            return self.max_input_channels
        elif self.device_type == DeviceType.OUTPUT:
            return self.max_output_channels
        else:  # LOOPBACK
            return max(self.max_input_channels, self.max_output_channels)
    
    def supports_sample_rate(self, sample_rate: float) -> bool:
        """Check if device supports given sample rate"""
        return sample_rate in self.supported_sample_rates
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'api_type': self.api_type.value,
            'device_type': self.device_type.value,
            'max_input_channels': self.max_input_channels,
            'max_output_channels': self.max_output_channels,
            'default_sample_rate': self.default_sample_rate,
            'supported_sample_rates': self.supported_sample_rates,
            'host_api': self.host_api,
            'is_default_input': self.is_default_input,
            'is_default_output': self.is_default_output,
            'is_loopback': self.is_loopback,
        }


class DeviceManager:
    """Manages audio device discovery and information"""
    
    def __init__(self):
        self._devices: Dict[int, DeviceInfo] = {}
        self._pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self._last_scan_time: float = 0
        self._cache_duration: float = 5.0  # Cache for 5 seconds
    
    def __enter__(self):
        self._init_pyaudio()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_pyaudio()
    
    def _init_pyaudio(self):
        """Initialize PyAudio instance"""
        if self._pyaudio_instance is None:
            try:
                self._pyaudio_instance = pyaudio.PyAudio()
            except Exception as e:
                raise DeviceError(f"Failed to initialize PyAudio: {e}")
    
    def _cleanup_pyaudio(self):
        """Cleanup PyAudio instance"""
        if self._pyaudio_instance:
            try:
                self._pyaudio_instance.terminate()
            except Exception:
                pass
            finally:
                self._pyaudio_instance = None
    
    def scan_devices(self, force_refresh: bool = False) -> List[DeviceInfo]:
        """
        Scan and enumerate all available audio devices.
        
        Args:
            force_refresh: Force device re-scan even if cache is valid
            
        Returns:
            List of discovered devices
        """
        import time
        
        current_time = time.time()
        if not force_refresh and (current_time - self._last_scan_time) < self._cache_duration:
            return list(self._devices.values())
        
        self._devices.clear()
        self._init_pyaudio()
        
        device_id_counter = 0
        
        # Scan PyAudioWPatch devices (WASAPI)
        try:
            device_id_counter = self._scan_pyaudio_devices(device_id_counter)
        except Exception as e:
            print(f"Warning: Failed to scan PyAudio devices: {e}")
        
        # Scan SoundDevice devices (ASIO and others)
        try:
            device_id_counter = self._scan_sounddevice_devices(device_id_counter)
        except Exception as e:
            print(f"Warning: Failed to scan SoundDevice devices: {e}")
        
        self._last_scan_time = current_time
        return list(self._devices.values())
    
    def _scan_pyaudio_devices(self, start_id: int) -> int:
        """Scan PyAudioWPatch devices"""
        if not self._pyaudio_instance:
            return start_id
        
        device_count = self._pyaudio_instance.get_device_count()
        current_id = start_id
        
        for pa_index in range(device_count):
            try:
                pa_info = self._pyaudio_instance.get_device_info_by_index(pa_index)
                host_api_info = self._pyaudio_instance.get_host_api_info_by_index(pa_info['hostApi'])
                
                # Skip non-WASAPI devices here (we'll get them via sounddevice)
                if host_api_info['name'] != 'Windows WASAPI':
                    continue
                
                # Create device info
                device_info = self._create_device_from_pyaudio(
                    current_id, pa_index, pa_info, host_api_info
                )
                
                if device_info:
                    self._devices[current_id] = device_info
                    current_id += 1
                    
                    # Check for loopback version
                    loopback_info = self._check_loopback_device(pa_index, pa_info, host_api_info)
                    if loopback_info:
                        self._devices[current_id] = loopback_info
                        current_id += 1
                
            except Exception as e:
                print(f"Warning: Failed to process PyAudio device {pa_index}: {e}")
                continue
        
        return current_id
    
    def _scan_sounddevice_devices(self, start_id: int) -> int:
        """Scan SoundDevice devices"""
        try:
            sd_devices = sd.query_devices()
            if not isinstance(sd_devices, list):
                sd_devices = [sd_devices]
            
            current_id = start_id
            
            for sd_index, sd_info in enumerate(sd_devices):
                try:
                    # Skip WASAPI devices (already handled by PyAudioWPatch)
                    host_api_name = sd.query_hostapis(sd_info['hostapi'])['name']
                    if 'WASAPI' in host_api_name:
                        continue
                    
                    device_info = self._create_device_from_sounddevice(
                        current_id, sd_index, sd_info, host_api_name
                    )
                    
                    if device_info:
                        self._devices[current_id] = device_info
                        current_id += 1
                
                except Exception as e:
                    print(f"Warning: Failed to process SoundDevice device {sd_index}: {e}")
                    continue
            
            return current_id
            
        except Exception as e:
            print(f"Warning: SoundDevice query failed: {e}")
            return start_id
    
    def _create_device_from_pyaudio(self, device_id: int, pa_index: int, 
                                   pa_info: dict, host_api_info: dict) -> Optional[DeviceInfo]:
        """Create DeviceInfo from PyAudio device info"""
        try:
            # Determine device type
            has_input = pa_info['maxInputChannels'] > 0
            has_output = pa_info['maxOutputChannels'] > 0
            
            if has_input and has_output:
                device_type = DeviceType.INPUT  # Prioritize input for duplex devices
            elif has_input:
                device_type = DeviceType.INPUT
            elif has_output:
                device_type = DeviceType.OUTPUT
            else:
                return None  # Skip devices with no channels
            
            # Get supported sample rates
            supported_rates = self._get_supported_sample_rates_pyaudio(pa_index, pa_info)
            
            return DeviceInfo(
                id=device_id,
                name=pa_info['name'],
                api_type=APIType.WASAPI,
                device_type=device_type,
                max_input_channels=pa_info['maxInputChannels'],
                max_output_channels=pa_info['maxOutputChannels'],
                default_sample_rate=pa_info['defaultSampleRate'],
                supported_sample_rates=supported_rates,
                pyaudio_index=pa_index,
                host_api=host_api_info['name'],
                is_default_input=pa_index == self._pyaudio_instance.get_default_input_device_info()['index'],
                is_default_output=pa_index == self._pyaudio_instance.get_default_output_device_info()['index'],
            )
            
        except Exception as e:
            print(f"Warning: Failed to create device info for PyAudio device {pa_index}: {e}")
            return None
    
    def _create_device_from_sounddevice(self, device_id: int, sd_index: int,
                                       sd_info: dict, host_api_name: str) -> Optional[DeviceInfo]:
        """Create DeviceInfo from SoundDevice device info"""
        try:
            # Determine API type
            api_type = APIType.ASIO if 'ASIO' in host_api_name else APIType.AUTO
            
            # Determine device type
            has_input = sd_info['max_input_channels'] > 0
            has_output = sd_info['max_output_channels'] > 0
            
            if has_input and has_output:
                device_type = DeviceType.INPUT  # Prioritize input for duplex devices
            elif has_input:
                device_type = DeviceType.INPUT
            elif has_output:
                device_type = DeviceType.OUTPUT
            else:
                return None
            
            # Get supported sample rates
            supported_rates = self._get_supported_sample_rates_sounddevice(sd_index, sd_info)
            
            return DeviceInfo(
                id=device_id,
                name=sd_info['name'],
                api_type=api_type,
                device_type=device_type,
                max_input_channels=sd_info['max_input_channels'],
                max_output_channels=sd_info['max_output_channels'],
                default_sample_rate=sd_info['default_samplerate'],
                supported_sample_rates=supported_rates,
                sounddevice_index=sd_index,
                host_api=host_api_name,
                is_default_input=sd_index == sd.default.device[0],
                is_default_output=sd_index == sd.default.device[1],
            )
            
        except Exception as e:
            print(f"Warning: Failed to create device info for SoundDevice device {sd_index}: {e}")
            return None
    
    def _check_loopback_device(self, pa_index: int, pa_info: dict, host_api_info: dict) -> Optional[DeviceInfo]:
        """Check if device supports loopback and create loopback DeviceInfo"""
        try:
            # Only WASAPI output devices can have loopback
            if pa_info['maxOutputChannels'] == 0:
                return None
            
            # Try to check if loopback is available for this device
            loopback_info = None
            try:
                # PyAudioWPatch specific: check if loopback device exists
                # This is a simplified check - in reality we'd need to test actual loopback capability
                if 'Speakers' in pa_info['name'] or 'output' in pa_info['name'].lower():
                    loopback_info = DeviceInfo(
                        id=-1,  # Will be set by caller
                        name=f"{pa_info['name']} (Loopback)",
                        api_type=APIType.WASAPI,
                        device_type=DeviceType.LOOPBACK,
                        max_input_channels=pa_info['maxOutputChannels'],  # Loopback captures output
                        max_output_channels=0,
                        default_sample_rate=pa_info['defaultSampleRate'],
                        supported_sample_rates=self._get_supported_sample_rates_pyaudio(pa_index, pa_info),
                        pyaudio_index=pa_index,
                        host_api=host_api_info['name'],
                        is_loopback=True,
                    )
            except Exception:
                pass
            
            return loopback_info
            
        except Exception:
            return None
    
    def _get_supported_sample_rates_pyaudio(self, pa_index: int, pa_info: dict) -> List[float]:
        """Get supported sample rates for PyAudio device"""
        common_rates = [8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 192000]
        supported = []
        
        for rate in common_rates:
            try:
                # Test if sample rate is supported
                if pa_info['maxInputChannels'] > 0:
                    params = {
                        'format': pyaudio.paInt16,
                        'channels': min(2, pa_info['maxInputChannels']),
                        'rate': int(rate),
                        'input': True,
                        'input_device_index': pa_index
                    }
                    if self._pyaudio_instance.is_format_supported(**params):
                        supported.append(rate)
                elif pa_info['maxOutputChannels'] > 0:
                    params = {
                        'format': pyaudio.paInt16,
                        'channels': min(2, pa_info['maxOutputChannels']),
                        'rate': int(rate),
                        'output': True,
                        'output_device_index': pa_index
                    }
                    if self._pyaudio_instance.is_format_supported(**params):
                        supported.append(rate)
            except Exception:
                continue
        
        # If no rates found, return common defaults
        return supported if supported else [44100.0, 48000.0]
    
    def _get_supported_sample_rates_sounddevice(self, sd_index: int, sd_info: dict) -> List[float]:
        """Get supported sample rates for SoundDevice device"""
        common_rates = [8000, 11025, 16000, 22050, 44100, 48000, 88200, 96000, 192000]
        supported = []
        
        for rate in common_rates:
            try:
                # Test if sample rate is supported
                if sd_info['max_input_channels'] > 0:
                    sd.check_input_settings(
                        device=sd_index,
                        channels=min(2, sd_info['max_input_channels']),
                        samplerate=rate
                    )
                    supported.append(rate)
                elif sd_info['max_output_channels'] > 0:
                    sd.check_output_settings(
                        device=sd_index,
                        channels=min(2, sd_info['max_output_channels']),
                        samplerate=rate
                    )
                    supported.append(rate)
            except Exception:
                continue
        
        return supported if supported else [44100.0, 48000.0]
    
    def get_device_by_id(self, device_id: int) -> Optional[DeviceInfo]:
        """Get device info by ID"""
        return self._devices.get(device_id)
    
    def get_device_by_name(self, name: str, api_type: Optional[APIType] = None) -> Optional[DeviceInfo]:
        """Get device info by name (and optionally API type)"""
        for device in self._devices.values():
            if device.name == name:
                if api_type is None or device.api_type == api_type:
                    return device
        return None
    
    def list_devices(self, device_type: Optional[DeviceType] = None, 
                    api_type: Optional[APIType] = None) -> List[DeviceInfo]:
        """List devices with optional filtering"""
        devices = list(self._devices.values())
        
        if device_type:
            devices = [d for d in devices if d.device_type == device_type]
        
        if api_type:
            devices = [d for d in devices if d.api_type == api_type]
        
        return devices
    
    def get_default_input_device(self, api_type: Optional[APIType] = None) -> Optional[DeviceInfo]:
        """Get default input device"""
        for device in self._devices.values():
            if device.is_default_input and device.device_type == DeviceType.INPUT:
                if api_type is None or device.api_type == api_type:
                    return device
        return None
    
    def get_default_output_device(self, api_type: Optional[APIType] = None) -> Optional[DeviceInfo]:
        """Get default output device"""
        for device in self._devices.values():
            if device.is_default_output and device.device_type == DeviceType.OUTPUT:
                if api_type is None or device.api_type == api_type:
                    return device
        return None


# Global device manager instance
_device_manager = None


def get_device_manager() -> DeviceManager:
    """Get global device manager instance"""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager


def list_devices(device_type: Optional[DeviceType] = None, 
                api_type: Optional[APIType] = None,
                force_refresh: bool = False) -> List[DeviceInfo]:
    """
    List available audio devices.
    
    Args:
        device_type: Filter by device type
        api_type: Filter by API type
        force_refresh: Force device re-scan
        
    Returns:
        List of available devices
    """
    manager = get_device_manager()
    with manager:
        manager.scan_devices(force_refresh=force_refresh)
        return manager.list_devices(device_type=device_type, api_type=api_type)


def get_device_info(device_id: int, force_refresh: bool = False) -> Optional[DeviceInfo]:
    """
    Get device information by ID.
    
    Args:
        device_id: Device ID
        force_refresh: Force device re-scan
        
    Returns:
        Device information or None if not found
    """
    manager = get_device_manager()
    with manager:
        manager.scan_devices(force_refresh=force_refresh)
        return manager.get_device_by_id(device_id)


def find_device(name: str, api_type: Optional[APIType] = None, 
               force_refresh: bool = False) -> Optional[DeviceInfo]:
    """
    Find device by name.
    
    Args:
        name: Device name
        api_type: API type filter
        force_refresh: Force device re-scan
        
    Returns:
        Device information or None if not found
    """
    manager = get_device_manager()
    with manager:
        manager.scan_devices(force_refresh=force_refresh)
        return manager.get_device_by_name(name, api_type)