"""
Archive mode for compressing entire folders
"""

import tarfile
import zstandard as zstd
import pathlib
import os
from typing import Optional

def compress_folder(folder_path: str, 
                   output_path: Optional[str] = None,
                   compression_level: int = 8) -> str:
    """
    Compress an entire folder into a tar.zst archive
    
    Args:
        folder_path: Path to folder to compress
        output_path: Optional output path (auto-generated if None)
        compression_level: Zstd compression level (1-22)
        
    Returns:
        Path to created archive
    """
    folder_path = pathlib.Path(folder_path)
    
    if not folder_path.exists() or not folder_path.is_dir():
        raise ValueError(f"Folder not found: {folder_path}")
    
    # Ensure compressed_files directory exists
    compressed_dir = pathlib.Path("compressed_files")
    compressed_dir.mkdir(exist_ok=True)
    
    if output_path is None:
        output_path = compressed_dir / f"{folder_path.name}.tar.zst"
    else:
        output_path = pathlib.Path(output_path)
    
    print(f"\n📦 Archiving folder: {folder_path.name}")
    print(f"   Compression level: {compression_level}")
    
    cctx = zstd.ZstdCompressor(level=compression_level)
    
    with open(output_path, 'wb') as f_out:
        with cctx.stream_writer(f_out) as compressor:
            with tarfile.open(mode='w|', fileobj=compressor) as tar:
                tar.add(folder_path, arcname=folder_path.name)
    
    compressed_size = output_path.stat().st_size
    
    original_size = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = pathlib.Path(root) / file
            original_size += file_path.stat().st_size
    
    ratio = compressed_size / original_size if original_size > 0 else 1
    saved_percent = (1 - ratio) * 100
    
    print(f"   Original size: {original_size:,} bytes")
    print(f"   Archive size: {compressed_size:,} bytes")
    print(f"   Saved: {saved_percent:.1f}%")
    print(f"   ✅ Created: {output_path}")
    
    return str(output_path)

def decompress_archive(archive_path: str, output_folder: Optional[str] = None) -> str:
    """
    Decompress a tar.zst archive
    
    Args:
        archive_path: Path to .tar.zst archive
        output_folder: Optional output folder (auto-generated if None)
        
    Returns:
        Path to decompressed folder
    """
    archive_path = pathlib.Path(archive_path)
    
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")
    
    # Ensure decompressed_files directory exists
    decompressed_dir = pathlib.Path("decompressed_files")
    decompressed_dir.mkdir(exist_ok=True)
    
    if output_folder is None:
        output_folder = decompressed_dir / archive_path.name.replace('.tar.zst', '')
    else:
        output_folder = pathlib.Path(output_folder)
    
    print(f"\n📦 Extracting archive: {archive_path.name}")
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    with open(archive_path, 'rb') as f_in:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f_in) as reader:
            with tarfile.open(mode='r|', fileobj=reader) as tar:
                tar.extractall(output_folder)
    
    print(f"   ✅ Extracted to: {output_folder}")
    return str(output_folder)