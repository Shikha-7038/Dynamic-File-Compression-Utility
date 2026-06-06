"""
Dictionary training for Zstandard compression
Improves compression ratio for repetitive text (logs, JSON, CSV)
"""

import zstandard as zstd
import pathlib
import random
from typing import List

def train_dictionary(glob_pattern: str = "samples/*.log", 
                     dict_size: int = 112 * 1024,
                     sample_chunk_size: int = 4096) -> str:
    """
    Train a Zstandard dictionary from sample files
    
    Args:
        glob_pattern: Pattern to match sample files
        dict_size: Dictionary size in bytes (max 112KB for zstd)
        sample_chunk_size: Size of chunks to sample from each file
        
    Returns:
        Dictionary ID string
    """
    sample_paths = list(pathlib.Path(".").glob(glob_pattern))
    
    if not sample_paths:
        print(f"No files found matching pattern: {glob_pattern}")
        return ""
    
    print(f"\n📚 Training dictionary from {len(sample_paths)} files...")
    
    samples = []
    
    for file_path in sample_paths:
        try:
            file_data = file_path.read_bytes()
            file_size = len(file_data)
            
            num_chunks = min(50, max(1, file_size // sample_chunk_size))
            
            for _ in range(num_chunks):
                if file_size > sample_chunk_size:
                    offset = random.randrange(0, file_size - sample_chunk_size)
                else:
                    offset = 0
                
                chunk = file_data[offset:offset + sample_chunk_size]
                samples.append(chunk)
                
        except Exception as e:
            print(f"   Warning: Could not read {file_path}: {e}")
    
    if not samples:
        print("   No samples collected!")
        return ""
    
    print(f"   Collected {len(samples)} samples")
    print(f"   Dictionary size: {dict_size:,} bytes")
    
    try:
        dictionary = zstd.train_dictionary(dict_size, samples)
        
        # Save to outputs folder
        outputs_dir = pathlib.Path("outputs")
        outputs_dir.mkdir(exist_ok=True)
        
        dict_id = f"zstd_dict_{dict_size}_{len(sample_paths)}"
        dict_path = outputs_dir / f"{dict_id}.dict"
        dict_path.write_bytes(dictionary.as_bytes())
        
        print(f"   ✅ Dictionary saved to: {dict_path}")
        print(f"   Dictionary ID: {dict_id}")
        
        return dict_id
        
    except Exception as e:
        print(f"   ❌ Dictionary training failed: {e}")
        return ""

def load_dictionary(dict_path: str):
    """
    Load a trained dictionary for compression
    
    Args:
        dict_path: Path to dictionary file
        
    Returns:
        Zstandard dictionary object
    """
    dict_data = pathlib.Path(dict_path).read_bytes()
    return zstd.ZstdCompressionDict(dict_data)

def test_dictionary_effectiveness(file_path: str, dict_path: str) -> dict:
    """
    Test how much a dictionary improves compression
    
    Args:
        file_path: File to test compression on
        dict_path: Path to trained dictionary
        
    Returns:
        Dictionary with compression statistics
    """
    import time
    
    file_data = pathlib.Path(file_path).read_bytes()
    original_size = len(file_data)
    
    cctx_no_dict = zstd.ZstdCompressor(level=6)
    compressed_no_dict = cctx_no_dict.compress(file_data)
    size_no_dict = len(compressed_no_dict)
    
    dictionary = load_dictionary(dict_path)
    cctx_with_dict = zstd.ZstdCompressor(level=6, dict_data=dictionary)
    compressed_with_dict = cctx_with_dict.compress(file_data)
    size_with_dict = len(compressed_with_dict)
    
    improvement_bytes = size_no_dict - size_with_dict
    improvement_percent = (improvement_bytes / size_no_dict) * 100
    
    results = {
        "original_size": original_size,
        "without_dict_size": size_no_dict,
        "with_dict_size": size_with_dict,
        "saved_bytes": improvement_bytes,
        "saved_percent": round(improvement_percent, 2)
    }
    
    print(f"\n📊 Dictionary Effectiveness Test:")
    print(f"   Without dict: {size_no_dict:,} bytes")
    print(f"   With dict:    {size_with_dict:,} bytes")
    print(f"   Saved:        {improvement_bytes:,} bytes ({improvement_percent:.1f}%)")
    
    return results