"""
app/services/quarantine.py
──────────────────────────
Quarantine system — isolates suspicious files so they can't spread.

HOW QUARANTINE WORKS:
  1. The original file is ENCRYPTED using Fernet symmetric encryption
  2. The encrypted blob is stored in an isolated directory
  3. The original is deleted from the upload location
  4. The decryption key is stored securely in the database record
  5. To restore: the file is decrypted and moved back

This ensures:
  • Quarantined files can't execute or infect other files
  • Files aren't permanently deleted (so false positives can be recovered)
  • There's a full audit trail of quarantine/release events
"""

import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class QuarantineService:

    def __init__(self):
        self.quarantine_dir = Path(settings.QUARANTINE_DIR)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        # Each quarantine operation uses a fresh key.
        # The key is stored in the DB so the file can be decrypted later.
        logger.info(f"[Quarantine] Directory: {self.quarantine_dir}")

    def quarantine(
        self,
        file_data: bytes,
        original_filename: str,
        scan_id: str,
        threat_level: str,
    ) -> dict:
        """
        Encrypt and isolate file_data in the quarantine directory.

        Returns dict with:
            quarantine_path: str  — path to the encrypted file
            encryption_key:  str  — Fernet key (store this in DB!)
            quarantined_at:  str  — ISO timestamp
        """
        # Generate a fresh encryption key for this file
        key = Fernet.generate_key()
        fernet = Fernet(key)

        # Encrypt the file content
        encrypted_data = fernet.encrypt(file_data)

        # Save to quarantine directory
        # Filename = scan_id.quar (hides the original filename)
        quar_filename = f"{scan_id}.quar"
        quar_path = self.quarantine_dir / quar_filename
        quar_path.write_bytes(encrypted_data)

        # Write a metadata sidecar file (human-readable)
        meta_path = self.quarantine_dir / f"{scan_id}.meta"
        meta_content = (
            f"RANSOMGUARD QUARANTINE RECORD\n"
            f"Scan ID:           {scan_id}\n"
            f"Original filename: {original_filename}\n"
            f"Threat level:      {threat_level}\n"
            f"Quarantined at:    {datetime.now(timezone.utc).isoformat()}\n"
            f"File size:         {len(file_data)} bytes\n"
            f"Encrypted:         YES (Fernet)\n"
        )
        meta_path.write_text(meta_content)

        logger.info(
            f"[Quarantine] {original_filename} quarantined as {quar_filename} "
            f"(threat: {threat_level})"
        )

        return {
            "quarantine_path": str(quar_path),
            "encryption_key":  key.decode(),   # store in DB
            "quarantined_at":  datetime.now(timezone.utc).isoformat(),
        }

    def release(
        self,
        quarantine_path: str,
        encryption_key: str,
        destination: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Decrypt and release a quarantined file.

        Args:
            quarantine_path: Path to the .quar file
            encryption_key:  The key stored in the DB
            destination:     Where to write the decrypted file (optional)

        Returns:
            Decrypted file bytes, or None if decryption fails.
        """
        quar_path = Path(quarantine_path)
        if not quar_path.exists():
            logger.error(f"[Quarantine] File not found: {quarantine_path}")
            return None

        try:
            fernet = Fernet(encryption_key.encode())
            encrypted_data = quar_path.read_bytes()
            file_data = fernet.decrypt(encrypted_data)

            if destination:
                Path(destination).parent.mkdir(parents=True, exist_ok=True)
                Path(destination).write_bytes(file_data)
                logger.info(f"[Quarantine] Released to {destination}")

            return file_data

        except Exception as e:
            logger.error(f"[Quarantine] Release failed: {e}")
            return None

    def delete(self, quarantine_path: str) -> bool:
        """
        Permanently delete a quarantined file.
        Use only when you're certain the file is malicious.
        """
        try:
            quar_path = Path(quarantine_path)
            if quar_path.exists():
                quar_path.unlink()

            # Also remove sidecar
            meta_path = quar_path.with_suffix(".meta")
            if meta_path.exists():
                meta_path.unlink()

            logger.info(f"[Quarantine] Deleted {quarantine_path}")
            return True
        except Exception as e:
            logger.error(f"[Quarantine] Delete failed: {e}")
            return False

    def list_quarantined(self) -> list[dict]:
        """List all files currently in quarantine."""
        files = []
        for meta_file in self.quarantine_dir.glob("*.meta"):
            try:
                content = meta_file.read_text()
                scan_id = meta_file.stem
                quar_file = meta_file.with_suffix(".quar")
                files.append({
                    "scan_id": scan_id,
                    "exists": quar_file.exists(),
                    "size_bytes": quar_file.stat().st_size if quar_file.exists() else 0,
                    "metadata": content,
                })
            except Exception:
                pass
        return files


# ── Singleton ─────────────────────────────────────────────────────────────────

_quarantine_service: Optional[QuarantineService] = None

def get_quarantine_service() -> QuarantineService:
    global _quarantine_service
    if _quarantine_service is None:
        _quarantine_service = QuarantineService()
    return _quarantine_service
