#!/usr/bin/env python3
"""
scripts/train_real_model.py
──────────────────────────

Enhanced training script for real ransomware and clean file samples.

USAGE:
  # First, collect samples:
  python scripts/download_real_samples.py --bazaar-api-key YOUR_KEY

  # Then train the model:
  python scripts/train_real_model.py \
    --clean-dir data/real_samples/clean \
    --ransom-dir data/real_samples/ransomware

OPTIONS:
  --eval              - Evaluate an existing model
  --test-detection    - Test detection on sample files
  --save-report       - Save detailed training report
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Tuple, List, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.detector import extract_features, FEATURE_COLUMNS


def load_files_and_extract_features(
    directory: Path,
    label: int,
    max_files: Optional[int] = None,
    verbose: bool = True
) -> Tuple[List[list], List[int]]:
    """
    Load binary files from directory and extract ML features.
    
    Args:
        directory: Path to directory containing files
        label: Class label (0=clean, 1=ransomware)
        max_files: Max files to process (None = all)
        verbose: Print progress
    
    Returns:
        (features_list, labels_list)
    """
    X, y = [], []
    directory = Path(directory)
    
    if not directory.exists():
        print(f"  ✗ Directory not found: {directory}")
        return X, y
    
    files = list(directory.glob("*"))
    files = [f for f in files if f.is_file()]
    
    if max_files:
        files = files[:max_files]
    
    label_name = "clean" if label == 0 else "ransomware"
    print(f"\n[{label_name.upper()}] Processing {len(files)} files from {directory.name}/")
    
    skipped = 0
    errors = []
    
    for i, fpath in enumerate(files):
        try:
            data = fpath.read_bytes()
            
            # Skip empty files
            if len(data) == 0:
                skipped += 1
                continue
            
            # Skip huge files (likely system/media files)
            if len(data) > 100_000_000:  # 100 MB
                skipped += 1
                continue
            
            # Extract features
            features = extract_features(data, fpath.name)
            feature_vector = [features.get(col, 0) for col in FEATURE_COLUMNS]
            
            X.append(feature_vector)
            y.append(label)
            
            if verbose and (i + 1) % 50 == 0:
                print(f"  ✓ {i + 1}/{len(files)} files processed")
        
        except Exception as e:
            skipped += 1
            errors.append(f"{fpath.name}: {str(e)[:60]}")
    
    if verbose:
        print(f"  ✓ Successfully extracted {len(X)} features")
        if skipped > 0:
            print(f"  ⚠ Skipped {skipped} files")
        if errors and len(errors) <= 5:
            for err in errors[:5]:
                print(f"    - {err}")
    
    return X, y


def train_on_real_samples(
    clean_dir: str,
    ransom_dir: str,
    output_path: str,
    test_split: float = 0.2,
    save_report: bool = False
):
    """Train RandomForest on real labelled samples."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import (
            classification_report, confusion_matrix, roc_auc_score,
            precision_recall_curve, auc
        )
        import joblib
    except ImportError:
        print("ERROR: scikit-learn and joblib required")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("RANGARD Model Training on Real Samples")
    print("=" * 70)
    
    # Load samples
    X_clean, y_clean = load_files_and_extract_features(clean_dir, label=0, verbose=True)
    X_ransom, y_ransom = load_files_and_extract_features(ransom_dir, label=1, verbose=True)
    
    X = X_clean + X_ransom
    y = y_clean + y_ransom
    
    if len(X) < 10:
        print("\n✗ ERROR: Not enough samples for training (minimum 10 required)")
        print(f"  Found: {len(X)} samples")
        print(f"  Clean: {len(X_clean)}, Ransomware: {len(X_ransom)}")
        sys.exit(1)
    
    print(f"\n📊 Dataset Summary:")
    print(f"  Total samples:      {len(X)}")
    print(f"  Clean files:        {len(X_clean)} ({100*len(X_clean)/len(X):.1f}%)")
    print(f"  Ransomware files:   {len(X_ransom)} ({100*len(X_ransom)/len(X):.1f}%)")
    print(f"  Features per file:  {len(FEATURE_COLUMNS)}")
    
    # Split into train/test
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_split,
            random_state=42,
            stratify=y
        )
    except ValueError:
        print("⚠ Warning: Sample size too small for stratified split, using regular split")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_split,
            random_state=42
        )
    
    print(f"\n🔀 Train/Test Split:")
    print(f"  Training set:       {len(X_train)} samples")
    print(f"  Test set:           {len(X_test)} samples")
    
    # Train
    print(f"\n🤖 Training RandomForest...")
    print(f"  Estimators:         200 trees")
    print(f"  Max depth:          12")
    print(f"  Class weights:      Balanced")
    
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
        verbose=0
    )
    clf.fit(X_train, y_train)
    
    print(f"  ✓ Training complete")
    
    # Evaluate
    print(f"\n📈 Evaluation Metrics:")
    y_pred = clf.predict(X_test)
    y_pred_proba = clf.predict_proba(X_test)[:, 1]
    
    accuracy = clf.score(X_test, y_test)
    print(f"  Accuracy:           {accuracy:.1%}")
    
    try:
        auc_score = roc_auc_score(y_test, y_pred_proba)
        print(f"  ROC-AUC Score:      {auc_score:.4f}")
    except:
        pass
    
    print(f"\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["clean", "ransomware"]))
    
    print(f"Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TP (ransomware):    {cm[1,1]}")
    print(f"  FP (false alarm):   {cm[0,1]}")
    print(f"  TN (clean):         {cm[0,0]}")
    print(f"  FN (missed):        {cm[1,0]}")
    
    # Feature importances
    print(f"\n⭐ Top 10 Important Features:")
    importances = sorted(
        zip(FEATURE_COLUMNS, clf.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (feat, imp) in enumerate(importances[:10], 1):
        bar = "█" * int(imp * 40)
        print(f"  {i:2d}. {feat:<25} {imp:.4f}  {bar}")
    
    # Save model
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"\n💾 Model saved to: {output_path}")
    
    # Save report
    if save_report:
        report_path = output_path.replace(".joblib", "_report.json")
        report = {
            "accuracy": float(accuracy),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "clean_samples": len(X_clean),
            "ransomware_samples": len(X_ransom),
            "feature_importances": {name: float(imp) for name, imp in importances},
            "confusion_matrix": {
                "true_positives": int(cm[1,1]),
                "false_positives": int(cm[0,1]),
                "true_negatives": int(cm[0,0]),
                "false_negatives": int(cm[1,0])
            }
        }
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to: {report_path}")
    
    print("\n" + "=" * 70)
    print("✓ Model training complete!")
    print("=" * 70)


def evaluate_model(model_path: str):
    """Print detailed evaluation of an existing model."""
    try:
        import joblib
    except ImportError:
        print("ERROR: joblib required")
        sys.exit(1)
    
    if not os.path.exists(model_path):
        print(f"✗ Model not found: {model_path}")
        sys.exit(1)
    
    print(f"\n📊 Model Evaluation: {model_path}")
    clf = joblib.load(model_path)
    
    print(f"\nModel Details:")
    print(f"  Type:               {type(clf).__name__}")
    print(f"  Estimators:         {clf.n_estimators}")
    print(f"  Max Depth:          {clf.max_depth}")
    
    print(f"\n⭐ Feature Importances:")
    importances = sorted(
        zip(FEATURE_COLUMNS, clf.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (feat, imp) in enumerate(importances, 1):
        bar = "█" * int(imp * 50)
        print(f"  {i:2d}. {feat:<25} {imp:.4f}  {bar}")


def test_detection(model_path: str, test_file: str):
    """Test detection on a single file."""
    from app.ml.detector import RansomwareDetector
    
    if not os.path.exists(test_file):
        print(f"✗ File not found: {test_file}")
        sys.exit(1)
    
    detector = RansomwareDetector(model_path=model_path)
    
    with open(test_file, "rb") as f:
        file_data = f.read()
    
    result = detector.scan(file_data, os.path.basename(test_file))
    
    print(f"\n🔍 Scan Result: {os.path.basename(test_file)}")
    print(f"  Threat Level:       {result.threat_level.upper()}")
    print(f"  Confidence:         {result.confidence:.1%}")
    print(f"  File Size:          {result.features['file_size']:,} bytes")
    print(f"  Entropy:            {result.features['entropy_full']:.2f}/8.0")
    print(f"  Scan Time:          {result.scan_duration_ms}ms")
    
    if result.patterns:
        print(f"\n  Detected Patterns:")
        for pattern in result.patterns:
            print(f"    • {pattern}")


def main():
    parser = argparse.ArgumentParser(
        description="Train ransomware detector on REAL samples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train on real samples")
    train_parser.add_argument("--clean-dir", required=True,
                              help="Directory of clean files")
    train_parser.add_argument("--ransom-dir", required=True,
                              help="Directory of ransomware samples")
    train_parser.add_argument("--output", default="app/ml/model/ransomware_rf.joblib",
                              help="Output model path")
    train_parser.add_argument("--save-report", action="store_true",
                              help="Save JSON training report")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("eval", help="Evaluate model")
    eval_parser.add_argument("--model", default="app/ml/model/ransomware_rf.joblib",
                             help="Model path")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test on file")
    test_parser.add_argument("--model", default="app/ml/model/ransomware_rf.joblib",
                             help="Model path")
    test_parser.add_argument("--file", required=True,
                             help="File to scan")
    
    args = parser.parse_args()
    
    if not args.command:
        # Default to train if no command
        if not sys.argv[1:]:  # No args provided
            parser.print_help()
            sys.exit(0)
        
        # Try to infer from common arg patterns
        if "--clean-dir" in sys.argv or "--ransom-dir" in sys.argv:
            args.command = "train"
        else:
            parser.print_help()
            sys.exit(0)
    
    if args.command == "train":
        train_on_real_samples(
            args.clean_dir,
            args.ransom_dir,
            args.output,
            save_report=args.save_report
        )
    elif args.command == "eval":
        evaluate_model(args.model)
    elif args.command == "test":
        test_detection(args.model, args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
