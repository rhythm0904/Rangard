"""
app/ml/detector.py
──────────────────
The AI ransomware detection engine.

HOW IT WORKS (beginner explanation):
─────────────────────────────────────
Traditional antivirus looks for known "signatures" — like a list of known
criminals' fingerprints.  It misses new ransomware immediately.

We use BEHAVIOURAL ANALYSIS instead:
  • We extract ~30 features from a file (entropy, file type, PE headers, etc.)
  • A trained ML model scores those features: "how ransomware-like is this?"
  • This catches UNKNOWN ransomware that behaves like known ransomware

The model is a RandomForest classifier trained on a mix of:
  - Clean files (documents, images, executables)
  - Known ransomware samples (WannaCry, Ryuk, LockBit families)

In production you would retrain this model regularly with new samples.
For development we include a "demo mode" that returns realistic scores
without needing a real trained model file.
"""

import hashlib
import math
import os
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

# We import sklearn lazily so the app starts even without a saved model
try:
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    sha256: str
    threat_level: str          # clean | low | medium | high | critical
    confidence: float          # 0.0 → 1.0
    features: dict             # raw extracted features
    patterns: list[str]        # human-readable findings
    scan_duration_ms: int
    mime_type: str = "unknown"
    error: Optional[str] = None


# ── Feature extraction ────────────────────────────────────────────────────────

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _entropy(data: bytes) -> float:
    """
    Shannon entropy measures randomness.
    Plain text: ~3-4 bits.  Encrypted/compressed data: ~7-8 bits.
    Ransomware encrypts files → very high entropy (near 8.0).
    """
    if not data:
        return 0.0
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    length = len(data)
    return -sum(
        (count / length) * math.log2(count / length)
        for count in freq.values()
        if count > 0
    )


def _byte_histogram(data: bytes) -> list[float]:
    """256-bin histogram of byte values, normalised to [0,1]."""
    hist = [0] * 256
    for b in data:
        hist[b] += 1
    total = len(data) or 1
    return [c / total for c in hist]


def _is_pe_file(data: bytes) -> bool:
    """PE = Windows executable (EXE, DLL). Starts with 'MZ'."""
    return len(data) >= 2 and data[:2] == b"MZ"


def _pe_features(data: bytes) -> dict:
    """Extract basic PE header features without pefile library."""
    features = {
        "pe_file": False,
        "pe_section_count": 0,
        "pe_suspicious_imports": False,
        "pe_has_overlay": False,
    }
    if not _is_pe_file(data):
        return features

    features["pe_file"] = True
    try:
        # e_lfanew offset points to the PE header
        if len(data) < 64:
            return features
        e_lfanew = struct.unpack_from("<I", data, 60)[0]
        if e_lfanew + 6 > len(data):
            return features

        num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
        features["pe_section_count"] = num_sections

        # High section count is suspicious (>8 unusual for legit software)
        if num_sections > 8:
            features["pe_suspicious_imports"] = True
    except Exception:
        pass

    return features


SUSPICIOUS_EXTENSIONS = {
    # Ransomware commonly targets these
    ".doc", ".docx", ".xls", ".xlsx", ".pdf", ".jpg", ".jpeg",
    ".png", ".mp4", ".zip", ".sql", ".mdb", ".db",
}

RANSOMWARE_STRINGS = [
    b"your files have been encrypted",
    b"bitcoin",
    b"ransom",
    b"decrypt",
    b"tor browser",
    b".onion",
    b"pay within",
    b"readme.txt",   # classic ransom note filename reference
    b"wncry",        # WannaCry
    b"locky",
    b"ryuk",
]


