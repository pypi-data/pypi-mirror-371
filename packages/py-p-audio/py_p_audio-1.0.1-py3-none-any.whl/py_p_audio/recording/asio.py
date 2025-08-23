"""ASIO recording implementation"""

import sounddevice as sd
import numpy as np
import soundfile as sf
import time
import threading
from pathlib import Path
from typing import Optional, Callable, List

from ..core.devices import DeviceInfo, get_device_info
from ..core.channels import ChannelMapper, ChannelSpec
from ..core.callbacks import CallbackManager, CallbackInfo, AudioMode, AudioStatus, APIType
from ..utils.exceptions import RecordingError, DeviceError


class ASIORecorder:
    """ASIO-based audio recorder using sounddevice"""
    
    def __init__(self, device_id: int, channels: ChannelSpec = None,
                 sample_rate: int = 44100, bit_depth: int = 16,
                 buffer_size: int = 1024, latency: str = 'low'):
        """
        Initialize ASIO recorder.
        
        Args:
            device_id: Device ID from device enumeration
            channels: Channel specification (None for stereo)
            sample_rate: Sample rate in Hz
            bit_depth: Bit depth (16, 24, 32)
            buffer_size: Buffer size in frames
            latency: Latency setting ('low', 'high', or specific value)
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.buffer_size = buffer_size
        self.latency = latency
        
        # Get device info
        self.device_info = get_device_info(device_id)
        if not self.device_info:
            raise DeviceError(f"Device {device_id} not found")
        
        if self.device_info.api_type != APIType.ASIO:
            raise DeviceError(f"Device {device_id} is not an ASIO device")
        
        if self.device_info.max_input_channels == 0:
            raise DeviceError(f"Device {device_id} has no input channels")
        
        # Setup channel mapping
        self.channel_mapper = ChannelMapper(channels, self.device_info.max_input_channels)
        
        # Validate sample rate
        if not self.device_info.supports_sample_rate(sample_rate):
            print(f"Warning: Sample rate {sample_rate}Hz may not be supported by device")
        
        # SoundDevice dtype mapping
        self.dtype_map = {
            16: np.int16,
            24: np.int32,  # 24-bit data is stored in 32-bit containers
            32: np.int32,
        }
        
        if bit_depth not in self.dtype_map:
            raise RecordingError(f"Unsupported bit depth: {bit_depth}")
        
        self.numpy_dtype = self.dtype_map[bit_depth]
        
        # State
        self._stream: Optional[sd.InputStream] = None
        self._recording = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Data storage
        self._recorded_data: List[np.ndarray] = []
        self._start_time: Optional[float] = None
        self._total_frames = 0
        
        # Performance monitoring
        self._last_latency_check = 0.0
        self._current_latency = 0.0
        
        # Callbacks
        self.callback_manager = CallbackManager()
        
        # File output
        self._output_file: Optional[str] = None
        self._sf_file: Optional[sf.SoundFile] = None
        
        # ASIO settings
        self._asio_settings = self._setup_asio_settings()
    
    def _setup_asio_settings(self):
        """Setup ASIO-specific settings"""
        try:
            # Configure ASIO settings through sounddevice
            settings = sd.AsioSettings(
                channel_selectors=None,  # Will be set during recording
                exclusive=False,  # Allow sharing of ASIO device
            )
            return settings
        except Exception as e:
            print(f"Warning: Could not setup ASIO settings: {e}")
            return None
    
    def set_progress_callback(self, callback: Optional[Callable[[CallbackInfo], None]]):
        """Set progress callback function"""
        self.callback_manager.set_progress_callback(callback)
    
    def set_time_callback(self, callback: Optional[Callable[[float, int, str], None]]):
        """Set simple time callback function"""
        self.callback_manager.set_time_callback(callback)
    
    def set_error_callback(self, callback: Optional[Callable[[str, Optional[str]], None]]):
        """Set error callback function"""
        self.callback_manager.set_error_callback(callback)
    
    def start_recording(self, output_file: Optional[str] = None):
        """
        Start ASIO recording.
        
        Args:
            output_file: Optional output file path. If None, data is stored in memory.
        """
        if self._recording:
            raise RecordingError("Recording already in progress")
        
        try:
            self._output_file = output_file
            self._setup_output_file()
            self._setup_audio_stream()
            
            # Start recording
            self._stop_event.clear()
            self._recording = True
            self._paused = False
            self._start_time = time.time()
            self._total_frames = 0
            self._recorded_data.clear()
            
            self.callback_manager.start_timing()
            self._stream.start()
            
        except Exception as e:
            self._cleanup()
            raise RecordingError(f"Failed to start ASIO recording: {e}")
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop recording and return recorded data.
        
        Returns:
            Recorded audio data as numpy array, or None if saved to file
        """
        if not self._recording:
            return None
        
        # Stop stream
        if self._stream:
            self._stream.stop()
        
        # Wait a moment for final callbacks
        time.sleep(0.1)
        
        # Get recorded data before cleanup
        recorded_data = None
        if not self._output_file and self._recorded_data:
            recorded_data = np.concatenate(self._recorded_data, axis=0)
        
        self._cleanup()
        return recorded_data
    
    def pause_recording(self):
        """Pause recording"""
        if self._recording and not self._paused:
            self._paused = True
    
    def resume_recording(self):
        """Resume recording"""
        if self._recording and self._paused:
            self._paused = False
    
    def is_recording(self) -> bool:
        """Check if recording is active"""
        return self._recording and not self._paused
    
    def is_paused(self) -> bool:
        """Check if recording is paused"""
        return self._recording and self._paused
    
    def get_current_time(self) -> float:
        """Get current recording time in seconds"""
        if not self._start_time:
            return 0.0
        return time.time() - self._start_time
    
    def get_recorded_frames(self) -> int:
        """Get number of recorded frames"""
        return self._total_frames
    
    def get_current_latency(self) -> float:
        """Get current ASIO latency in milliseconds"""
        return self._current_latency
    
    def _setup_output_file(self):
        """Setup output file if specified"""
        if self._output_file:
            try:
                # Ensure directory exists
                Path(self._output_file).parent.mkdir(parents=True, exist_ok=True)
                
                # Open soundfile for writing
                self._sf_file = sf.SoundFile(
                    self._output_file,
                    mode='w',
                    samplerate=self.sample_rate,
                    channels=self.channel_mapper.count,
                    subtype='PCM_16' if self.bit_depth == 16 else f'PCM_{self.bit_depth}'
                )
            except Exception as e:
                raise RecordingError(f"Failed to create output file: {e}")
    
    def _setup_audio_stream(self):
        """Setup SoundDevice ASIO input stream"""
        try:
            # Setup channel selectors for ASIO
            if self._asio_settings:
                # Configure specific input channels
                input_channels = [i + 1 for i in self.channel_mapper.channel_indices]  # ASIO uses 1-based
                self._asio_settings.channel_selectors = input_channels
            
            # Create input stream with callback
            self._stream = sd.InputStream(
                device=self.device_info.sounddevice_index,
                channels=self.channel_mapper.count,
                samplerate=self.sample_rate,
                dtype=self.numpy_dtype,
                blocksize=self.buffer_size,
                latency=self.latency,
                callback=self._audio_callback,
                extra_settings=self._asio_settings,
            )
            
        except Exception as e:
            raise RecordingError(f"Failed to setup ASIO audio stream: {e}")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """SoundDevice audio callback"""
        if status:
            self.callback_manager.trigger_error_callback(
                f"ASIO callback status: {status}", self.device_info.name
            )
        
        if self._paused or not self._recording:
            return
        
        try:
            # Update frame count
            self._total_frames += frames
            
            # Store or write data
            if self._sf_file:
                # Convert to float for soundfile
                if self.bit_depth == 16:
                    float_data = indata.astype(np.float32) / 32768.0
                elif self.bit_depth == 24:
                    float_data = indata.astype(np.float32) / 8388608.0  # 24-bit max value
                else:  # 32-bit
                    float_data = indata.astype(np.float32) / 2147483648.0
                self._sf_file.write(float_data)
            else:
                self._recorded_data.append(indata.copy())
            
            # Calculate levels for callback
            peak_levels = []
            for ch in range(indata.shape[1]):
                channel_data = indata[:, ch]
                if len(channel_data) > 0:
                    if self.bit_depth == 16:
                        peak = np.max(np.abs(channel_data)) / 32768.0
                    elif self.bit_depth == 24:
                        peak = np.max(np.abs(channel_data)) / 8388608.0
                    else:  # 32-bit
                        peak = np.max(np.abs(channel_data)) / 2147483648.0
                    peak_levels.append(float(peak))
                else:
                    peak_levels.append(0.0)
            
            # Update latency measurement (ASIO specific)
            current_time_val = time.time()
            if current_time_val - self._last_latency_check > 1.0:  # Check every second
                try:
                    # Get actual ASIO latency from time_info if available
                    if hasattr(time_info, 'input_adc_time') and hasattr(time_info, 'current_time'):
                        self._current_latency = (time_info.current_time - time_info.input_adc_time) * 1000.0
                    else:
                        # Estimate based on buffer size
                        self._current_latency = (self.buffer_size / self.sample_rate) * 1000.0
                except Exception:
                    self._current_latency = 0.0
                self._last_latency_check = current_time_val
            
            # Trigger callbacks
            recording_time = self.get_current_time()
            
            # Progress callback
            info = CallbackInfo(
                current_time=recording_time,
                device_name=self.device_info.name,
                api_type=APIType.ASIO,
                mode=AudioMode.RECORDING,
                status=AudioStatus.PAUSED if self._paused else AudioStatus.ACTIVE,
                sample_rate=self.sample_rate,
                channels=self.channel_mapper.count,
                bit_depth=self.bit_depth,
                buffer_size=self.buffer_size,
                peak_levels=peak_levels,
                latency=self._current_latency,
                elapsed_samples=self._total_frames,
                file_size=Path(self._output_file).stat().st_size if self._output_file and Path(self._output_file).exists() else None,
            )
            
            self.callback_manager.trigger_progress_callback(info)
            
            # Simple time callback
            self.callback_manager.trigger_time_callback(
                recording_time, self._total_frames,
                "paused" if self._paused else "recording"
            )
            
        except Exception as e:
            self.callback_manager.trigger_error_callback(
                f"ASIO recording callback error: {e}", self.device_info.name
            )
    
    def _cleanup(self):
        """Cleanup resources"""
        self._recording = False
        
        # Close soundfile
        if self._sf_file:
            try:
                self._sf_file.close()
            except Exception:
                pass
            self._sf_file = None
        
        # Close stream
        if self._stream:
            try:
                self._stream.close()
            except Exception:
                pass
            self._stream = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._recording:
            self.stop_recording()
        self._cleanup()


