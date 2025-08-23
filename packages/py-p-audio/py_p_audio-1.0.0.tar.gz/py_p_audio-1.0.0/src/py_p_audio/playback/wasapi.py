"""WASAPI playback implementation"""

import pyaudiowpatch as pyaudio
import numpy as np
import soundfile as sf
import time
import threading
from pathlib import Path
from typing import Optional, Callable, Union

from ..core.devices import DeviceInfo, get_device_info
from ..core.channels import ChannelMapper, ChannelSpec
from ..core.callbacks import CallbackManager, CallbackInfo, AudioMode, AudioStatus, APIType
from ..utils.exceptions import PlaybackError, DeviceError, FileError


class WASAPIPlayer:
    """WASAPI-based audio player using PyAudioWPatch"""
    
    def __init__(self, device_id: int, channels: ChannelSpec = None,
                 sample_rate: Optional[int] = None, bit_depth: int = 16,
                 buffer_size: int = 1024):
        """
        Initialize WASAPI player.
        
        Args:
            device_id: Device ID from device enumeration
            channels: Channel specification (None for auto-detect from file)
            sample_rate: Sample rate in Hz (None for auto-detect from file)
            bit_depth: Bit depth (16, 24, 32)
            buffer_size: Buffer size in frames
        """
        self.device_id = device_id
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.buffer_size = buffer_size
        
        # Get device info
        self.device_info = get_device_info(device_id)
        if not self.device_info:
            raise DeviceError(f"Device {device_id} not found")
        
        if self.device_info.api_type != APIType.WASAPI:
            raise DeviceError(f"Device {device_id} is not a WASAPI device")
        
        if self.device_info.max_output_channels == 0:
            raise DeviceError(f"Device {device_id} has no output channels")
        
        # Channel mapping will be set when loading audio
        self.channel_mapper: Optional[ChannelMapper] = None
        
        # Audio format mapping
        self.format_map = {
            16: pyaudio.paInt16,
            24: pyaudio.paInt24,
            32: pyaudio.paInt32,
        }
        
        if bit_depth not in self.format_map:
            raise PlaybackError(f"Unsupported bit depth: {bit_depth}")
        
        self.pyaudio_format = self.format_map[bit_depth]
        
        # State
        self._pyaudio: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._playing = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Audio data
        self._audio_data: Optional[np.ndarray] = None
        self._file_info: Optional[dict] = None
        self._current_frame = 0
        self._total_frames = 0
        self._start_time: Optional[float] = None
        self._pause_time = 0.0
        
        # Callbacks
        self.callback_manager = CallbackManager()
    
    def set_progress_callback(self, callback: Optional[Callable[[CallbackInfo], None]]):
        """Set progress callback function"""
        self.callback_manager.set_progress_callback(callback)
    
    def set_time_callback(self, callback: Optional[Callable[[float, int, str], None]]):
        """Set simple time callback function"""
        self.callback_manager.set_time_callback(callback)
    
    def set_error_callback(self, callback: Optional[Callable[[str, Optional[str]], None]]):
        """Set error callback function"""
        self.callback_manager.set_error_callback(callback)
    
    def load_file(self, file_path: str) -> dict:
        """
        Load audio file and return file information.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with file information
        """
        try:
            if not Path(file_path).exists():
                raise FileError(f"Audio file not found: {file_path}")
            
            # Read audio file
            with sf.SoundFile(file_path, 'r') as f:
                self._audio_data = f.read(dtype=np.float32)
                
                # If mono, reshape to 2D
                if self._audio_data.ndim == 1:
                    self._audio_data = self._audio_data.reshape(-1, 1)
                
                file_info = {
                    'path': file_path,
                    'sample_rate': f.samplerate,
                    'channels': f.channels,
                    'frames': f.frames,
                    'duration': f.frames / f.samplerate,
                    'format': f.format,
                    'subtype': f.subtype,
                }
                
                self._file_info = file_info
                self._total_frames = f.frames
                self._current_frame = 0
                
                # Set sample rate if not specified
                if self.sample_rate is None:
                    self.sample_rate = f.samplerate
                
                # Validate sample rate
                if not self.device_info.supports_sample_rate(self.sample_rate):
                    print(f"Warning: Sample rate {self.sample_rate}Hz may not be supported by device")
                
                # Setup channel mapping
                if self.channel_mapper is None:
                    self.channel_mapper = ChannelMapper(None, self.device_info.max_output_channels)
                
                # Ensure audio data matches output channels
                self._prepare_audio_data()
                
                return file_info
                
        except Exception as e:
            raise FileError(f"Failed to load audio file: {e}")
    
    def load_data(self, audio_data: np.ndarray, sample_rate: int) -> dict:
        """
        Load audio data directly.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate of the audio data
            
        Returns:
            Dictionary with data information
        """
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data.reshape(-1, 1)
            
            self._audio_data = audio_data.astype(np.float32)
            self._total_frames = audio_data.shape[0]
            self._current_frame = 0
            
            if self.sample_rate is None:
                self.sample_rate = sample_rate
            
            # Setup channel mapping
            if self.channel_mapper is None:
                self.channel_mapper = ChannelMapper(None, self.device_info.max_output_channels)
            
            # Prepare audio data
            self._prepare_audio_data()
            
            data_info = {
                'sample_rate': sample_rate,
                'channels': audio_data.shape[1],
                'frames': audio_data.shape[0],
                'duration': audio_data.shape[0] / sample_rate,
                'format': 'numpy_array',
            }
            
            self._file_info = data_info
            return data_info
            
        except Exception as e:
            raise PlaybackError(f"Failed to load audio data: {e}")
    
    def _prepare_audio_data(self):
        """Prepare audio data for playback"""
        if self._audio_data is None or self.channel_mapper is None:
            return
        
        # Convert to target bit depth
        if self.bit_depth == 16:
            self._audio_data = (self._audio_data * 32767).astype(np.int16)
        elif self.bit_depth == 24:
            self._audio_data = (self._audio_data * 8388607).astype(np.int32)
        else:  # 32-bit
            self._audio_data = (self._audio_data * 2147483647).astype(np.int32)
        
        # Handle channel mapping
        input_channels = self._audio_data.shape[1]
        output_channels = self.device_info.max_output_channels
        
        if input_channels != output_channels:
            # Create output array
            output_data = np.zeros((self._audio_data.shape[0], output_channels), dtype=self._audio_data.dtype)
            
            # Map input channels to output channels
            for i, channel_idx in enumerate(self.channel_mapper.channel_indices):
                if i < input_channels and channel_idx < output_channels:
                    output_data[:, channel_idx] = self._audio_data[:, i]
            
            self._audio_data = output_data
    
    def play(self, start_position: float = 0.0):
        """
        Start playback.
        
        Args:
            start_position: Start position in seconds
        """
        if self._playing:
            raise PlaybackError("Playback already in progress")
        
        if self._audio_data is None:
            raise PlaybackError("No audio data loaded")
        
        try:
            # Set start position
            if start_position > 0:
                start_frame = int(start_position * self.sample_rate)
                self._current_frame = min(start_frame, self._total_frames)
            else:
                self._current_frame = 0
            
            self._setup_audio()
            
            # Start playback thread
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._playback_thread, daemon=True)
            self._playing = True
            self._paused = False
            self._start_time = time.time()
            self._pause_time = 0.0
            
            self.callback_manager.start_timing()
            self._thread.start()
            
        except Exception as e:
            self._cleanup()
            raise PlaybackError(f"Failed to start playback: {e}")
    
    def stop(self):
        """Stop playback"""
        if not self._playing:
            return
        
        # Signal stop and wait for thread
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        self._cleanup()
    
    def pause(self):
        """Pause playback"""
        if self._playing and not self._paused:
            self._paused = True
            self._pause_time = time.time()
    
    def resume(self):
        """Resume playback"""
        if self._playing and self._paused:
            self._paused = False
            # Adjust start time to account for pause duration
            if self._pause_time > 0:
                pause_duration = time.time() - self._pause_time
                self._start_time += pause_duration
                self._pause_time = 0.0
    
    def seek(self, position: float):
        """
        Seek to position in seconds.
        
        Args:
            position: Position in seconds
        """
        if self._audio_data is None:
            return
        
        target_frame = int(position * self.sample_rate)
        self._current_frame = max(0, min(target_frame, self._total_frames))
        
        if self._playing:
            # Adjust start time for new position
            self._start_time = time.time() - position
    
    def is_playing(self) -> bool:
        """Check if playing is active"""
        return self._playing and not self._paused
    
    def is_paused(self) -> bool:
        """Check if playback is paused"""
        return self._playing and self._paused
    
    def get_position(self) -> float:
        """Get current playback position in seconds"""
        if not self._start_time:
            return 0.0
        
        if self._paused:
            return (self._pause_time - self._start_time) if self._pause_time > 0 else 0.0
        
        return max(0.0, time.time() - self._start_time)
    
    def get_duration(self) -> float:
        """Get total duration in seconds"""
        if self._file_info:
            return self._file_info.get('duration', 0.0)
        return 0.0
    
    def get_progress(self) -> float:
        """Get playback progress (0.0 to 1.0)"""
        duration = self.get_duration()
        if duration > 0:
            return min(1.0, self.get_position() / duration)
        return 0.0
    
    def _setup_audio(self):
        """Setup PyAudio and stream"""
        try:
            self._pyaudio = pyaudio.PyAudio()
            
            # Create output stream
            self._stream = self._pyaudio.open(
                format=self.pyaudio_format,
                channels=self.device_info.max_output_channels,
                rate=self.sample_rate,
                output=True,
                output_device_index=self.device_info.pyaudio_index,
                frames_per_buffer=self.buffer_size,
                stream_callback=None,  # We'll use blocking mode
            )
            
        except Exception as e:
            raise PlaybackError(f"Failed to setup audio stream: {e}")
    
    def _playback_thread(self):
        """Main playback thread"""
        try:
            while not self._stop_event.is_set() and self._current_frame < self._total_frames:
                if self._paused:
                    time.sleep(0.01)
                    continue
                
                # Calculate frames to play
                frames_remaining = self._total_frames - self._current_frame
                frames_to_play = min(self.buffer_size, frames_remaining)
                
                if frames_to_play <= 0:
                    break
                
                # Get audio chunk
                try:
                    audio_chunk = self._audio_data[self._current_frame:self._current_frame + frames_to_play]
                    
                    # Convert to bytes for PyAudio
                    audio_bytes = audio_chunk.tobytes()
                    
                    # Play chunk
                    self._stream.write(audio_bytes)
                    
                    # Update position
                    self._current_frame += frames_to_play
                    
                    # Calculate levels for callback
                    peak_levels = []
                    for ch in range(audio_chunk.shape[1]):
                        channel_data = audio_chunk[:, ch]
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
                    
                    # Trigger callbacks
                    current_time = self.get_position()
                    duration = self.get_duration()
                    
                    # Progress callback
                    info = CallbackInfo(
                        current_time=current_time,
                        total_time=duration,
                        position=self.get_progress(),
                        device_name=self.device_info.name,
                        api_type=APIType.WASAPI,
                        mode=AudioMode.PLAYBACK,
                        status=AudioStatus.PAUSED if self._paused else AudioStatus.ACTIVE,
                        sample_rate=self.sample_rate,
                        channels=self.channel_mapper.count if self.channel_mapper else 2,
                        bit_depth=self.bit_depth,
                        buffer_size=self.buffer_size,
                        peak_levels=peak_levels,
                        elapsed_samples=self._current_frame,
                    )
                    
                    self.callback_manager.trigger_progress_callback(info)
                    
                    # Simple time callback
                    self.callback_manager.trigger_time_callback(
                        current_time, self._current_frame,
                        "paused" if self._paused else "playing"
                    )
                
                except Exception as e:
                    self.callback_manager.trigger_error_callback(
                        f"Playback error: {e}", self.device_info.name
                    )
                    break
        
        except Exception as e:
            self.callback_manager.trigger_error_callback(
                f"Playback thread error: {e}", self.device_info.name
            )
        finally:
            self._playing = False
    
    def _cleanup(self):
        """Cleanup resources"""
        self._playing = False
        
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
        if self._playing:
            self.stop()
        self._cleanup()


def play_audio_file(device_id: int, file_path: str,
                   channels: ChannelSpec = None, sample_rate: Optional[int] = None,
                   bit_depth: int = 16, start_position: float = 0.0,
                   progress_callback: Optional[Callable[[CallbackInfo], None]] = None) -> bool:
    """
    Convenience function to play an audio file.
    
    Args:
        device_id: Device ID for playback
        file_path: Path to audio file
        channels: Channel specification
        sample_rate: Sample rate (None for auto-detect)
        bit_depth: Bit depth
        start_position: Start position in seconds
        progress_callback: Optional progress callback
        
    Returns:
        True if playback was successful
    """
    try:
        with WASAPIPlayer(device_id, channels, sample_rate, bit_depth) as player:
            if progress_callback:
                player.set_progress_callback(progress_callback)
            
            file_info = player.load_file(file_path)
            player.play(start_position)
            
            # Wait for completion
            duration = file_info['duration'] - start_position
            time.sleep(max(0.1, duration))
            
            return True
            
    except Exception as e:
        print(f"Playback failed: {e}")
        return False