def extract_features(file_data: bytes, filename: str) -> dict:
    """
    Extract all features from raw file bytes.
    Returns a flat dict used both for ML prediction and for display.
    """
    ext = Path(filename).suffix.lower()
    entropy = _entropy(file_data)
    hist = _byte_histogram(file_data[:4096])  # first 4KB only (fast)
    pe = _pe_features(file_data)

    # Count how many ransomware strings appear in the file (case-insensitive)
    file_lower = file_data[:8192].lower()
    ransom_string_hits = sum(
        1 for s in RANSOMWARE_STRINGS if s in file_lower
    )

    # Ratio of printable ASCII — ransomware dropper has low printable ratio
    printable = sum(1 for b in file_data[:2048] if 32 <= b <= 126)
    printable_ratio = printable / min(len(file_data), 2048) if file_data else 0

    return {
        # Entropy features
        "entropy_full": entropy,
        "entropy_header": _entropy(file_data[:512]),
        "entropy_footer": _entropy(file_data[-512:]) if len(file_data) >= 512 else 0,
        "high_entropy": int(entropy > 7.2),

        # File type
        "is_pe": int(pe["pe_file"]),
        "is_suspicious_ext": int(ext in SUSPICIOUS_EXTENSIONS),
        "extension": ext,

        # PE-specific
        "pe_section_count": pe["pe_section_count"],
        "pe_suspicious": int(pe["pe_suspicious_imports"]),

        # Content analysis
        "ransom_string_hits": ransom_string_hits,
        "printable_ratio": printable_ratio,
        "file_size": len(file_data),

        # Byte distribution — low variance = encrypted (uniform distribution)
        "byte_variance": float(np.var(hist)),
        "byte_mean":     float(np.mean(hist)),
        "null_byte_ratio": hist[0],            # high null = padding/encrypted
    }


# ── ML Model wrapper ──────────────────────────────────────────────────────────

FEATURE_COLUMNS = [
    "entropy_full", "entropy_header", "entropy_footer", "high_entropy",
    "is_pe", "is_suspicious_ext", "pe_section_count", "pe_suspicious",
    "ransom_string_hits", "printable_ratio", "file_size",
    "byte_variance", "byte_mean", "null_byte_ratio",
]


def _features_to_vector(features: dict) -> np.ndarray:
    """Convert feature dict to numpy array in the correct order."""
    return np.array([[features.get(col, 0) for col in FEATURE_COLUMNS]])


