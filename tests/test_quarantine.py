"""
tests/test_quarantine.py
─────────────────────────
Tests for the quarantine encrypt/decrypt cycle.
"""

import os
import tempfile
import pytest
from app.services.quarantine import QuarantineService


@pytest.fixture
def quarantine_service(tmp_path):
    """Create a QuarantineService using a temp directory."""
    svc = QuarantineService.__new__(QuarantineService)
    svc.quarantine_dir = tmp_path
    return svc


def test_quarantine_creates_encrypted_file(quarantine_service, tmp_path):
    data = b"This is a test file that should be quarantined."
    result = quarantine_service.quarantine(
        file_data=data,
        original_filename="malware.exe",
        scan_id="test-scan-001",
        threat_level="critical",
    )

    assert "quarantine_path" in result
    assert "encryption_key" in result
    assert os.path.exists(result["quarantine_path"])

    # Encrypted file should NOT contain the original plaintext
    encrypted = open(result["quarantine_path"], "rb").read()
    assert data not in encrypted


def test_quarantine_and_release(quarantine_service):
    original_data = b"Secret file content that got quarantined."
    result = quarantine_service.quarantine(
        file_data=original_data,
        original_filename="document.docx",
        scan_id="test-scan-002",
        threat_level="high",
    )

    # Release and check we get back the original bytes
    released = quarantine_service.release(
        quarantine_path=result["quarantine_path"],
        encryption_key=result["encryption_key"],
    )

    assert released == original_data


def test_wrong_key_fails(quarantine_service):
    data = b"Some content"
    result = quarantine_service.quarantine(
        file_data=data,
        original_filename="file.txt",
        scan_id="test-scan-003",
        threat_level="medium",
    )

    # Wrong key should return None
    from cryptography.fernet import Fernet
    wrong_key = Fernet.generate_key().decode()
    released = quarantine_service.release(
        quarantine_path=result["quarantine_path"],
        encryption_key=wrong_key,
    )
    assert released is None


def test_delete_quarantined_file(quarantine_service):
    data = b"Malicious content"
    result = quarantine_service.quarantine(
        file_data=data,
        original_filename="virus.exe",
        scan_id="test-scan-004",
        threat_level="critical",
    )

    path = result["quarantine_path"]
    assert os.path.exists(path)

    success = quarantine_service.delete(path)
    assert success
    assert not os.path.exists(path)


def test_large_file_quarantine(quarantine_service):
    """Test with a 1MB file."""
    data = os.urandom(1024 * 1024)
    result = quarantine_service.quarantine(
        file_data=data,
        original_filename="large_ransomware.bin",
        scan_id="test-scan-005",
        threat_level="critical",
    )

    released = quarantine_service.release(
        quarantine_path=result["quarantine_path"],
        encryption_key=result["encryption_key"],
    )
    assert released == data
