"""
app/api/scans.py
────────────────
File scanning endpoints — the heart of the application.

  POST /api/scans/upload       → upload a file, trigger AI scan
  GET  /api/scans/             → list all scans for current user
  GET  /api/scans/{scan_id}    → get one scan with full details
  GET  /api/scans/{scan_id}/report → download PDF report
  POST /api/scans/{scan_id}/release → release from quarantine
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.models import (
    BlockchainRecord, FileScan, QuarantineRecord,
    QuarantineStatus, ScanStatus, ThreatLevel, User,
)
from app.ml.detector import get_detector
from app.blockchain.service import get_blockchain_service
from app.services.email import get_email_service
from app.services.quarantine import get_quarantine_service
from app.services.report import generate_pdf_report

router = APIRouter(prefix="/api/scans", tags=["File Scanning"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Threat levels that trigger quarantine
QUARANTINE_LEVELS = {"medium", "high", "critical"}


# ── Response schemas ──────────────────────────────────────────────────────────

class ScanSummary(BaseModel):
    id: str
    filename: str
    threat_level: Optional[str]
    confidence: Optional[float]
    status: str
    created_at: datetime
    is_quarantined: bool
    has_blockchain: bool


class ScanDetail(ScanSummary):
    sha256: str
    file_size_bytes: int
    mime_type: Optional[str]
    detected_patterns: Optional[list]
    scan_duration_ms: Optional[int]
    blockchain_tx: Optional[str]
    quarantine_reason: Optional[str]
    completed_at: Optional[datetime]


class UploadResponse(BaseModel):
    scan_id: str
    status: str
    message: str
    threat_level: Optional[str] = None
    confidence: Optional[float] = None
    quarantined: bool = False
    blockchain_tx: Optional[str] = None


# ── The main upload + scan endpoint ──────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a file and run AI ransomware detection.

    Pipeline:
      1. Read file bytes and validate size
      2. Run ML detection
      3. If threat detected: quarantine + send email alert
      4. Anchor file hash to Ethereum blockchain
      5. Save results to database
      6. Return results to frontend

    The whole pipeline runs synchronously but is wrapped in async
    so FastAPI can handle other requests while heavy I/O waits.
    """
    try:
        print("File received:", file.filename)

        # ── 1. Read and validate ───────────────────────────────────────────────
        file_data = await file.read()

        if len(file_data) == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        if len(file_data) > settings.max_file_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB}MB",
            )

        size = len(file_data)
        print("File size:", size)

        # ── 2. Create a DB record immediately (status = scanning) ──────────────
        scan = FileScan(
            user_id=current_user.id,
            original_filename=file.filename or "unknown",
            file_size_bytes=size,
            mime_type=file.content_type,
            sha256_hash="pending",
            status=ScanStatus.SCANNING,
        )
        db.add(scan)
        await db.flush()  # get scan.id
        scan_id = scan.id

        # ── 3. Run ML detection (CPU-bound — run in thread pool) ───────────
        detector = get_detector()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            detector.scan,
            file_data,
            file.filename or "unknown",
        )

        scan.sha256_hash = result.sha256
        scan.threat_level = ThreatLevel(result.threat_level)
        scan.confidence_score = result.confidence
        scan.ml_features = result.features
        scan.detected_patterns = result.patterns
        scan.scan_duration_ms = result.scan_duration_ms
        scan.status = ScanStatus.COMPLETE
        scan.completed_at = datetime.now(timezone.utc)

        logger.info(
            f"[Scan] {file.filename} → {result.threat_level.upper()} "
            f"(confidence: {result.confidence:.1%}, {result.scan_duration_ms}ms)"
        )

        # ── 4. Quarantine if needed ────────────────────────────────────────
        is_quarantined = False
        if result.threat_level in QUARANTINE_LEVELS:
            quarantine_svc = get_quarantine_service()
            quar = quarantine_svc.quarantine(
                file_data=file_data,
                original_filename=file.filename or "unknown",
                scan_id=scan_id,
                threat_level=result.threat_level,
            )
            quar_record = QuarantineRecord(
                scan_id=scan_id,
                quarantine_path=quar["quarantine_path"],
                reason=(
                    f"AI detection: {result.threat_level} threat "
                    f"(confidence {result.confidence:.1%})\n"
                    + "\n".join(result.patterns)
                ),
                status=QuarantineStatus.QUARANTINED,
            )
            db.add(quar_record)
            is_quarantined = True
            logger.info(f"[Quarantine] {file.filename} quarantined (scan {scan_id})")

        # ── 5. Send email alert (async fire-and-forget) ───────────────────
        # Only send alerts to verified emails
        email_alert_sent = False
        if result.threat_level != "clean" and current_user.is_verified:
            email_svc = get_email_service()
            asyncio.create_task(
                _send_alert_async(
                    email_svc,
                    to_email=current_user.email,
                    to_name=current_user.full_name or current_user.email,
                    filename=file.filename or "unknown",
                    threat_level=result.threat_level,
                    confidence=result.confidence,
                    patterns=result.patterns,
                    scan_id=scan_id,
                )
            )
            email_alert_sent = True
        elif result.threat_level != "clean" and not current_user.is_verified:
            logger.info(f"[Alert] User {current_user.email} not verified — threat alert not sent")

        # ── 6. Anchor to blockchain ────────────────────────────────────────
        blockchain_svc = get_blockchain_service()
        anchor = await loop.run_in_executor(
            None,
            blockchain_svc.anchor_file,
            result.sha256,
            scan.ipfs_cid or "",
            1,
        )

        tx_hash = None
        if anchor.success:
            bc_record = BlockchainRecord(
                scan_id=scan_id,
                tx_hash=anchor.tx_hash,
                block_number=anchor.block_number,
                network=anchor.network,
                file_hash=result.sha256,
                gas_used=anchor.gas_used,
            )
            db.add(bc_record)
            tx_hash = anchor.tx_hash
            logger.info(f"[Blockchain] Anchored {result.sha256[:16]}… tx: {anchor.tx_hash[:16]}…")

        await db.commit()

        # Build message based on threat level and email verification status
        base_message = _result_message(result.threat_level, is_quarantined)
        if result.threat_level != "clean" and not current_user.is_verified:
            base_message += " (Email alerts disabled — verify your email to receive notifications)"

        return UploadResponse(
            scan_id=scan_id,
            status="complete",
            message=base_message,
            threat_level=result.threat_level,
            confidence=result.confidence,
            quarantined=is_quarantined,
            blockchain_tx=tx_hash,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Scan] Failed for {file.filename}: {e}", exc_info=True)
        if 'scan' in locals() and scan is not None:
            scan.status = ScanStatus.FAILED
            await db.commit()
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


