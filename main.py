#!/usr/bin/env python3
"""
Dynamic File Compression Utility - Main Entry Point with Auto-Generation
"""

import sys
import os
import random
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.cli import main as cli_main

def generate_test_data():
    """Automatically generate test files for compression"""
    
    print("\n🔧 AUTO-GENERATING TEST DATA...")
    
    Path("input_files").mkdir(exist_ok=True)
    Path("compressed_files").mkdir(exist_ok=True)
    Path("decompressed_files").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)
    Path("samples").mkdir(exist_ok=True)
    
    # 1. Text file
    text_content = []
    for i in range(500):
        text_content.append(f"Line {i:04d}: This is repeated text that will compress very well")
    Path("input_files/sample.txt").write_text("\n".join(text_content))
    print(f"   ✅ Generated: input_files/sample.txt ({Path('input_files/sample.txt').stat().st_size:,} bytes)")
    
    # 2. JSON file
    json_data = {"records": []}
    for i in range(200):
        json_data["records"].append({
            "id": i,
            "name": f"item_{i}",
            "value": i * 10,
            "category": f"cat_{i % 5}"
        })
    Path("input_files/sample.json").write_text(json.dumps(json_data, indent=2))
    print(f"   ✅ Generated: input_files/sample.json ({Path('input_files/sample.json').stat().st_size:,} bytes)")
    
    # 3. CSV file
    csv_content = "id,name,value,category\n"
    for i in range(300):
        csv_content += f"{i},item_{i},{i * 10},cat_{i % 5}\n"
    Path("input_files/sample.csv").write_text(csv_content)
    print(f"   ✅ Generated: input_files/sample.csv ({Path('input_files/sample.csv').stat().st_size:,} bytes)")
    
    # 4. Log file for dictionary training
    log_content = []
    levels = ["ERROR", "WARNING", "INFO", "DEBUG"]
    messages = ["Connection failed", "User logged in", "Timeout occurred", "Cache miss"]
    for i in range(1000):
        log_line = f"2024-01-01 10:{(i%60):02d}:{(i%60):02d} - {levels[i%4]} - {messages[i%4]} - ID:{i:08d}\n"
        log_content.append(log_line)
    Path("samples/app.log").write_text("".join(log_content))
    print(f"   ✅ Generated: samples/app.log ({Path('samples/app.log').stat().st_size:,} bytes)")
    
    # 5. Binary file
    binary_content = bytes([random.randint(0, 255) for _ in range(50000)])
    Path("input_files/random.bin").write_bytes(binary_content)
    print(f"   ✅ Generated: input_files/random.bin ({Path('input_files/random.bin').stat().st_size:,} bytes)")
    
    # 6. Repetitive file (highly compressible)
    repetitive_content = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" * 1000
    Path("input_files/repetitive.txt").write_text(repetitive_content)
    print(f"   ✅ Generated: input_files/repetitive.txt ({Path('input_files/repetitive.txt').stat().st_size:,} bytes)")
    
    print("\n✨ Auto-generation complete! 6 test files created.\n")
    return True

def run_auto_demo():
    """Run complete demonstration automatically"""
    
    print("=" * 70)
    print("🚀 DYNAMIC FILE COMPRESSION UTILITY - AUTO DEMO MODE")
    print("=" * 70)
    
    generate_test_data()
    
    print("\n📊 STEP 1: ANALYZING FILES")
    print("-" * 50)
    
    for file_path in Path("input_files").glob("*"):
        print(f"\n🔍 Analyzing: {file_path.name}")
        os.system(f'python main.py info "{file_path}"')
    
    print("\n\n📦 STEP 2: COMPRESSING FILES")
    print("-" * 50)
    
    test_cases = [
        ("input_files/sample.txt", "auto"),
        ("input_files/sample.json", "balanced"),
        ("input_files/sample.csv", "max"),
        ("input_files/repetitive.txt", "auto"),
    ]
    
    for file_path, mode in test_cases:
        print(f"\n🔄 Compressing: {Path(file_path).name} (mode: {mode})")
        os.system(f'python main.py compress "{file_path}" --mode {mode}')
    
    print("\n\n✅ STEP 3: VERIFYING INTEGRITY")
    print("-" * 50)
    
    for manifest in Path("compressed_files").glob("*.dfc.json"):
        print(f"\n🔐 Verifying: {manifest.name}")
        os.system(f'python main.py verify "{manifest}"')
    
    print("\n\n📁 FINAL OUTPUT LOCATIONS")
    print("=" * 60)
    
    folders = {
        "Compressed files": "compressed_files",
        "Decompressed files": "decompressed_files",
        "Reports": "outputs",
        "Original files": "input_files",
        "Samples for training": "samples"
    }
    
    for name, folder in folders.items():
        count = len(list(Path(folder).glob("*")))
        print(f"📂 {name}: {folder}/ ({count} files)")
    
    print("\n" + "=" * 70)
    print("✨ DEMO COMPLETE! Check the folders above for outputs.")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_auto_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "--generate-only":
        generate_test_data()
    else:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║     Dynamic File Compression Utility - Smart Compressor v1.0      ║
║                                                                   ║
║  🚀 QUICK START:                                                  ║
║     python main.py --demo        (Run complete auto-demo)         ║
║     python main.py --generate-only (Generate test files only)     ║
║                                                                   ║
║  📚 MANUAL MODE:                                                  ║
║     python main.py compress input_files/sample.txt                ║
║     python main.py decompress compressed_files/sample.zst         ║
║     python main.py info input_files/sample.txt                    ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
        if len(sys.argv) == 1:
            cli_main()
        else:
            cli_main()