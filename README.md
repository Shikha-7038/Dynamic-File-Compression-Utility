# 🗜️ Dynamic File Compression Utility

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](https://pytest.org)

> **A smart, cross-platform compression utility that automatically selects the best lossless codec based on file type and content.**

## 🎯 Project Overview

The **Dynamic File Compression Utility** is an intelligent, production-ready compression tool that automatically analyzes file content and selects the optimal compression algorithm (gzip, bzip2, lzma/xz, zstd, or brotli) based on file type, entropy, and compression requirements.

Unlike traditional compression tools that use a one-size-fits-all approach, this utility:
1. **Analyzes** file content (text ratio, entropy, magic bytes)
2. **Decides** the best codec and compression level
3. **Compresses** using streaming (handles large files)
4. **Verifies** integrity with SHA-256 checksums
5. **Decompresses** back to original with 100% accuracy

## ❓ Problem Statement

**The Challenge:** Different file types compress differently:
- Text files (logs, JSON, CSV) → compress well with any codec
- Already compressed files (JPEG, PNG, MP4) → should not be recompressed
- Binary files → need specific algorithms for best results
- Large files → require streaming to avoid memory issues

**The Solution:** A content-aware utility that:
- Automatically detects file characteristics
- Chooses optimal compression strategy
- Handles files of any size via streaming
- Provides both CLI and programmatic API

## 🧠 DSA Concepts Used

| DSA Concept | Application in Project | Location |
|-------------|------------------------|----------|
| **Hash Maps** | Character frequency analysis, MIME type detection, Magic byte lookup | `detector.py` |
| **Priority Queue** | Codec priority selection based on compression ratio | `strategy.py` |
| **Binary Trees** | Huffman coding (internal to zstd/brotli) | Codec internals |
| **Greedy Algorithms** | Optimal codec selection based on file analysis | `strategy.py` |
| **Streaming Algorithms** | Chunk-based file processing for large files | `compress.py` |
| **File I/O** | Binary file handling with buffered reads/writes | All modules |
| **Checksum/Verification** | SHA-256 integrity checking | `verify.py` |
| **Dynamic Programming** | Dictionary training for zstd | `dict_train.py` |
| **Tree Data Structure** | Archive (tar) file structure | `archive.py` |

## 🔬 Algorithm Explanation

### Step-by-Step Compression Flow:
Input File → Detection → Strategy Selection → Compression → Verification → Output

## ✨ Features

### Core Features
- ✅ **Auto Codec Selection** - Intelligently chooses from 6 compression algorithms
- ✅ **Streaming Compression** - Handles files of any size (no memory limit)
- ✅ **Multiple Modes** - Auto, Fast, Balanced, Max compression
- ✅ **Integrity Verification** - SHA-256 checksum verification
- ✅ **Dictionary Training** - Improve compression for repetitive data
- ✅ **Archive Mode** - Compress entire folders to .tar.zst
- ✅ **Parallel Processing** - Multi-threaded compression support
- ✅ **Cross-Platform** - Works on Windows, macOS, Linux

### Technical Features
- 🚀 **Chunk-based Processing** - 1-4MB chunks for optimal performance
- 📊 **Compression Reports** - Detailed JSON/Markdown reports
- 🔐 **Manifest Files** - Store metadata for verification
- 🎯 **Content Detection** - Magic bytes + entropy analysis
- 📈 **Performance Metrics** - Time, ratio, space saved

## 🛠️ Tech Stack

### Languages & Frameworks
- **Python 3.10+** - Core language
- **argparse** - CLI interface
- **pytest** - Unit testing

### Compression Libraries
| Codec | Library | Best For |
|-------|---------|----------|
| Zstandard | `zstandard` | Balance of speed/ratio |
| Brotli | `brotli` | Text/HTML compression |
| GZIP | `gzip` (stdlib) | Compatibility |
| BZIP2 | `bz2` (stdlib) | Good compression |
| LZMA/XZ | `lzma` (stdlib) | Best ratio, slowest |

### Development Tools
- **pytest** - Testing framework
- **black** - Code formatting
- **mypy** - Type checking

## 📁 Folder Structure
```
Dynamic-File-Compression-Utility/
│
├── input_files/ # Place test files here
│ ├── sample.txt # Example text file
│ ├── sample.json # Example JSON data
│ └── sample.csv # Example CSV data
│
├── compressed_files/ # Compressed output
│ ├── *.zst # Zstandard compressed
│ ├── *.gz # GZIP compressed
│ ├── *.xz # LZMA compressed
│ ├── *.br # Brotli compressed
│ └── *.dfc.json # Manifest files
├── outputs/ # Reports & statistics
│ ├── compression_report.json
│ └── compression_report.md
│
├── samples/ # For dictionary training
│ └── *.log # Sample log files
│
├── src/ # Source code
│ ├── init.py
│ ├── detector.py # File type detection
│ ├── strategy.py # Codec selection
│ ├── compress.py # Compression engine
│ ├── verify.py # Decompression & verification
│ ├── dict_train.py # Dictionary training
│ ├── archive.py # Folder archiving
│ ├── cli.py # Command-line interface
│ └── test_dfc.py # Unit tests
│
├── images/ # Screenshots for README
├── main.py # Entry point
├── requirements.txt # Dependencies
├── .gitignore # Git ignore rules
└── README.md # This file
```

## 💻 Installation

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/Dynamic-File-Compression-Utility.git
cd Dynamic-File-Compression-Utility

Step 2: Create Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

Step 4: Verify Installation
python main.py --help

## 🚀 How to Run
Quick Start - Automatic Demo
# Generate test files and run complete demo
python main.py --demo

# Just generate test files
python main.py --generate-only
Basic Commands

# Compress a file (auto mode - recommended)
python main.py compress input_files/sample.txt --mode auto

# Compress with specific mode
python main.py compress input_files/sample.txt --mode fast
python main.py compress input_files/sample.txt --mode balanced
python main.py compress input_files/sample.txt --mode max

# Decompress a file
python main.py decompress compressed_files/sample.zst

# Verify integrity
python main.py verify compressed_files/sample.zst.dfc.json

# Analyze file
python main.py info input_files/sample.txt
Advanced Commands

# Train compression dictionary
python main.py train-dict --glob "samples/*.log" --size 112640

# Test dictionary effectiveness
python main.py test-dict input_files/sample.txt outputs/zstd_dict_112640_1.dict

# Archive entire folder
python main.py archive input_files --output my_archive.tar.zst

# Extract archive
python main.py extract my_archive.tar.zst --output extracted_folder

📚 Usage Examples
Example 1: Compress a Text File
$ python main.py compress input_files/sample.txt --mode auto

📁 Compressing: sample.txt
   Mode: AUTO
   Codec: ZSTD (level 6)
   Original size: 25,500 bytes
   Compressed size: 3,456 bytes
   Compression ratio: 0.136 (86.4% saved)
   Time: 0.03 seconds
   ✅ Saved to: compressed_files/sample.zst
Example 2: Compress JSON Data
$ python main.py compress input_files/sample.json --mode max

📁 Compressing: sample.json
   Mode: MAX
   Codec: LZMA (level 9)
   Original size: 18,234 bytes
   Compressed size: 2,345 bytes
   Compression ratio: 0.129 (87.1% saved)
   Time: 0.15 seconds
   ✅ Saved to: compressed_files/sample.xz

Example 3: Decompress and Verify
$ python main.py decompress compressed_files/sample.zst

📂 Decompressing: sample.zst
   ✅ Decompressed to: decompressed_files/sample_restored.txt
$ python main.py verify compressed_files/sample.zst.dfc.json

🔍 Verifying: sample.zst
   ✅ Verification PASSED
   Hash match: a1b2c3d4e5f6...
   Size match: 25,500 bytes

Example 4: File Analysis
$ python main.py info input_files/sample.txt

📊 File Analysis: input_files/sample.txt
   Entropy: 4.52 (lower = more compressible)
   Text ratio: 98.5%
   Is binary: False
   Magic type: None
   MIME type: text/plain

📊 Sample Output
Compression Report (JSON)
json
{
  "source_file": "input_files/sample.txt",
  "compressed_file": "compressed_files/sample.zst",
  "codec": "zstd",
  "compression_level": 6,
  "original_size_bytes": 25500,
  "compressed_size_bytes": 3456,
  "compression_ratio": 0.1355,
  "space_saved_percent": 86.45,
  "compression_time_seconds": 0.03,
  "sha256_hash": "a1b2c3d4e5f67890..."
}
Performance Comparison
Mode	Codec	Level	Speed	Ratio	Best For
Fast	ZSTD	3	⚡⚡⚡	0.25	Quick compression
Balanced	ZSTD	6	⚡⚡	0.15	Default choice
Max	LZMA	9	⚡	0.08	Archival storage
Auto	Dynamic	Varies	⚡⚡	0.12	Intelligent choice
```

## 📚 Learning Outcomes
DSA Skills Gained
- ✅ Implemented greedy algorithms for codec selection
- ✅ Used hash maps for magic byte detection
- ✅ Applied streaming algorithms for large file processing
- ✅ Implemented priority queue logic for strategy selection
- ✅ Used binary trees (indirectly via codec internals)

System Design Skills
- ✅ Designed modular architecture with separation of concerns
- ✅ Implemented strategy pattern for codec selection
- ✅ Used factory pattern for compression creation
- ✅ Implemented manifest pattern for metadata
- ✅ Designed streaming pipeline for data processing

Python Skills
- ✅ Advanced file I/O with binary mode
- ✅ Type hints and dataclasses
- ✅ Context managers for resource management
- ✅ Argparse for CLI development
- ✅ Unit testing with pytest

## 🔮 Future Enhancements
- Parallel Compression - Multi-threaded chunk compression
- Encryption - AES-256 encryption for sensitive data
- Cloud Integration - Direct S3/GCS/Azure upload
- Delta Compression - For versioned backups
- ML Codec Prediction - Train model for optimal selection
- Web Interface - Flask/FastAPI REST API
- Deduplication - Content-defined chunking
- Real-time Monitoring - Progress bars and metrics
- GPU Acceleration - CUDA support for compression
- Plugin System - Custom codec plugins