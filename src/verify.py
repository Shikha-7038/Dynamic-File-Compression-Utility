"""
Decompression and integrity verification
"""

import gzip
import bz2
import lzma
import brotli
import zstandard as zstd
import hashlib
import json
from pathlib import Path
from typing import Optional

def calculate_sha256_stream(file_obj) -> str:
    """
    Calculate SHA-256 hash from a file object
    
    Args:
        file_obj: File object in binary mode
        
    Returns:
        SHA-256 hash as hex string
    """
    sha256_hash = hashlib.sha256()
    for chunk in iter(lambda: file_obj.read(1024 * 1024), b''):
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def decompress_file(compressed_path: str, output_path: Optional[str] = None) -> str:
    """
    Decompress a file based on its extension
    
    Args:
        compressed_path: Path to compressed file
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to decompressed file
    """
    compressed_path = Path(compressed_path)
    
    # Ensure decompressed_files directory exists
    decompressed_dir = Path("decompressed_files")
    decompressed_dir.mkdir(exist_ok=True)
    
    if output_path is None:
        original_name = compressed_path.stem
        for ext in ['.zst', '.gz', '.bz2', '.xz', '.br', '.store']:
            if original_name.endswith(ext):
                original_name = original_name[:-len(ext)]
                break
        output_path = decompressed_dir / f"{original_name}_restored.txt"
    else:
        output_path = Path(output_path)
    
    print(f"\n📂 Decompressing: {compressed_path.name}")
    
    if compressed_path.name.endswith('.zst'):
        with open(compressed_path, 'rb') as src_file:
            dctx = zstd.ZstdDecompressor()
            with dctx.stream_reader(src_file) as reader:
                with open(output_path, 'wb') as dst_file:
                    while True:
                        chunk = reader.read(1024 * 1024)
                        if not chunk:
                            break
                        dst_file.write(chunk)
    
    elif compressed_path.name.endswith('.br'):
        with open(compressed_path, 'rb') as src_file:
            compressed_data = src_file.read()
            decompressed_data = brotli.decompress(compressed_data)
            with open(output_path, 'wb') as dst_file:
                dst_file.write(decompressed_data)
    
    elif compressed_path.name.endswith('.gz'):
        with gzip.open(compressed_path, 'rb') as src_file:
            with open(output_path, 'wb') as dst_file:
                while True:
                    chunk = src_file.read(1024 * 1024)
                    if not chunk:
                        break
                    dst_file.write(chunk)
    
    elif compressed_path.name.endswith('.bz2'):
        with bz2.open(compressed_path, 'rb') as src_file:
            with open(output_path, 'wb') as dst_file:
                while True:
                    chunk = src_file.read(1024 * 1024)
                    if not chunk:
                        break
                    dst_file.write(chunk)
    
    elif compressed_path.name.endswith('.xz'):
        with lzma.open(compressed_path, 'rb') as src_file:
            with open(output_path, 'wb') as dst_file:
                while True:
                    chunk = src_file.read(1024 * 1024)
                    if not chunk:
                        break
                    dst_file.write(chunk)
    
    elif compressed_path.name.endswith('.store'):
        with open(compressed_path, 'rb') as src_file:
            with open(output_path, 'wb') as dst_file:
                while True:
                    chunk = src_file.read(1024 * 1024)
                    if not chunk:
                        break
                    dst_file.write(chunk)
    
    else:
        raise ValueError(f"Unknown compression format: {compressed_path}")
    
    print(f"   ✅ Decompressed to: {output_path}")
    return str(output_path)

def verify_integrity(manifest_path: str) -> bool:
    """
    Verify decompressed file matches original using SHA-256
    
    Args:
        manifest_path: Path to manifest JSON file
        
    Returns:
        True if verification passes, False otherwise
    """
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    compressed_file = manifest['compressed_file']
    original_hash = manifest['sha256_hash']
    original_size = manifest['original_size_bytes']
    
    print(f"\n🔍 Verifying: {Path(compressed_file).name}")
    
    try:
        temp_output = Path("decompressed_files") / "__verify_temp__"
        decompress_file(compressed_file, str(temp_output))
        
        with open(temp_output, 'rb') as f:
            decompressed_hash = calculate_sha256_stream(f)
        
        decompressed_size = temp_output.stat().st_size
        temp_output.unlink()
        
        if decompressed_hash == original_hash and decompressed_size == original_size:
            print(f"   ✅ Verification PASSED")
            print(f"   Hash match: {original_hash[:16]}...")
            print(f"   Size match: {original_size:,} bytes")
            return True
        else:
            print(f"   ❌ Verification FAILED")
            print(f"   Expected hash: {original_hash}")
            print(f"   Got hash: {decompressed_hash}")
            return False
    
    except Exception as e:
        print(f"   ❌ Verification error: {e}")
        return False

def decompress_with_verify(compressed_path: str, output_path: Optional[str] = None) -> bool:
    """
    Decompress a file and verify against its manifest
    
    Args:
        compressed_path: Path to compressed file
        output_path: Optional output path
        
    Returns:
        True if verification passes
    """
    manifest_path = str(Path(compressed_path).parent / f"{Path(compressed_path).name}.dfc.json")
    
    if Path(manifest_path).exists():
        decompress_file(compressed_path, output_path)
        return verify_integrity(manifest_path)
    else:
        print("⚠️  No manifest found, skipping verification")
        decompress_file(compressed_path, output_path)
        return True