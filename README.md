# Modern Image Compressor

A lightweight, high-performance image compression tool written in Python. Features both a responsive, modern desktop UI (Tkinter) and a headless compression engine for batch workflows.

## Features
- **Multi-Format Support**: Compress and convert between JPEG, PNG, and WebP.
- **Adaptive Optimization**: Smart palette quantization for PNGs, binary-search target file-size constraint, and high-efficiency WebP conversion.
- **EXIF Preservation**: Automatically retains orientation metadata while stripping bulky metadata tags.
- **Interactive UI**: Batch queue manager, progress tracking, quality & scaling sliders, and real-time reduction statistics.
- **Fallback CLI Mode**: Can be operated headless or via scripts.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Launch GUI
```bash
python main.py
```

### Run via CLI
```bash
python main.py --cli --input ./photos --output ./compressed --quality 75 --format WEBP
```

## Running Tests

```bash
python -m unittest discover tests
```