def record_asio_audio(device_id: int, duration: float, output_file: str,
                     channels: ChannelSpec = None, sample_rate: int = 44100,
                     bit_depth: int = 16, buffer_size: int = 1024,
                     latency: str = 'low',
                     progress_callback: Optional[Callable[[CallbackInfo], None]] = None) -> bool:
    """
    Convenience function to record ASIO audio for a specified duration.
    
    Args:
        device_id: ASIO device ID for recording
        duration: Recording duration in seconds
        output_file: Output file path
        channels: Channel specification
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth
        buffer_size: Buffer size in frames
        latency: Latency setting
        progress_callback: Optional progress callback
        
    Returns:
        True if recording was successful
    """
    try:
        with ASIORecorder(device_id, channels, sample_rate, bit_depth, 
                         buffer_size, latency) as recorder:
            if progress_callback:
                recorder.set_progress_callback(progress_callback)
            
            recorder.start_recording(output_file)
            
            # Wait for duration
            time.sleep(duration)
            
            recorder.stop_recording()
            return True
            
    except Exception as e:
        print(f"ASIO recording failed: {e}")
        return False


def record_asio_with_monitoring(device_id: int, duration: float, output_file: str,
                               channels: ChannelSpec = None, sample_rate: int = 44100,
                               bit_depth: int = 16, buffer_size: int = 256,
                               show_levels: bool = True) -> bool:
    """
    Record ASIO audio with real-time level monitoring.
    
    Args:
        device_id: ASIO device ID for recording
        duration: Recording duration in seconds
        output_file: Output file path
        channels: Channel specification
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth
        buffer_size: Buffer size in frames (smaller for lower latency)
        show_levels: Show real-time level meters
        
    Returns:
        True if recording was successful
    """
    from ..core.callbacks import create_detailed_progress_callback
    
    try:
        progress_callback = create_detailed_progress_callback() if show_levels else None
        
        with ASIORecorder(device_id, channels, sample_rate, bit_depth, 
                         buffer_size, 'low') as recorder:
            if progress_callback:
                recorder.set_progress_callback(progress_callback)
            
            print(f"🎵 Starting ASIO recording ({duration}s)...")
            recorder.start_recording(output_file)
            
            # Wait for duration
            time.sleep(duration)
            
            recorder.stop_recording()
            print(f"\n✅ Recording completed: {output_file}")
            print(f"📊 Latency: {recorder.get_current_latency():.1f}ms")
            return True
            
    except Exception as e:
        print(f"\n❌ ASIO recording failed: {e}")
        return False