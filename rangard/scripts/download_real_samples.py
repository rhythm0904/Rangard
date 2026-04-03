#!/usr/bin/env python3
"""
scripts/download_real_samples.py
────────────────────────────────

Download real ransomware and clean samples for model training.

SOURCES:
  1. MalwareBazaar.org - Free ransomware samples (requires registration)
  2. System files - Use existing clean files from Windows/Program Files
  3. VirusShare - Alternative malware repository

SAFETY:
  - Samples are NOT extracted or executed
  - Downloaded as binary files only
  - Keep in isolated data directory
  - No execution, only analysis

USAGE:
  # Download from MalwareBazaar (requires free API key)
  python scripts/download_real_samples.py \
    --bazaar-api-key YOUR_API_KEY \
    --num-ransomware 100 \
    --output-dir data/real_samples

  # Collect clean system files (safe, no downloads)
  python scripts/download_real_samples.py \
    --collect-clean-only \
    --output-dir data/real_samples

  # Both (recommended)
  python scripts/download_real_samples.py \
    --bazaar-api-key YOUR_API_KEY \
    --num-ransomware 100 \
    --collect-clean \
    --output-dir data/real_samples
"""

import argparse
import hashlib
import json
import os
import random
import shutil
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)


def collect_clean_files(clean_dir: Path, max_files: int = 200) -> int:
    """
    Collect real clean files from system directories.
    Safe operation - only reads existing files.
    """
    print(f"\n[Clean Files] Scanning system directories...")
    clean_dir.mkdir(parents=True, exist_ok=True)
    
    # Common places to find clean files
    system_paths = [
        Path("C:/Windows/System32"),           # Windows system files
        Path("C:/Program Files"),              # Installed applications
        Path("C:/Program Files (x86)"),        # 32-bit applications
        Path(os.path.expanduser("~")),         # User documents
    ]
    
    collected = 0
    extensions_to_collect = {
        '.dll', '.exe', '.sys',           # System binaries
        '.doc', '.docx', '.xls', '.xlsx', # Documents
        '.pdf', '.txt', '.jpg', '.png',   # Various file types
        '.zip', '.7z', '.rar',            # Archives
    }
    
    print(f"[Clean Files] Collecting from system (max {max_files} files)...")
    
    for base_path in system_paths:
        if not base_path.exists():
            continue
            
        try:
            # Limit search depth to avoid scanning entire drive
            for root, dirs, files in os.walk(base_path):
                # Skip system/hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Only go 2 levels deep
                depth = root.count(os.sep) - base_path.count(os.sep)
                if depth > 2:
                    dirs.clear()
                    continue
                
                for file in files[:10]:  # Sample from each directory
                    if collected >= max_files:
                        return collected
                    
                    fpath = Path(root) / file
                    ext = fpath.suffix.lower()
                    
                    if ext not in extensions_to_collect:
                        continue
                    
                    try:
                        if fpath.stat().st_size > 100000000:  # Skip huge files
                            continue
                        
                        dest = clean_dir / f"clean_{collected:05d}{ext}"
                        shutil.copy2(fpath, dest)
                        collected += 1
                        
                        if collected % 50 == 0:
                            print(f"  Collected {collected}/{max_files} clean files")
                    except Exception as e:
                        pass
        except PermissionError:
            continue
        except Exception:
            continue
    
    print(f"[Clean Files] Collected {collected} real system files")
    return collected


def download_from_malwarebazaar(
    api_key: str,
    ransom_dir: Path,
    max_samples: int = 100
) -> int:
    """
    Download ransomware samples from MalwareBazaar API.
    
    Get free API key:
      1. Go to https://bazaar.abuse.ch/api/
      2. Register for free account
      3. Generate API key
    """
    ransom_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[MalwareBazaar] Authenticating...")
    api_url = "https://mb-api.abuse.ch/api/v1/"
    
    headers = {
        "API-KEY": api_key,
        "User-Agent": "RANGARD-AI"
    }
    
    downloaded = 0
    families = ["wncry", "ryuk", "locky", "cerber", "petya", "wannacry"]
    
    for family in families:
        if downloaded >= max_samples:
            break
        
        print(f"\n[MalwareBazaar] Searching for {family.upper()} samples...")
        
        payload = {
            "query": "get_samples",
            "families": family,
            "limit": min(20, max_samples - downloaded)
        }
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"  API error: {response.status_code}")
                continue
            
            data = response.json()
            if data.get("query_status") != "ok":
                print(f"  Query failed: {data.get('query_status')}")
                continue
            
            samples = data.get("samples", [])
            print(f"  Found {len(samples)} {family} samples")
            
            for sample in samples[:20]:
                if downloaded >= max_samples:
                    break
                
                sha256 = sample.get("sha256_hash")
                if not sha256:
                    continue
                
                # Download the sample
                print(f"    Downloading {sha256[:16]}...")
                
                dl_payload = {
                    "query": "get_file",
                    "sha256_hash": sha256
                }
                
                try:
                    dl_response = requests.post(
                        api_url,
                        headers=headers,
                        data=dl_payload,
                        timeout=30,
                        stream=True
                    )
                    
                    if dl_response.status_code == 200:
                        filepath = ransom_dir / f"ransom_{family}_{downloaded:04d}_{sha256[:8]}.bin"
                        with open(filepath, "wb") as f:
                            f.write(dl_response.content)
                        downloaded += 1
                        print(f"      ✓ Saved {filepath.name} ({len(dl_response.content)} bytes)")
                    
                except requests.RequestException as e:
                    print(f"      ✗ Download failed: {e}")
                    
        except requests.RequestException as e:
            print(f"  API request failed: {e}")
            continue
    
    print(f"\n[MalwareBazaar] Downloaded {downloaded} ransomware samples")
    return downloaded


