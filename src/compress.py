"""
Streaming compression for multiple codecs with integrity verification
"""

import gzip
import bz2
import lzma
import brotli
import zstandard as zstd
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Optional

from src.strategy import choose_strategy, CompressionPlan, get_codec_extension

def calculate_sha256(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash as hex string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def create_manifest(src_path: str, dst_path: str, plan: CompressionPlan, 
                    orig_size: int, comp_size: int, duration: float) -> Dict:
    """
    Create compression metadata manifest
    
    Args:
        src_path: Source file path
        dst_path: Compressed file path
        plan: Compression plan used
        orig_size: Original file size
        comp_size: Compressed file size
        duration: Compression time in seconds
        
    Returns:
        Dictionary with manifest data
    """
    manifest = {
        "source_file": src_path,
        "compressed_file": dst_path,
        "codec": plan.codec,
        "compression_level": plan.level,
        "chunk_size": plan.chunk_size,
        "threads": plan.threads,
        "original_size_bytes": orig_size,
        "compressed_size_bytes": comp_size,
        "compression_ratio": round(comp_size / orig_size, 4) if orig_size > 0 else 1.0,
        "space_saved_percent": round((1 - comp_size / orig_size) * 100, 2) if orig_size > 0 else 0,
        "compression_time_seconds": round(duration, 2),
        "sha256_hash": calculate_sha256(src_path)
    }
    
    manifest_path = Path(dst_path).parent / f"{Path(dst_path).name}.dfc.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    return manifest

def compress_with_zstd(src_path: str, dst_path: str, plan: CompressionPlan) -> tuple:
    """Compress using Zstandard (zstd)"""
    start_time = time.time()
    
    cctx = zstd.ZstdCompressor(level=plan.level, threads=plan.threads or 1)
    
    with open(src_path, 'rb') as src_file:
        with open(dst_path, 'wb') as dst_file:
            with cctx.stream_writer(dst_file) as compressor:
                while True:
                    chunk = src_file.read(plan.chunk_size)
                    if not chunk:
                        break
                    compressor.write(chunk)
    
    duration = time.time() - start_time
    return dst_path, duration

def compress_with_brotli(src_path: str, dst_path: str, plan: CompressionPlan) -> tuple:
    """Compress using Brotli"""
    start_time = time.time()
    
    compressor = brotli.Compressor(quality=plan.level)
    
    with open(src_path, 'rb') as src_file:
        with open(dst_path, 'wb') as dst_file:
            while True:
                chunk = src_file.read(plan.chunk_size)
                if not chunk:
                    break
                compressed_chunk = compressor.process(chunk)
                if compressed_chunk:
                    dst_file.write(compressed_chunk)
            dst_file.write(compressor.finish())
    
    duration = time.time() - start_time
    return dst_path, duration

def compress_with_gzip(src_path: str, dst_path: str, plan: CompressionPlan) -> tuple:
    """Compress using GZIP"""
    start_time = time.time()
    
    with open(src_path, 'rb') as src_file:
        with gzip.open(dst_path, 'wb', compresslevel=plan.level) as dst_file:
            while True:
                chunk = src_file.read(plan.chunk_size)
                if not chunk:
                    break
                dst_file.write(chunk)
    
    duration = time.time() - start_time
    return dst_path, duration

def compress_with_bz2(src_path: str, dst_path: str, plan: CompressionPlan) -> tuple:
    """Compress using BZIP2"""
    start_time = time.time()
    
    with open(src_path, 'rb') as src_file:
        with bz2.open(dst_path, 'wb', compresslevel=min(9, plan.level)) as dst_file:
            while True:
                chunk = src_file.read(plan.chunk_size)
                if not chunk:
                    break
                dst_file.write(chunk)
    
    duration = time.time() - start_time
    return dst_path, duration

def compress_with_lzma(src_path: str, dst_path: str, plan: CompressionPlan) -> tuple:
    """Compress using LZMA/XZ"""
    start_time = time.time()
    
    with open(src_path, 'rb') as src_file:
        with lzma.open(dst_path, 'wb', preset=min(9, plan.level)) as dst_file:
            while True:
                chunk = src_file.read(plan.chunk_size)
                if not chunk:
                    break
                dst_file.write(chunk)
    
    duration = time.time() - start_time
    return dst_path, duration

def compress_with_store(src_path: str, dst_path: str) -> tuple:
    """Copy file without compression"""
    start_time = time.time()
    
    with open(src_path, 'rb') as src_file:
        with open(dst_path, 'wb') as dst_file:
            while True:
                chunk = src_file.read(1024 * 1024)
                if not chunk:
                    break
                dst_file.write(chunk)
    
    duration = time.time() - start_time
    return dst_path, duration

def compress_file(src_path: str, dst_path: Optional[str] = None, 
                  mode: str = "auto") -> Dict:
    """
    Main compression function - automatically selects best codec
    
    Args:
        src_path: Path to source file
        dst_path: Optional destination path (auto-generated if None)
        mode: Compression mode ('auto', 'fast', 'balanced', 'max')
        
    Returns:
        Dictionary with compression results and manifest
    """
    src_path = Path(src_path)
    
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src_path}")
    
    plan = choose_strategy(str(src_path), mode)
    
    # Ensure compressed_files directory exists
    compressed_dir = Path("compressed_files")
    compressed_dir.mkdir(exist_ok=True)
    
    if dst_path is None:
        extension = get_codec_extension(plan.codec)
        dst_path = compressed_dir / f"{src_path.stem}{extension}"
    else:
        dst_path = Path(dst_path)
    
    original_size = src_path.stat().st_size
    
    print(f"\n📁 Compressing: {src_path.name}")
    print(f"   Mode: {mode.upper()}")
    print(f"   Codec: {plan.codec.upper()} (level {plan.level})")
    print(f"   Original size: {original_size:,} bytes")
    
    if plan.codec == "zstd":
        _, duration = compress_with_zstd(str(src_path), str(dst_path), plan)
    elif plan.codec == "brotli":
        _, duration = compress_with_brotli(str(src_path), str(dst_path), plan)
    elif plan.codec == "gzip":
        _, duration = compress_with_gzip(str(src_path), str(dst_path), plan)
    elif plan.codec == "bz2":
        _, duration = compress_with_bz2(str(src_path), str(dst_path), plan)
    elif plan.codec == "lzma":
        _, duration = compress_with_lzma(str(src_path), str(dst_path), plan)
    elif plan.codec == "store":
        _, duration = compress_with_store(str(src_path), str(dst_path))
    else:
        raise ValueError(f"Unknown codec: {plan.codec}")
    
    compressed_size = dst_path.stat().st_size
    
    manifest = create_manifest(str(src_path), str(dst_path), plan, 
                               original_size, compressed_size, duration)
    
    ratio = compressed_size / original_size
    saved_percent = (1 - ratio) * 100
    print(f"   Compressed size: {compressed_size:,} bytes")
    print(f"   Compression ratio: {ratio:.3f} ({saved_percent:.1f}% saved)")
    print(f"   Time: {duration:.2f} seconds")
    print(f"   ✅ Saved to: {dst_path}")
    
    return manifest