import sys
import os
import argparse
from compressor.engine import ImageCompressor

def run_cli(args):
    compressor = ImageCompressor()
    in_path = os.path.abspath(args.input)
    out_dir = os.path.abspath(args.output)
    os.makedirs(out_dir, exist_ok=True)

    files = []
    if os.path.isdir(in_path):
        exts = compressor.get_supported_extensions()
        for root, _, filenames in os.walk(in_path):
            for fn in filenames:
                if any(fn.lower().endswith(e) for e in exts):
                    files.append(os.path.join(root, fn))
    elif os.path.isfile(in_path):
        files.append(in_path)
    else:
        print(f"Error: Input path '{in_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(files)} files...")
    for f in files:
        base, orig_ext = os.path.splitext(os.path.basename(f))
        ext = f".{args.format.lower()}" if args.format and args.format.upper() != "ORIGINAL" else orig_ext
        dest = os.path.join(out_dir, f"{base}_opt{ext}")
        result = compressor.compress_single(
            input_path=f,
            output_path=dest,
            quality=args.quality,
            max_dimension=args.max_dim,
            target_format=None if args.format == "ORIGINAL" else args.format,
            target_kb=args.target_kb
        )
        if result.success:
            print(f"[OK] {os.path.basename(f)} -> {result.compressed_bytes/1024:.1f}KB (-{result.saved_percent}%)")
        else:
            print(f"[ERROR] {os.path.basename(f)}: {result.error_message}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Image Compressor & Converter")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode without GUI")
    parser.add_argument("-i", "--input", type="str", help="Input file or directory")
    parser.add_argument("-o", "--output", type="str", default="./output", help="Output directory")
    parser.add_argument("-q", "--quality", type=int, default=80, help="Quality level 1-100")
    parser.add_argument("--max-dim", type=int, default=None, help="Max dimension for resize")
    parser.add_argument("-f", "--format", type="str", default="ORIGINAL", help="Format: ORIGINAL, JPEG, WEBP, PNG")
    parser.add_argument("--target-kb", type=int, default=0, help="Target file size in KB")

    args = parser.parse_args()

    if args.cli or args.input:
        if not args.input:
            parser.error("--input is required in CLI mode.")
        run_cli(args)
    else:
        from compressor.ui import CompressorApp
        app = CompressorApp()
        app.mainloop()

if __name__ == "__main__":
    main()
