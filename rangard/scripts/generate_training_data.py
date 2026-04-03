#!/usr/bin/env python3
"""
scripts/generate_training_data.py
─────────────────────────────────

Generate realistic synthetic training data for the ransomware detector.
This creates sample data files that mimic real file characteristics.

USAGE:
  python scripts/generate_training_data.py --output-dir data/training_samples

This generates:
  data/training_samples/clean/     - synthetic clean files
  data/training_samples/ransomware/ - synthetic ransomware-like files

The files are NOT actual malware — they're benign data with feature patterns
that match real ransomware behavior for training purposes.
"""

import argparse
import os
import random
import string
import zlib
from pathlib import Path


def create_clean_file(path: Path, size_kb: int = 50, file_type: str = "doc"):
    """
    Create a synthetic clean file with realistic characteristics.
    - Low entropy (text, images, executables)
    - Readable content
    - Normal structure
    """
    size = size_kb * 1024
    
    if file_type == "pe":
        # Minimal PE executable header (safe)
        data = b"MZ" + b"\x00" * 60 + b"\x40\x00" + b"\x00" * 100  # Minimal PE
        data += b"\x00" * (size - len(data))
        data = b"Microsoft Visual C++ Runtime Library\n" * 20
        
    elif file_type == "text":
        # Document-like content (low entropy)
        lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        data = (lorem * (size // len(lorem))).encode()
        
    elif file_type == "image":
        # PNG-like structure (some entropy, but structured)
        data = b"\x89PNG\r\n\x1a\n"  # PNG header
        data += bytes([random.randint(0, 255) for _ in range(size - len(data))])
        
    else:  # generic text
        # Random but readable text
        chars = string.ascii_letters + string.digits + " \n" * 5
        data = ''.join(random.choices(chars, k=size)).encode()
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def create_ransomware_file(path: Path, size_kb: int = 50):
    """
    Create a synthetic ransomware-like file with realistic characteristics:
    - High entropy (encrypted data)
    - Some suspicious strings
    - Suspicious structure
    - Potentially binary content with PE headers
    """
    size = size_kb * 1024
    data = bytearray()
    
    # Some files are PE executables
    if random.random() < 0.4:
        data.extend(b"MZ" + b"\x00" * 60 + b"\x40\x00")  # PE header
        data.extend(bytes([random.randint(0, 255) for _ in range(256)]))
    
    # Add encrypted-like (high entropy) content
    encrypted_portion = bytes([random.randint(0, 255) for _ in range(size - len(data) - 1000)])
    data.extend(encrypted_portion)
    
    # Add some suspicious strings (but harmless)
    suspicious_strings = [
        b"your files have been encrypted",
        b"send bitcoin to recover",
        b"readme.txt.encrypted",
        b"ransom note content",
        b"decrypt your files",
        b".onion",
        b"pay within 24 hours",
        b"wncry_wannacry",
    ]
    
    for string in random.sample(suspicious_strings, k=random.randint(1, 3)):
        data.extend(string + b"\x00" * random.randint(10, 50))
    
    # Fill the rest with random bytes (simulates encryption)
    while len(data) < size:
        data.extend(bytes([random.randint(0, 255) for _ in range(min(100, size - len(data)))]))
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(bytes(data[:size]))


def generate_dataset(output_dir: str, num_clean: int = 100, num_ransom: int = 80):
    """Generate a complete training dataset."""
    output_path = Path(output_dir)
    clean_dir = output_path / "clean"
    ransom_dir = output_path / "ransomware"
    
    print(f"Generating {num_clean} clean files...")
    file_types = ["text", "pe", "image", "generic"]
    for i in range(num_clean):
        file_type = file_types[i % len(file_types)]
        ext = {"text": ".docx", "pe": ".exe", "image": ".png", "generic": ".bin"}[file_type]
        filename = f"clean_{i:04d}{ext}"
        size = random.randint(10, 500)  # 10-500 KB
        create_clean_file(clean_dir / filename, size_kb=size, file_type=file_type)
        if (i + 1) % 20 == 0:
            print(f"  Created {i + 1}/{num_clean}")
    
    print(f"\nGenerating {num_ransom} ransomware-like files...")
    for i in range(num_ransom):
        filename = f"ransom_{i:04d}.bin"
        size = random.randint(50, 800)  # 50-800 KB
        create_ransomware_file(ransom_dir / filename, size_kb=size)
        if (i + 1) % 20 == 0:
            print(f"  Created {i + 1}/{num_ransom}")
    
    print(f"\n✓ Dataset generated at {output_dir}")
    print(f"  Clean files:     {clean_dir} ({num_clean} files)")
    print(f"  Ransomware:      {ransom_dir} ({num_ransom} files)")
    print(f"\nNext step: Train the model with:")
    print(f"  python scripts/train_model.py --mode real \\")
    print(f"    --clean-dir data/training_samples/clean \\")
    print(f"    --ransom-dir data/training_samples/ransomware")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate realistic synthetic training data")
    parser.add_argument("--output-dir", default="data/training_samples",
                        help="Output directory for generated files")
    parser.add_argument("--num-clean", type=int, default=100,
                        help="Number of clean sample files to generate")
    parser.add_argument("--num-ransom", type=int, default=80,
                        help="Number of ransomware sample files to generate")
    args = parser.parse_args()
    
    generate_dataset(args.output_dir, args.num_clean, args.num_ransom)
