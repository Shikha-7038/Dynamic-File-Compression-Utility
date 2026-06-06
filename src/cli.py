"""
Command-line interface for the compression utility
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compress import compress_file
from src.verify import decompress_file, verify_integrity, decompress_with_verify
from src.dict_train import train_dictionary, test_dictionary_effectiveness
from src.archive import compress_folder, decompress_archive

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="dfc",
        description="Dynamic File Compression Utility - Smart, cross-platform compression",
        epilog="Example: dfc compress myfile.txt --mode auto"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    compress_parser = subparsers.add_parser("compress", help="Compress a file")
    compress_parser.add_argument("input", help="Input file to compress")
    compress_parser.add_argument("--output", "-o", help="Output file path (optional)")
    compress_parser.add_argument("--mode", "-m", choices=["auto", "fast", "balanced", "max"], 
                                 default="auto", help="Compression mode (default: auto)")
    
    decompress_parser = subparsers.add_parser("decompress", help="Decompress a file")
    decompress_parser.add_argument("input", help="Compressed file to decompress")
    decompress_parser.add_argument("--output", "-o", help="Output file path (optional)")
    
    verify_parser = subparsers.add_parser("verify", help="Verify compressed file integrity")
    verify_parser.add_argument("manifest", help="Path to .dfc.json manifest file")
    
    train_parser = subparsers.add_parser("train-dict", help="Train compression dictionary")
    train_parser.add_argument("--glob", "-g", default="samples/*.log", 
                             help="Glob pattern for training files (default: samples/*.log)")
    train_parser.add_argument("--size", "-s", type=int, default=112*1024,
                             help="Dictionary size in bytes (default: 114688)")
    
    test_dict_parser = subparsers.add_parser("test-dict", help="Test dictionary effectiveness")
    test_dict_parser.add_argument("file", help="File to test compression on")
    test_dict_parser.add_argument("dictionary", help="Path to dictionary file")
    
    archive_parser = subparsers.add_parser("archive", help="Compress entire folder")
    archive_parser.add_argument("folder", help="Folder to archive")
    archive_parser.add_argument("--output", "-o", help="Output archive path (optional)")
    archive_parser.add_argument("--level", "-l", type=int, default=8,
                               choices=range(1, 23), help="Compression level 1-22 (default: 8)")
    
    extract_parser = subparsers.add_parser("extract", help="Extract archived folder")
    extract_parser.add_argument("archive", help="Archive file (.tar.zst)")
    extract_parser.add_argument("--output", "-o", help="Output folder (optional)")
    
    info_parser = subparsers.add_parser("info", help="Show file compression info")
    info_parser.add_argument("file", help="File to analyze")
    
    args = parser.parse_args()
    
    if args.command == "compress":
        try:
            manifest = compress_file(args.input, args.output, args.mode)
            print(f"\n✨ Compression complete!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "decompress":
        try:
            decompress_with_verify(args.input, args.output)
            print(f"\n✨ Decompression complete!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "verify":
        try:
            success = verify_integrity(args.manifest)
            sys.exit(0 if success else 1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "train-dict":
        try:
            dict_id = train_dictionary(args.glob, args.size)
            if dict_id:
                print(f"\n✨ Dictionary training complete!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "test-dict":
        try:
            test_dictionary_effectiveness(args.file, args.dictionary)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "archive":
        try:
            output = compress_folder(args.folder, args.output, args.level)
            print(f"\n✨ Archive complete!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "extract":
        try:
            output = decompress_archive(args.archive, args.output)
            print(f"\n✨ Extraction complete!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "info":
        try:
            from src.detector import get_sample_stats
            stats = get_sample_stats(args.file)
            print(f"\n📊 File Analysis: {args.file}")
            print(f"   Entropy: {stats['entropy']} (lower = more compressible)")
            print(f"   Text ratio: {stats['text_ratio']:.1%}")
            print(f"   Is binary: {stats['is_binary']}")
            print(f"   Magic type: {stats.get('magic_type', 'Unknown')}")
            print(f"   MIME type: {stats.get('mime_type', 'Unknown')}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()