class RansomwareDetector:
    """
    Main detection class.  Usage:
        detector = RansomwareDetector()
        result = await detector.scan(file_bytes, "invoice.docx", "user@email.com")
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "model", "ransomware_rf.joblib"
        )
        self._load_model()

    def _load_model(self):
        """Try to load a saved model; fall back to rule-based scoring."""
        if SKLEARN_AVAILABLE and os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"[ML] Loaded trained model from {self.model_path}")
                return
            except Exception as e:
                print(f"[ML] Could not load model: {e} — using rule-based fallback")
        print("[ML] No trained model found — using rule-based heuristics (good for development)")

    def _rule_based_score(self, features: dict) -> float:
        """
        Heuristic scoring when no ML model is available.
        Returns a probability-like score in [0, 1].
        This is surprisingly effective and transparent.
        """
        score = 0.0

        # Entropy is the strongest single signal
        entropy = features.get("entropy_full", 0)
        if entropy > 7.8:   score += 0.45
        elif entropy > 7.2: score += 0.25
        elif entropy > 6.5: score += 0.10

        # Ransomware strings are a near-certain hit
        hits = features.get("ransom_string_hits", 0)
        score += min(hits * 0.20, 0.40)

        # PE file with suspicious properties
        if features.get("is_pe") and features.get("pe_suspicious"):
            score += 0.15

        # Very high null-byte ratio often means encrypted content
        if features.get("null_byte_ratio", 0) > 0.3:
            score += 0.10

        # Suspiciously low printable ratio in a document-type file
        if features.get("is_suspicious_ext") and features.get("printable_ratio", 1) < 0.1:
            score += 0.15

        return min(score, 1.0)

    def _score_to_threat_level(self, score: float) -> str:
        if score < 0.15: return "clean"
        if score < 0.35: return "low"
        if score < 0.55: return "medium"
        if score < 0.75: return "high"
        return "critical"

    def _build_patterns(self, features: dict, threat_level: str) -> list[str]:
        """Generate human-readable descriptions of what was found."""
        patterns = []

        if features["entropy_full"] > 7.2:
            patterns.append(
                f"Very high file entropy ({features['entropy_full']:.2f}/8.0) — "
                "characteristic of encrypted or packed content"
            )

        if features["ransom_string_hits"] > 0:
            patterns.append(
                f"Found {features['ransom_string_hits']} ransomware-related "
                "string(s) embedded in file"
            )

        if features["is_pe"] and features["pe_suspicious"]:
            patterns.append(
                f"PE executable with unusual section count "
                f"({features['pe_section_count']}) — possible packer"
            )

        if features["null_byte_ratio"] > 0.3:
            patterns.append(
                "Unusually high null-byte density — may indicate encrypted payload"
            )

        if not patterns and threat_level == "clean":
            patterns.append("No suspicious patterns detected")

        return patterns

    def scan(self, file_data: bytes, filename: str) -> ScanResult:
        """
        Synchronous scan — call this directly or wrap in asyncio.
        Returns a ScanResult with full details.
        """
        start = time.monotonic()

        sha256 = _sha256(file_data)
        features = extract_features(file_data, filename)

        # Use ML model if available, otherwise rule-based
        if self.model is not None:
            vector = _features_to_vector(features)
            proba = self.model.predict_proba(vector)[0]
            # proba[1] = probability of being ransomware
            score = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            score = self._rule_based_score(features)

        threat_level = self._score_to_threat_level(score)
        patterns     = self._build_patterns(features, threat_level)

        elapsed_ms = int((time.monotonic() - start) * 1000)

        return ScanResult(
            sha256=sha256,
            threat_level=threat_level,
            confidence=round(score, 4),
            features=features,
            patterns=patterns,
            scan_duration_ms=elapsed_ms,
        )


# ── Model training helper (run once to create model/ransomware_rf.joblib) ─────

def train_demo_model(output_path: str = "app/ml/model/ransomware_rf.joblib"):
    """
    Train a demo RandomForest on SYNTHETIC data.

    In production you would replace this with real labelled samples.
    This gives you a working model to test the pipeline end-to-end.

    Run from project root:
        python -c "from app.ml.detector import train_demo_model; train_demo_model()"
    """
    import random
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    import joblib

    print("Generating synthetic training data...")
    rng = random.Random(42)
    X, y = [], []

    # Clean files: low entropy, no ransomware strings, normal PE
    for _ in range(600):
        X.append([
            rng.uniform(3.0, 5.5),  # entropy_full
            rng.uniform(2.5, 5.0),  # entropy_header
            rng.uniform(2.5, 5.0),  # entropy_footer
            0,                       # high_entropy
            rng.randint(0, 1),       # is_pe
            rng.randint(0, 1),       # is_suspicious_ext
            rng.randint(1, 5),       # pe_section_count
            0,                       # pe_suspicious
            0,                       # ransom_string_hits
            rng.uniform(0.6, 0.95),  # printable_ratio
            rng.randint(1000, 5000000), # file_size
            rng.uniform(0.0001, 0.001), # byte_variance
            rng.uniform(0.003, 0.005),  # byte_mean
            rng.uniform(0.0, 0.05),     # null_byte_ratio
        ])
        y.append(0)  # 0 = clean

    # Ransomware: high entropy, possibly some ransom strings, suspicious PE
    for _ in range(400):
        X.append([
            rng.uniform(7.0, 8.0),  # entropy_full — very high
            rng.uniform(6.5, 8.0),  # entropy_header
            rng.uniform(6.5, 8.0),  # entropy_footer
            1,                       # high_entropy
            rng.randint(0, 1),       # is_pe
            rng.randint(0, 1),       # is_suspicious_ext
            rng.randint(5, 15),      # pe_section_count — higher
            rng.randint(0, 1),       # pe_suspicious
            rng.randint(0, 3),       # ransom_string_hits
            rng.uniform(0.0, 0.2),   # printable_ratio — low
            rng.randint(50000, 2000000),
            rng.uniform(0.000001, 0.00005),  # very uniform = encrypted
            rng.uniform(0.003, 0.005),
            rng.uniform(0.1, 0.5),           # high null ratio
        ])
        y.append(1)  # 1 = ransomware

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    accuracy = clf.score(X_test, y_test)
    print(f"Demo model accuracy: {accuracy:.1%}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"Model saved to {output_path}")
    print("NOTE: This is trained on synthetic data. For production, use real samples.")


# ── Singleton ─────────────────────────────────────────────────────────────────

_detector_instance: Optional[RansomwareDetector] = None

def get_detector() -> RansomwareDetector:
    """Return the shared detector instance (created once on first call)."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = RansomwareDetector()
    return _detector_instance
