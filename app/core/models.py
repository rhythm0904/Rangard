"""
app/core/models.py
──────────────────
SQLAlchemy ORM models.  Each class becomes a database table.
Relationships are defined so we can do:
    user.scans          → all scans for a user
    scan.quarantine     → the quarantine record for a scan
    scan.blockchain     → the blockchain record for a scan
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float,
    ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


# ── Base class ────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Enums ─────────────────────────────────────────────────────────────────────

class ThreatLevel(str, enum.Enum):
    CLEAN    = "clean"
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class ScanStatus(str, enum.Enum):
    PENDING    = "pending"
    SCANNING   = "scanning"
    COMPLETE   = "complete"
    FAILED     = "failed"


class QuarantineStatus(str, enum.Enum):
    QUARANTINED = "quarantined"
    RELEASED    = "released"
    DELETED     = "deleted"


# ── Tables ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name       = Column(String(255), nullable=True)
    is_active       = Column(Boolean, default=True, nullable=False)
    is_verified     = Column(Boolean, default=False, nullable=False)
    created_at      = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at      = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    scans           = relationship("FileScan", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class FileScan(Base):
    """One record per file upload & scan."""
    __tablename__ = "file_scans"

    id               = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id          = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # File info
    original_filename = Column(String(500), nullable=False)
    file_size_bytes   = Column(Integer, nullable=False)
    mime_type         = Column(String(200), nullable=True)
    sha256_hash       = Column(String(64), nullable=False, index=True)  # file fingerprint

    # Scan result
    status           = Column(Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False)
    threat_level     = Column(Enum(ThreatLevel), nullable=True)
    confidence_score = Column(Float, nullable=True)   # 0.0 → 1.0
    ml_features      = Column(JSON, nullable=True)    # raw feature vector (for debugging)
    detected_patterns = Column(JSON, nullable=True)   # list of matched patterns / signatures
    scan_duration_ms = Column(Integer, nullable=True)

    # Storage
    storage_path     = Column(String(1000), nullable=True)   # S3 key or local path
    ipfs_cid         = Column(String(100), nullable=True)    # IPFS content ID

    created_at       = Column(DateTime(timezone=True), default=_now, nullable=False)
    completed_at     = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user             = relationship("User", back_populates="scans")
    quarantine       = relationship("QuarantineRecord", back_populates="scan", uselist=False)
    blockchain       = relationship("BlockchainRecord", back_populates="scan", uselist=False)

    def __repr__(self) -> str:
        return f"<FileScan {self.original_filename} [{self.threat_level}]>"


class QuarantineRecord(Base):
    """Files flagged as suspicious are moved here."""
    __tablename__ = "quarantine_records"

    id           = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    scan_id      = Column(UUID(as_uuid=False), ForeignKey("file_scans.id", ondelete="CASCADE"), unique=True, nullable=False)
    quarantine_path = Column(String(1000), nullable=False)   # encrypted file on disk
    status       = Column(Enum(QuarantineStatus), default=QuarantineStatus.QUARANTINED)
    reason       = Column(Text, nullable=True)               # human-readable why it was quarantined
    quarantined_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    resolved_at    = Column(DateTime(timezone=True), nullable=True)

    scan         = relationship("FileScan", back_populates="quarantine")


class BlockchainRecord(Base):
    """
    Stores the Ethereum transaction that anchored the file hash on-chain.
    This gives immutable proof that a file existed in a known state at a given time.
    """
    __tablename__ = "blockchain_records"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    scan_id         = Column(UUID(as_uuid=False), ForeignKey("file_scans.id", ondelete="CASCADE"), unique=True, nullable=False)
    tx_hash         = Column(String(66), nullable=False, index=True)   # 0x + 64 hex chars
    block_number    = Column(Integer, nullable=True)
    network         = Column(String(50), nullable=False, default="sepolia")
    file_hash       = Column(String(64), nullable=False)               # sha256 of original file
    version         = Column(Integer, nullable=False, default=1)       # increments on each re-anchor
    gas_used        = Column(Integer, nullable=True)
    anchored_at     = Column(DateTime(timezone=True), default=_now, nullable=False)

    scan            = relationship("FileScan", back_populates="blockchain")


class ThreatIntelligence(Base):
    """
    Anonymised threat signatures contributed by the community.
    No file content is stored — only behavioural patterns.
    """
    __tablename__ = "threat_intelligence"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    pattern_hash    = Column(String(64), unique=True, nullable=False, index=True)
    threat_family   = Column(String(200), nullable=True)   # e.g. "WannaCry", "Ryuk"
    pattern_type    = Column(String(100), nullable=True)   # e.g. "file_extension_mass_rename"
    severity        = Column(Enum(ThreatLevel), nullable=False)
    occurrences     = Column(Integer, default=1, nullable=False)
    first_seen      = Column(DateTime(timezone=True), default=_now, nullable=False)
    last_seen       = Column(DateTime(timezone=True), default=_now, nullable=False)
    metadata        = Column(JSON, nullable=True)
