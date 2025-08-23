"""Channel processing and parsing logic"""

from typing import Union, List, Optional, Tuple
from ..utils.exceptions import ChannelError


ChannelSpec = Union[str, int, List[int], Tuple[int, ...], range, None]


def parse_channels(channels: ChannelSpec) -> List[int]:
    """
    Parse channel specification and convert to 0-based channel indices.
    
    Args:
        channels: Channel specification in various formats:
            - None: Default stereo (1-2) -> [0, 1]
            - str: Range format "1-6" -> [0, 1, 2, 3, 4, 5]
            - int: Single channel 1 -> [0]
            - List[int]: Multiple channels [1, 3, 5] -> [0, 2, 4]
            - range: Range object range(1, 7) -> [0, 1, 2, 3, 4, 5]
    
    Returns:
        List of 0-based channel indices
        
    Raises:
        ChannelError: If channel specification is invalid
    """
    if channels is None:
        return [0, 1]  # Default stereo
    
    if isinstance(channels, str):
        return _parse_string_channels(channels)
    
    if isinstance(channels, int):
        if channels < 1:
            raise ChannelError(f"Channel number must be >= 1, got {channels}")
        return [channels - 1]  # Convert to 0-based
    
    if isinstance(channels, range):
        if len(channels) == 0:
            raise ChannelError("Empty channel range")
        if min(channels) < 1:
            raise ChannelError(f"Channel numbers must be >= 1, got min {min(channels)}")
        return [ch - 1 for ch in channels]  # Convert to 0-based
    
    if isinstance(channels, (list, tuple)):
        if len(channels) == 0:
            raise ChannelError("Empty channel list")
        if any(ch < 1 for ch in channels):
            raise ChannelError("All channel numbers must be >= 1")
        return [ch - 1 for ch in channels]  # Convert to 0-based
    
    raise ChannelError(f"Invalid channel specification type: {type(channels)}")


def _parse_string_channels(channels: str) -> List[int]:
    """Parse string channel specification like '1-6' or '1'"""
    channels = channels.strip()
    
    if not channels:
        raise ChannelError("Empty channel string")
    
    if '-' in channels:
        # Range specification like "1-6"
        parts = channels.split('-')
        if len(parts) != 2:
            raise ChannelError(f"Invalid range format: '{channels}'. Use format '1-6'")
        
        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            raise ChannelError(f"Invalid numbers in range: '{channels}'")
        
        if start < 1 or end < 1:
            raise ChannelError(f"Channel numbers must be >= 1, got range {start}-{end}")
        
        if start > end:
            raise ChannelError(f"Start channel ({start}) must be <= end channel ({end})")
        
        return list(range(start - 1, end))  # Convert to 0-based, end is inclusive
    
    else:
        # Single channel like "1"
        try:
            channel = int(channels)
        except ValueError:
            raise ChannelError(f"Invalid channel number: '{channels}'")
        
        if channel < 1:
            raise ChannelError(f"Channel number must be >= 1, got {channel}")
        
        return [channel - 1]  # Convert to 0-based


def validate_channels(channel_indices: List[int], max_channels: int) -> None:
    """
    Validate that channel indices are within device limits.
    
    Args:
        channel_indices: 0-based channel indices
        max_channels: Maximum channels supported by device
        
    Raises:
        ChannelError: If any channel index is out of range
    """
    if not channel_indices:
        raise ChannelError("No channels specified")
    
    max_index = max(channel_indices)
    if max_index >= max_channels:
        # Convert back to 1-based for error message
        user_channel = max_index + 1
        raise ChannelError(
            f"Channel {user_channel} exceeds device limit of {max_channels} channels"
        )


def channels_to_user_string(channel_indices: List[int]) -> str:
    """
    Convert 0-based channel indices back to user-friendly string.
    
    Args:
        channel_indices: 0-based channel indices
        
    Returns:
        User-friendly string representation
    """
    if not channel_indices:
        return "None"
    
    # Convert to 1-based
    user_channels = [ch + 1 for ch in channel_indices]
    
    if len(user_channels) == 1:
        return str(user_channels[0])
    
    # Check if it's a continuous range
    if user_channels == list(range(min(user_channels), max(user_channels) + 1)):
        return f"{min(user_channels)}-{max(user_channels)}"
    
    # Otherwise, list individual channels
    return ",".join(map(str, user_channels))


class ChannelMapper:
    """Helper class for managing channel mappings"""
    
    def __init__(self, channels: ChannelSpec, max_channels: int):
        self.channel_indices = parse_channels(channels)
        validate_channels(self.channel_indices, max_channels)
        self.max_channels = max_channels
    
    @property
    def count(self) -> int:
        """Number of channels"""
        return len(self.channel_indices)
    
    @property
    def user_string(self) -> str:
        """User-friendly string representation"""
        return channels_to_user_string(self.channel_indices)
    
    def map_data(self, multi_channel_data, frame_count: int):
        """
        Extract specified channels from multi-channel audio data.
        
        Args:
            multi_channel_data: Input audio data
            frame_count: Number of frames
            
        Returns:
            Data for selected channels only
        """
        # This will be implemented based on the audio library being used
        # (PyAudio, sounddevice, etc.)
        pass