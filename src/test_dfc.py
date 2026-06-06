"""
Unit tests for the compression utility
"""

import pytest
import os
import tempfile
import pathlib
import random
import string
import json

import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.compress import compress_file
from src.verify import decompress_file, verify_integrity
from src.detector import get_sample_stats, calculate_entropy
from src.strategy import choose_strategy

def create_test_file(content: bytes, suffix: str = ".txt") -> str:
    """Create a temporary test file"""
    temp_dir = tempfile.gettempdir()
    file_path = pathlib.Path(temp_dir) / f"test_{os.urandom(8).hex()}{suffix}"
    file_path.write_bytes(content)
    return str(file_path)

def create_text_file(lines: int = 1000) -> str:
    """Create a text file with repeated lines"""
    content = ""
    for i in range(lines):
        content += f"Line {i}: This is a test line for compression\n"
    return create_test_file(content.encode())

def create_binary_file(size: int = 10000) -> str:
    """Create a random binary file"""
    content = os.urandom(size)
    return create_test_file(content, ".bin")

def test_text_file_compression():
    """Test compression of text files"""
    src = create_text_file(500)
    
    try:
        manifest = compress_file(src, mode="auto")
        
        assert "compressed_file" in manifest
        assert manifest["original_size_bytes"] > 0
        assert manifest["compressed_size_bytes"] > 0
        
        manifest_path = pathlib.Path(manifest["compressed_file"]).parent / f"{pathlib.Path(manifest['compressed_file']).name}.dfc.json"
        assert verify_integrity(str(manifest_path))
        
    finally:
        pathlib.Path(src).unlink(missing_ok=True)

def test_binary_file_compression():
    """Test compression of binary files"""
    src = create_binary_file(50000)
    
    try:
        manifest = compress_file(src, mode="max")
        
        assert manifest["original_size_bytes"] > 0
        assert manifest["compressed_size_bytes"] > 0
        
    finally:
        pathlib.Path(src).unlink(missing_ok=True)

def test_roundtrip():
    """Test decompression matches original exactly"""
    original_content = b"Hello World! " * 1000
    src = create_test_file(original_content)
    
    try:
        manifest = compress_file(src, mode="fast")
        compressed_file = manifest["compressed_file"]
        
        decompressed_file = str(pathlib.Path(compressed_file).parent / "test_restored.txt")
        decompress_file(compressed_file, decompressed_file)
        
        decompressed_content = pathlib.Path(decompressed_file).read_bytes()
        assert decompressed_content == original_content
        
        pathlib.Path(decompressed_file).unlink(missing_ok=True)
        
    finally:
        pathlib.Path(src).unlink(missing_ok=True)

def test_different_modes():
    """Test all compression modes work"""
    src = create_text_file(200)
    
    try:
        for mode in ["auto", "fast", "balanced", "max"]:
            manifest = compress_file(src, mode=mode)
            manifest_path = pathlib.Path(manifest["compressed_file"]).parent / f"{pathlib.Path(manifest['compressed_file']).name}.dfc.json"
            assert verify_integrity(str(manifest_path))
            
            pathlib.Path(manifest["compressed_file"]).unlink(missing_ok=True)
            manifest_path.unlink(missing_ok=True)
            
    finally:
        pathlib.Path(src).unlink(missing_ok=True)

def test_entropy_calculation():
    """Test entropy calculation works correctly"""
    low_entropy_data = b"A" * 1000
    low_entropy = calculate_entropy(low_entropy_data)
    assert low_entropy < 0.1
    
    high_entropy_data = os.urandom(1000)
    high_entropy = calculate_entropy(high_entropy_data)
    assert high_entropy > 7.0

def test_strategy_selection():
    """Test strategy selection for different file types"""
    text_file = create_text_file(100)
    plan = choose_strategy(text_file)
    assert plan.codec in ["zstd", "brotli"]
    pathlib.Path(text_file).unlink()
    
    binary_file = create_binary_file(1000)
    plan = choose_strategy(binary_file)
    assert plan.codec in ["lzma", "zstd", "store"]
    pathlib.Path(binary_file).unlink()

def test_empty_file():
    """Test compression of empty file"""
    src = create_test_file(b"")
    
    try:
        manifest = compress_file(src)
        assert manifest["original_size_bytes"] == 0
        assert manifest["compressed_size_bytes"] == 0
        assert manifest["compression_ratio"] == 1.0
        
    finally:
        pathlib.Path(src).unlink(missing_ok=True)