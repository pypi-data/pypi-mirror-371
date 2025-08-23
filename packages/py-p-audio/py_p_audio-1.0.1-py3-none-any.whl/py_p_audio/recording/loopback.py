"""WASAPI loopback recording implementation"""

import pyaudiowpatch as pyaudio
import numpy as np
import soundfile as sf
import time
import threading
from pathlib import Path
from typing import Optional, Callable, List

from ..core.devices import DeviceInfo, get_device_info, DeviceType
from ..core.channels import ChannelMapper, ChannelSpec
from ..core.callbacks import CallbackManager, CallbackInfo, AudioMode, AudioStatus, APIType
from ..utils.exceptions import RecordingError, DeviceError


class WASAPILoopbackRecorder:
    """WASAPI loopback recorder for capturing system audio output"""
    
    def __init__(self, device_id: int, channels: ChannelSpec = None,
                 sample_rate: int = 44100, bit_depth: int = 16,
                 buffer_size: int = 1024, silence_threshold: float = 0.001):
        """
        Initialize WASAPI loopback recorder.
        
        Args:
            device_id: Device ID for loopback recording (must be loopback device)
            channels: Channel specification (None for stereo)
            sample_rate: Sample rate in Hz
            bit_depth: Bit depth (16, 24, 32)
            buffer_size: Buffer size in frames
            silence_threshold: Threshold for silence detection (0.0-1.0)
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.buffer_size = buffer_size
        self.silence_threshold = silence_threshold
        
        # Get device info
        self.device_info = get_device_info(device_id)
        if not self.device_info:
            raise DeviceError(f"Device {device_id} not found")
        
        if self.device_info.api_type != APIType.WASAPI:
            raise DeviceError(f"Device {device_id} is not a WASAPI device")
        
        if not self.device_info.is_loopback:
            raise DeviceError(f"Device {device_id} is not a loopback device")
        
        # For loopback, max_input_channels represents the output channels we can capture
        max_channels = self.device_info.max_input_channels
        if max_channels == 0:
            raise DeviceError(f"Loopback device {device_id} has no capturable channels")
        
        # Setup channel mapping
        self.channel_mapper = ChannelMapper(channels, max_channels)
        
        # Validate sample rate
        if not self.device_info.supports_sample_rate(sample_rate):
            print(f"Warning: Sample rate {sample_rate}Hz may not be supported by device")
        
        # Audio format mapping
        self.format_map = {
            16: pyaudio.paInt16,
            24: pyaudio.paInt24,
            32: pyaudio.paInt32,
        }
        
        if bit_depth not in self.format_map:
            raise RecordingError(f"Unsupported bit depth: {bit_depth}")
        
        self.pyaudio_format = self.format_map[bit_depth]
        
        # State
        self._pyaudio: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._recording = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Data storage
        self._recorded_data: List[np.ndarray] = []
        self._start_time: Optional[float] = None
        self._total_frames = 0
        
        # Silence detection
        self._silent_frames = 0
        self._silent_duration = 0.0
        self._last_audio_time = 0.0
        
        # Callbacks
        self.callback_manager = CallbackManager()
        
        # File output
        self._output_file: Optional[str] = None
        self._sf_file: Optional[sf.SoundFile] = None
    
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
        Start loopback recording.
        
        Args:
            output_file: Optional output file path. If None, data is stored in memory.
        """
        if self._recording:
            raise RecordingError("Recording already in progress")
        
        try:
            self._output_file = output_file
            self._setup_audio()
            self._setup_output_file()
            
            # Start recording thread
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._recording_thread, daemon=True)
            self._recording = True
            self._paused = False
            self._start_time = time.time()
            self._total_frames = 0
            self._silent_frames = 0
            self._silent_duration = 0.0
            self._last_audio_time = time.time()
            self._recorded_data.clear()
            
            self.callback_manager.start_timing()
            self._thread.start()
            
        except Exception as e:
            self._cleanup()
            raise RecordingError(f"Failed to start loopback recording: {e}")
    
    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop recording and return recorded data.
        
        Returns:
            Recorded audio data as numpy array, or None if saved to file
        """
        if not self._recording:
            return None
        
        # Signal stop and wait for thread
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
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
    
    def get_silence_duration(self) -> float:
        """Get duration of current silence in seconds"""
        return self._silent_duration
    
    def is_silent(self) -> bool:
        """Check if currently detecting silence"""
        return self._silent_duration > 0.1  # Consider silent if > 100ms
    
    def _setup_audio(self):
        """Setup PyAudio and loopback stream"""
        try:
            self._pyaudio = pyaudio.PyAudio()
            
            # For loopback recording, we need to use the WASAPI loopback feature
            # PyAudioWPatch supports this through special device handling
            
            # Get the actual PyAudio device index for loopback
            pa_device_index = self.device_info.pyaudio_index
            
            # Create loopback stream
            self._stream = self._pyaudio.open(
                format=self.pyaudio_format,
                channels=self.device_info.max_input_channels,  # Capture all output channels
                rate=self.sample_rate,
                input=True,
                input_device_index=pa_device_index,
                frames_per_buffer=self.buffer_size,
                # Enable loopback mode (PyAudioWPatch specific)
                as_loopback=True,
            )
            
        except Exception as e:
            raise RecordingError(f"Failed to setup loopback audio stream: {e}")
    
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
    
    def _recording_thread(self):
        """Main loopback recording thread"""
        try:
            while not self._stop_event.is_set():
                if self._paused:
                    time.sleep(0.01)
                    continue
                
                # Read audio data
                try:
                    data = self._stream.read(self.buffer_size, exception_on_overflow=False)
                    if not data:
                        continue
                    
                    # Convert to numpy array
                    if self.bit_depth == 16:
                        audio_data = np.frombuffer(data, dtype=np.int16)
                    elif self.bit_depth == 24:
                        audio_data = np.frombuffer(data, dtype=np.int32)  # 24-bit packed in 32-bit
                    else:  # 32-bit
                        audio_data = np.frombuffer(data, dtype=np.int32)
                    
                    # Reshape to channels
                    if len(audio_data) % self.device_info.max_input_channels == 0:
                        audio_data = audio_data.reshape(-1, self.device_info.max_input_channels)
                        
                        # Extract specified channels
                        selected_data = audio_data[:, self.channel_mapper.channel_indices]
                        
                        # Update frame count
                        self._total_frames += selected_data.shape[0]
                        
                        # Calculate levels for callback and silence detection
                        peak_levels = []
                        max_peak = 0.0
                        
                        for ch in range(selected_data.shape[1]):
                            channel_data = selected_data[:, ch]
                            if len(channel_data) > 0:
                                if self.bit_depth == 16:
                                    peak = np.max(np.abs(channel_data)) / 32768.0
                                else:
                                    peak = np.max(np.abs(channel_data)) / 2147483648.0
                                peak_levels.append(float(peak))
                                max_peak = max(max_peak, peak)
                            else:
                                peak_levels.append(0.0)
                        
                        # Silence detection
                        current_time = time.time()
                        is_silent = max_peak < self.silence_threshold
                        
                        if is_silent:
                            self._silent_frames += selected_data.shape[0]
                            self._silent_duration = self._silent_frames / self.sample_rate
                        else:
                            self._silent_frames = 0
                            self._silent_duration = 0.0
                            self._last_audio_time = current_time
                        
                        # Store or write data (even if silent, for complete recording)
                        if self._sf_file:
                            # Convert to float for soundfile
                            if self.bit_depth == 16:
                                float_data = selected_data.astype(np.float32) / 32768.0
                            else:
                                float_data = selected_data.astype(np.float32) / 2147483648.0
                            self._sf_file.write(float_data)
                        else:
                            self._recorded_data.append(selected_data)
                        
                        # Trigger callbacks
                        recording_time = self.get_current_time()
                        
                        # Progress callback
                        info = CallbackInfo(
                            current_time=recording_time,
                            device_name=self.device_info.name,
                            api_type=APIType.WASAPI,
                            mode=AudioMode.RECORDING,
                            status=AudioStatus.PAUSED if self._paused else AudioStatus.ACTIVE,
                            sample_rate=self.sample_rate,
                            channels=self.channel_mapper.count,
                            bit_depth=self.bit_depth,
                            buffer_size=self.buffer_size,
                            peak_levels=peak_levels,
                            elapsed_samples=self._total_frames,
                            is_silent=is_silent,
                            file_size=Path(self._output_file).stat().st_size if self._output_file and Path(self._output_file).exists() else None,
                        )
                        
                        self.callback_manager.trigger_progress_callback(info)
                        
                        # Simple time callback
                        status = "silent" if is_silent else ("paused" if self._paused else "recording")
                        self.callback_manager.trigger_time_callback(
                            recording_time, self._total_frames, status
                        )
                
                except Exception as e:
                    self.callback_manager.trigger_error_callback(
                        f"Loopback recording error: {e}", self.device_info.name
                    )
                    break
        
        except Exception as e:
            self.callback_manager.trigger_error_callback(
                f"Loopback recording thread error: {e}", self.device_info.name
            )
        finally:
            self._recording = False
    
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
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        
        # Terminate PyAudio
        if self._pyaudio:
            try:
                self._pyaudio.terminate()
            except Exception:
                pass
            self._pyaudio = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._recording:
            self.stop_recording()
        self._cleanup()


def record_system_audio(device_id: int, duration: float, output_file: str,
                       channels: ChannelSpec = None, sample_rate: int = 44100,
                       bit_depth: int = 16, silence_threshold: float = 0.001,
                       progress_callback: Optional[Callable[[CallbackInfo], None]] = None) -> bool:
    """
    Convenience function to record system audio for a specified duration.
    
    Args:
        device_id: Loopback device ID for recording
        duration: Recording duration in seconds
        output_file: Output file path
        channels: Channel specification
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth
        silence_threshold: Silence detection threshold
        progress_callback: Optional progress callback
        
    Returns:
        True if recording was successful
    """
    try:
        with WASAPILoopbackRecorder(device_id, channels, sample_rate, bit_depth, 
                                   silence_threshold=silence_threshold) as recorder:
            if progress_callback:
                recorder.set_progress_callback(progress_callback)
            
            recorder.start_recording(output_file)
            
            # Wait for duration
            time.sleep(duration)
            
            recorder.stop_recording()
            return True
            
    except Exception as e:
        print(f"Loopback recording failed: {e}")
        return False


def record_until_silence(device_id: int, output_file: str, max_duration: float = 600.0,
                        silence_duration: float = 3.0, channels: ChannelSpec = None,
                        sample_rate: int = 44100, bit_depth: int = 16,
                        silence_threshold: float = 0.001,
                        progress_callback: Optional[Callable[[CallbackInfo], None]] = None) -> bool:
    """
    Record system audio until silence is detected for a specified duration.
    
    Args:
        device_id: Loopback device ID for recording
        output_file: Output file path
        max_duration: Maximum recording duration in seconds
        silence_duration: Duration of silence required to stop recording
        channels: Channel specification
        sample_rate: Sample rate in Hz
        bit_depth: Bit depth
        silence_threshold: Silence detection threshold
        progress_callback: Optional progress callback
        
    Returns:
        True if recording was successful
    """
    try:
        with WASAPILoopbackRecorder(device_id, channels, sample_rate, bit_depth,
                                   silence_threshold=silence_threshold) as recorder:
            if progress_callback:
                recorder.set_progress_callback(progress_callback)
            
            recorder.start_recording(output_file)
            
            # Wait for silence or max duration
            start_time = time.time()
            while time.time() - start_time < max_duration:
                if recorder.get_silence_duration() >= silence_duration:
                    break
                time.sleep(0.1)
            
            recorder.stop_recording()
            return True
            
    except Exception as e:
        print(f"Loopback recording failed: {e}")
        return False