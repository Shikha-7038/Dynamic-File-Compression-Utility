"""
Strategy selection for choosing optimal compression codec and level
"""

from dataclasses import dataclass
from pathlib import Path
from src.detector import get_sample_stats, is_already_compressed, guess_mime_type

@dataclass
class CompressionPlan:
    """
    Compression configuration plan
    
    Attributes:
        codec: Compression algorithm ('gzip', 'bz2', 'lzma', 'zstd', 'brotli', 'store')
        level: Compression level (1-22 depending on codec)
        chunk_size: Size of chunks for streaming (bytes)
        threads: Number of threads for parallel compression (0 = auto)
        store: If True, just copy file without compression
        dict_id: Dictionary ID for zstd dictionary training
    """
    codec: str
    level: int
    chunk_size: int
    threads: int
    store: bool = False
    dict_id: str | None = None

def choose_strategy(file_path: str, mode: str = "auto") -> CompressionPlan:
    """
    Choose optimal compression strategy based on file analysis
    
    Args:
        file_path: Path to the file to compress
        mode: Compression mode ('auto', 'fast', 'balanced', 'max')
        
    Returns:
        CompressionPlan with optimal settings
    """
    
    if is_already_compressed(file_path):
        return CompressionPlan(
            codec="store",
            level=0,
            chunk_size=0,
            threads=0,
            store=True
        )
    
    stats = get_sample_stats(file_path)
    mime_type = guess_mime_type(file_path)
    
    if mode == "fast":
        return CompressionPlan(
            codec="zstd",
            level=3,
            chunk_size=1024 * 1024,
            threads=0,
            store=False
        )
    
    if mode == "max":
        return CompressionPlan(
            codec="lzma",
            level=9,
            chunk_size=1024 * 1024,
            threads=0,
            store=False
        )
    
    if mode == "balanced":
        return CompressionPlan(
            codec="zstd",
            level=6,
            chunk_size=4 * 1024 * 1024,
            threads=0,
            store=False
        )
    
    # Auto mode - intelligent selection
    if stats.get('is_binary', True) and stats.get('entropy', 8) > 7.5:
        if stats.get('magic_type'):
            return CompressionPlan(
                codec="store",
                level=0,
                chunk_size=0,
                threads=0,
                store=True
            )
    
    if stats.get('text_ratio', 0) > 0.7 and stats.get('entropy', 8) < 7.0:
        if stats.get('newline_count', 0) > 100:
            return CompressionPlan(
                codec="zstd",
                level=8,
                chunk_size=4 * 1024 * 1024,
                threads=0,
                store=False
            )
        else:
            return CompressionPlan(
                codec="brotli",
                level=6,
                chunk_size=2 * 1024 * 1024,
                threads=0,
                store=False
            )
    
    if 'json' in mime_type or 'csv' in mime_type or 'text' in mime_type:
        return CompressionPlan(
            codec="zstd",
            level=10,
            chunk_size=4 * 1024 * 1024,
            threads=0,
            store=False
        )
    
    if mime_type.startswith('image/') or mime_type.startswith('video/') or mime_type.startswith('audio/'):
        return CompressionPlan(
            codec="store",
            level=0,
            chunk_size=0,
            threads=0,
            store=True
        )
    
    if stats.get('entropy', 8) < 6.5:
        return CompressionPlan(
            codec="lzma",
            level=6,
            chunk_size=1024 * 1024,
            threads=0,
            store=False
        )
    
    return CompressionPlan(
        codec="zstd",
        level=6,
        chunk_size=2 * 1024 * 1024,
        threads=0,
        store=False
    )

def get_codec_extension(codec: str) -> str:
    """
    Get file extension for a given codec
    
    Args:
        codec: Codec name
        
    Returns:
        File extension (including dot)
    """
    extensions = {
        'gzip': '.gz',
        'bz2': '.bz2',
        'lzma': '.xz',
        'zstd': '.zst',
        'brotli': '.br',
        'store': '.store'
    }
    return extensions.get(codec, '.bin')