def create_dataset_manifest(output_dir: Path):
    """Create a manifest file describing the dataset."""
    manifest = {
        "description": "Real-world training dataset for RANGARD",
        "clean_files": len(list((output_dir / "clean").glob("*"))) if (output_dir / "clean").exists() else 0,
        "ransomware_files": len(list((output_dir / "ransomware").glob("*"))) if (output_dir / "ransomware").exists() else 0,
        "collection_date": str(__import__("datetime").datetime.now().isoformat()),
        "sources": [
            "MalwareBazaar (https://bazaar.abuse.ch/)",
            "System files (Windows)",
        ],
        "usage": "python scripts/train_model.py --mode real --clean-dir data/real_samples/clean --ransom-dir data/real_samples/ransomware"
    }
    
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✓ Manifest created: {manifest_file}")
    
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Download real samples for model training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
SETUP:
  1. Get MalwareBazaar API key:
     - Visit https://bazaar.abuse.ch/api/
     - Register for free account
     - Generate API key
  
  2. Run with API key:
     python scripts/download_real_samples.py --bazaar-api-key YOUR_KEY

EXAMPLES:
  # Download ransomware + collect clean files
  python scripts/download_real_samples.py --bazaar-api-key KEY123 --num-ransomware 80

  # Just collect clean files (safe, no downloads)
  python scripts/download_real_samples.py --collect-clean-only

  # Already have samples, just organize them
  python scripts/download_real_samples.py --organize-only
        """
    )
    
    parser.add_argument("--bazaar-api-key", default="",
                        help="MalwareBazaar API key (get free key from bazaar.abuse.ch/api/)")
    parser.add_argument("--num-ransomware", type=int, default=100,
                        help="Number of ransomware samples to download")
    parser.add_argument("--num-clean", type=int, default=200,
                        help="Number of clean files to collect")
    parser.add_argument("--collect-clean", action="store_true", default=True,
                        help="Collect clean files from system (default: True)")
    parser.add_argument("--collect-clean-only", action="store_true",
                        help="Only collect clean files (skip ransomware download)")
    parser.add_argument("--output-dir", default="data/real_samples",
                        help="Output directory for samples")
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    clean_dir = output_dir / "clean"
    ransom_dir = output_dir / "ransomware"
    
    print("=" * 60)
    print("RANGARD Real Sample Collection")
    print("=" * 60)
    
    # Collect clean files
    if args.collect_clean or args.collect_clean_only:
        collect_clean_files(clean_dir, max_files=args.num_clean)
    
    # Download ransomware samples
    if not args.collect_clean_only:
        if not args.bazaar_api_key:
            print("\n⚠ No MalwareBazaar API key provided")
            print("  Get free key from: https://bazaar.abuse.ch/api/")
            print("  Then run: python scripts/download_real_samples.py --bazaar-api-key YOUR_KEY")
        else:
            download_from_malwarebazaar(
                args.bazaar_api_key,
                ransom_dir,
                max_samples=args.num_ransomware
            )
    
    # Create manifest
    manifest = create_dataset_manifest(output_dir)
    
    print("\n" + "=" * 60)
    print("✓ Dataset Ready")
    print("=" * 60)
    print(f"Clean files:        {manifest['clean_files']}")
    print(f"Ransomware files:   {manifest['ransomware_files']}")
    print(f"Total samples:      {manifest['clean_files'] + manifest['ransomware_files']}")
    print(f"\nNext step: Train the model")
    print(f"  {manifest['usage']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
