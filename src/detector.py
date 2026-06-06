"""
File type detection using magic bytes, entropy calculation, and MIME guessing
"""

import mimetypes
import math
import pathlib
from collections import Counter

# Magic bytes signatures for different file types
MAGIC_SIGNATURES = {
    b'\x1F\x8B': 'gzip',
    b'\x42\x5A\x68': 'bz2',
    b'\xFD\x37\x7A\x58\x5A\x00': 'xz',
    b'\x28\xB5\x2F\xFD': 'zstd',
    b'\x28\xB5\x2F\xFD\x04': 'zstd_dict',
    b'\xFF\xD8\xFF': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'%PDF': 'pdf',
    b'PK\x03\x04': 'zip',
    b'RIFF': 'riff',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
}

def detect_magic_type(file_path: str) -> str | None:
    """
    Detect file type by reading magic bytes from the beginning of the file
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type string or None if not detected
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            
        for magic, file_type in MAGIC_SIGNATURES.items():
            if header.startswith(magic):
                return file_type
        return None
    except Exception:
        return None

def guess_mime_type(file_path: str) -> str:
    """
    Guess MIME type using Python's mimetypes module
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"

def calculate_entropy(data: bytes) -> float:
    """
    Calculate Shannon entropy of binary data
    
    Higher entropy = more random = less compressible
    Lower entropy = more predictable = more compressible
    
    Args:
        data: Binary data to analyze
        
    Returns:
        Entropy value between 0 and 8
    """
    if not data:
        return 0.0
    
    byte_counts = Counter(data)
    total_bytes = len(data)
    
    entropy = 0.0
    for count in byte_counts.values():
        probability = count / total_bytes
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy

def get_sample_stats(file_path: str, sample_size: int = 256 * 1024) -> dict:
    """
    Analyze file statistics from a sample (first 256KB)
    
    Args:
        file_path: Path to the file
        sample_size: Number of bytes to analyze (default 256KB)
        
    Returns:
        Dictionary with analysis results
    """
    try:
        with open(file_path, 'rb') as f:
            sample_data = f.read(sample_size)
        
        if not sample_data:
            return {
                "entropy": 0.0,
                "text_ratio": 0.0,
                "newline_count": 0,
                "size_sampled": 0,
                "is_binary": True
            }
        
        entropy = calculate_entropy(sample_data)
        
        printable_count = 0
        for byte in sample_data:
            if 32 <= byte <= 126 or byte in (9, 10, 13):
                printable_count += 1
        
        text_ratio = printable_count / len(sample_data)
        newline_count = sample_data.count(b'\n')
        is_binary = text_ratio < 0.7 or entropy > 7.0
        
        return {
            "entropy": round(entropy, 3),
            "text_ratio": round(text_ratio, 3),
            "newline_count": newline_count,
            "size_sampled": len(sample_data),
            "is_binary": is_binary,
            "magic_type": detect_magic_type(file_path),
            "mime_type": guess_mime_type(file_path)
        }
    
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return {
            "entropy": 0.0,
            "text_ratio": 0.0,
            "newline_count": 0,
            "size_sampled": 0,
            "is_binary": True,
            "error": str(e)
        }

def is_already_compressed(file_path: str) -> bool:
    """
    Check if file is already compressed (based on magic bytes or extension)
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if already compressed, False otherwise
    """
    compressed_extensions = {'.gz', '.bz2', '.xz', '.zst', '.br', '.zip', '.7z', '.rar', '.tar'}
    
    file_ext = pathlib.Path(file_path).suffix.lower()
    if file_ext in compressed_extensions:
        return True
    
    magic_type = detect_magic_type(file_path)
    if magic_type in ['gzip', 'bz2', 'xz', 'zstd', 'zip']:
        return True
    
    return False