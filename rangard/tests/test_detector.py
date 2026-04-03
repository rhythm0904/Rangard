"""
tests/test_detector.py
───────────────────────
Unit tests for the ML ransomware detector.

Run with:
    pytest tests/ -v
"""

import pytest
from app.ml.detector import (
    RansomwareDetector,
    extract_features,
    _entropy,
    _sha256,
)


# ── Entropy tests ──────────────────────────────────────────────────────────────

def test_entropy_empty():
    assert _entropy(b"") == 0.0


def test_entropy_uniform():
    # All same byte = 0 entropy (perfectly predictable)
    data = b"\x00" * 1000
    assert _entropy(data) == 0.0


def test_entropy_random():
    # Random-ish data should have high entropy
    import os
    data = os.urandom(4096)
    assert _entropy(data) > 7.0


def test_entropy_text():
    # English text is around 3-5 bits
    data = b"The quick brown fox jumps over the lazy dog" * 20
    e = _entropy(data)
    assert 3.0 < e < 6.0


# ── SHA-256 ────────────────────────────────────────────────────────────────────

def test_sha256_known():
    # Known hash for empty string
    h = _sha256(b"")
    assert h == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert len(h) == 64


def test_sha256_deterministic():
    data = b"RANGARD test data"
    assert _sha256(data) == _sha256(data)


# ── Feature extraction ─────────────────────────────────────────────────────────

def test_features_clean_text():
    data = b"Hello world, this is a plain text file with normal content." * 50
    features = extract_features(data, "readme.txt")

    assert features["is_pe"] == 0
    assert features["high_entropy"] == 0
    assert features["ransom_string_hits"] == 0
    assert features["entropy_full"] < 6.0


def test_features_ransomware_strings():
    data = b"your files have been encrypted pay bitcoin ransom" * 10
    features = extract_features(data, "README_IMPORTANT.txt")

    assert features["ransom_string_hits"] >= 2


def test_features_high_entropy():
    import os
    # Simulated encrypted content = random bytes
    data = os.urandom(8192)
    features = extract_features(data, "document.docx")

    assert features["high_entropy"] == 1
    assert features["entropy_full"] > 7.0


def test_features_pe_file():
    # Minimal PE header (MZ magic)
    data = b"MZ" + b"\x00" * 58 + b"\x40\x00\x00\x00" + b"\x00" * 200
    features = extract_features(data, "program.exe")

    assert features["is_pe"] == 1


def test_features_suspicious_extension():
    data = b"content" * 100
    features = extract_features(data, "invoice.docx")
    assert features["is_suspicious_ext"] == 1

    features2 = extract_features(data, "script.py")
    assert features2["is_suspicious_ext"] == 0


# ── Detector end-to-end ────────────────────────────────────────────────────────

@pytest.fixture
def detector():
    return RansomwareDetector()


def test_clean_file(detector):
    data = b"This is a completely normal text document.\n" * 100
    result = detector.scan(data, "notes.txt")

    assert result.threat_level in ("clean", "low")
    assert result.confidence < 0.5
    assert result.sha256 is not None
    assert len(result.sha256) == 64
    assert result.scan_duration_ms >= 0


def test_ransomware_strings(detector):
    data = (
        b"your files have been encrypted\n"
        b"send bitcoin to decrypt your files\n"
        b"visit our .onion site\n"
        b"pay ransom within 72 hours\n"
    ) * 5
    result = detector.scan(data, "README_DECRYPT.txt")

    # Should detect as at least medium threat
    assert result.threat_level in ("medium", "high", "critical")
    assert result.confidence > 0.3
    assert len(result.patterns) > 0


def test_high_entropy_file(detector):
    import os
    data = os.urandom(10000)
    result = detector.scan(data, "suspicious.bin")

    assert result.confidence > 0.2
    assert result.threat_level != "clean" or result.confidence < 0.2


def test_result_has_all_fields(detector):
    data = b"test file content"
    result = detector.scan(data, "test.txt")

    assert result.sha256
    assert result.threat_level in ("clean", "low", "medium", "high", "critical")
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.features, dict)
    assert isinstance(result.patterns, list)
    assert result.scan_duration_ms >= 0


def test_scan_duration_reasonable(detector):
    data = b"test" * 10000
    result = detector.scan(data, "large_file.txt")
    # Should complete in under 5 seconds
    assert result.scan_duration_ms < 5000


def test_deterministic_results(detector):
    """Same file always produces same result."""
    data = b"deterministic test content" * 200
    r1 = detector.scan(data, "file.txt")
    r2 = detector.scan(data, "file.txt")

    assert r1.sha256 == r2.sha256
    assert r1.threat_level == r2.threat_level
    assert r1.confidence == r2.confidence