# ── List scans ────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ScanSummary])
async def list_scans(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all scans for the authenticated user, newest first."""
    result = await db.execute(
        select(FileScan)
        .where(FileScan.user_id == current_user.id)
        .order_by(desc(FileScan.created_at))
        .limit(limit)
        .offset(offset)
    )
    scans = result.scalars().all()

    return [
        ScanSummary(
            id=s.id,
            filename=s.original_filename,
            threat_level=s.threat_level.value if s.threat_level else None,
            confidence=s.confidence_score,
            status=s.status.value,
            created_at=s.created_at,
            is_quarantined=s.quarantine is not None,
            has_blockchain=s.blockchain is not None,
        )
        for s in scans
    ]


# ── Single scan detail ────────────────────────────────────────────────────────

@router.get("/{scan_id}", response_model=ScanDetail)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return full details for one scan (only accessible to the owner)."""
    result = await db.execute(
        select(FileScan).where(
            FileScan.id == scan_id,
            FileScan.user_id == current_user.id,
        )
    )
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return ScanDetail(
        id=scan.id,
        filename=scan.original_filename,
        threat_level=scan.threat_level.value if scan.threat_level else None,
        confidence=scan.confidence_score,
        status=scan.status.value,
        created_at=scan.created_at,
        is_quarantined=scan.quarantine is not None,
        has_blockchain=scan.blockchain is not None,
        sha256=scan.sha256_hash,
        file_size_bytes=scan.file_size_bytes,
        mime_type=scan.mime_type,
        detected_patterns=scan.detected_patterns,
        scan_duration_ms=scan.scan_duration_ms,
        blockchain_tx=scan.blockchain.tx_hash if scan.blockchain else None,
        quarantine_reason=scan.quarantine.reason if scan.quarantine else None,
        completed_at=scan.completed_at,
    )


# ── PDF report download ───────────────────────────────────────────────────────

@router.get("/{scan_id}/report")
async def download_report(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and download a PDF report for a completed scan."""
    result = await db.execute(
        select(FileScan).where(
            FileScan.id == scan_id,
            FileScan.user_id == current_user.id,
        )
    )
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status != ScanStatus.COMPLETE:
        raise HTTPException(status_code=400, detail="Scan is not yet complete")

    pdf_bytes = generate_pdf_report(scan, current_user)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="rangard-report-{scan_id[:8]}.pdf"'
            )
        },
    )


# ── Release from quarantine ───────────────────────────────────────────────────

@router.post("/{scan_id}/release", status_code=status.HTTP_200_OK)
async def release_from_quarantine(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Release a quarantined file (use if you're certain it's a false positive).
    The file is decrypted and the quarantine record is marked as released.
    """
    result = await db.execute(
        select(FileScan).where(
            FileScan.id == scan_id,
            FileScan.user_id == current_user.id,
        )
    )
    scan = result.scalar_one_or_none()

    if not scan or not scan.quarantine:
        raise HTTPException(status_code=404, detail="Quarantined scan not found")

    if scan.quarantine.status != QuarantineStatus.QUARANTINED:
        raise HTTPException(status_code=400, detail="File is not currently quarantined")

    scan.quarantine.status = QuarantineStatus.RELEASED
    scan.quarantine.resolved_at = datetime.now(timezone.utc)
    await db.commit()

    logger.warning(
        f"[Quarantine] {scan.original_filename} RELEASED from quarantine "
        f"by {current_user.email}"
    )

    return {"message": "File released from quarantine", "scan_id": scan_id}


# ── Analytics for dashboard ───────────────────────────────────────────────────

@router.get("/analytics/summary")
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return threat statistics for the dashboard charts."""
    from sqlalchemy import func

    result = await db.execute(
        select(
            FileScan.threat_level,
            func.count(FileScan.id).label("count")
        )
        .where(FileScan.user_id == current_user.id)
        .group_by(FileScan.threat_level)
    )
    rows = result.all()

    totals = {row.threat_level.value: row.count for row in rows if row.threat_level}
    total_scans = sum(totals.values())

    return {
        "total_scans": total_scans,
        "by_threat_level": totals,
        "quarantine_count": totals.get("critical", 0) + totals.get("high", 0) + totals.get("medium", 0),
        "clean_count": totals.get("clean", 0),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _result_message(threat_level: str, is_quarantined: bool) -> str:
    messages = {
        "clean":    "✅ File is clean — no threats detected",
        "low":      "⚠️ Low-risk patterns detected — file flagged for review",
        "medium":   "🚨 Medium threat detected — file quarantined",
        "high":     "🚨 High threat detected — file quarantined immediately",
        "critical": "🔴 CRITICAL threat detected — file quarantined, check your email",
    }
    return messages.get(threat_level, "Scan complete")


async def _send_alert_async(email_svc, **kwargs):
    """Wrapper to run email sending without blocking the response."""
    try:
        loop = asyncio.get_event_loop()
        def _send():
            success, error_msg = email_svc.send_threat_alert(**kwargs)
            if not success:
                logger.error(f"[Email] Background send failed: {error_msg}")
            return success
        await loop.run_in_executor(None, _send)
    except Exception as e:
        logger.error(f"[Email] Background send error: {e}")
