#!/usr/bin/env python3
"""
scripts/train_model.py
───────────────────────
Train (or retrain) the ransomware detection model.

USAGE:
  # Demo mode — synthetic data, good for development:
  python scripts/train_model.py --mode demo

  # Production mode — point to a directory of labelled samples:
  python scripts/train_model.py --mode real \
    --clean-dir  /data/clean_files \
    --ransom-dir /data/ransomware_samples

  # Evaluate an existing model:
  python scripts/train_model.py --mode eval

WHERE TO GET REAL TRAINING DATA:
  - MalwareBazaar: https://bazaar.abuse.ch/browse/ (free, requires account)
  - VirusTotal:    https://www.virustotal.com       (API access)
  - TheZoo:        https://github.com/ytisf/theZoo  (educational, handle with care)
  - Clean samples: collect from your own system (documents, executables, images)

IMPORTANT: Handle malware samples with extreme care.
  - Always work in an isolated VM or container
  - Never execute samples directly
  - Keep samples in an encrypted, air-gapped environment
"""

import argparse
import os
import sys

# Ensure we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def train_demo(output_path: str):
    """Train on synthetic data — useful for development and CI."""
    from app.ml.detector import train_demo_model
    train_demo_model(output_path)


def train_real(clean_dir: str, ransom_dir: str, output_path: str):
    """
    Train on real labelled files.
    clean_dir:  directory of clean files (label = 0)
    ransom_dir: directory of ransomware samples (label = 1)
    """
    import joblib
    import numpy as np
    from pathlib import Path
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    from app.ml.detector import extract_features, FEATURE_COLUMNS

    print("Extracting features from files…")
    X, y = [], []

    def process_dir(directory, label):
        path = Path(directory)
        files = list(path.rglob("*"))
        files = [f for f in files if f.is_file()]
        print(f"  {'Clean' if label == 0 else 'Ransomware'}: {len(files)} files in {directory}")
        for fpath in files:
            try:
                data = fpath.read_bytes()
                if len(data) == 0:
                    continue
                feats = extract_features(data, fpath.name)
                X.append([feats.get(col, 0) for col in FEATURE_COLUMNS])
                y.append(label)
            except Exception as e:
                print(f"    Skipping {fpath.name}: {e}")

    process_dir(clean_dir,  label=0)
    process_dir(ransom_dir, label=1)

    if len(X) < 10:
        print("Not enough samples — need at least 10 total.")
        sys.exit(1)

    print(f"\nTotal samples: {len(X)} ({sum(y)} ransomware, {len(y)-sum(y)} clean)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTraining RandomForest…")
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    print("\nEvaluation on held-out test set:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=["clean", "ransomware"]))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"\nModel saved to {output_path}")


def evaluate(model_path: str):
    """Print feature importances for an existing model."""
    import joblib
    from app.ml.detector import FEATURE_COLUMNS

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        sys.exit(1)

    clf = joblib.load(model_path)
    importances = sorted(
        zip(FEATURE_COLUMNS, clf.feature_importances_),
        key=lambda x: x[1], reverse=True,
    )

    print("\nFeature importances:")
    print("-" * 40)
    for feat, imp in importances:
        bar = "█" * int(imp * 50)
        print(f"  {feat:<25} {imp:.4f}  {bar}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the RANGARD ML model")
    parser.add_argument("--mode", choices=["demo", "real", "eval"], default="demo")
    parser.add_argument("--clean-dir",  default="data/clean")
    parser.add_argument("--ransom-dir", default="data/ransomware")
    parser.add_argument("--output",     default="app/ml/model/ransomware_rf.joblib")
    args = parser.parse_args()

    if args.mode == "demo":
        train_demo(args.output)
    elif args.mode == "real":
        train_real(args.clean_dir, args.ransom_dir, args.output)
    elif args.mode == "eval":
        evaluate(args.output)
