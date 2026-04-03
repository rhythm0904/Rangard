"""
Test script to verify file upload and persistence works end-to-end.
"""
import sys
sys.path.insert(0, '.')

import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.models import Base, User, FileScan, ScanStatus, ThreatLevel
from app.core.database import AsyncSessionLocal

async def test_persistence():
    print("=" * 70)
    print("FILE UPLOAD PERSISTENCE TEST")
    print("=" * 70)
    
    settings = get_settings()
    
    # Use the same database session as the app
    async with AsyncSessionLocal() as session:
        # Create a test user
        test_user_email = f"persistence_test_{uuid.uuid4().hex[:8]}@test.com"
        test_user = User(
            email=test_user_email,
            hashed_password="test_hash",
            full_name="Persistence Tester",
            is_verified=True,
        )
        session.add(test_user)
        await session.flush()
        user_id = test_user.id
        
        print(f"\n✓ Created test user: {test_user_email}")
        print(f"  User ID: {user_id}")
        
        # Create a test file scan record
        scan = FileScan(
            user_id=user_id,
            original_filename="test_document.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            sha256_hash="abc123def456",
            status=ScanStatus.COMPLETE,
            threat_level=ThreatLevel.CLEAN,
            confidence_score=0.95,
            scan_duration_ms=1500,
            completed_at=datetime.now(timezone.utc),
        )
        session.add(scan)
        await session.flush()
        scan_id = scan.id
        print(f"\n✓ Created test file scan record")
        print(f"  Scan ID: {scan_id}")
        print(f"  File: test_document.pdf")
        print(f"  Threat Level: CLEAN")
        
        # Commit the changes
        await session.commit()
        print(f"\n✓ Committed to database")
        
        # Now retrieve it to verify it was saved
        print(f"\n" + "-" * 70)
        print("RETRIEVING SAVED RECORD FROM DATABASE")
        print("-" * 70)
        
    # Use a fresh session to verify retrieval
    async with AsyncSessionLocal() as session:
        # Query the test user's scans
        result = await session.execute(
            select(FileScan)
            .where(FileScan.user_id == user_id)
            .order_by(desc(FileScan.created_at))
        )
        scans = result.scalars().all()
        
        print(f"\n✓ Found {len(scans)} scan(s) for user {test_user_email}")
        
        if scans:
            latest_scan = scans[0]
            print(f"\n  Latest scan details:")
            print(f"    ID: {latest_scan.id}")
            print(f"    File: {latest_scan.original_filename}")
            print(f"    Size: {latest_scan.file_size_bytes} bytes")
            print(f"    Threat: {latest_scan.threat_level.value if latest_scan.threat_level else 'N/A'}")
            print(f"    Confidence: {latest_scan.confidence_score}")
            print(f"    Status: {latest_scan.status.value}")
            print(f"    Created: {latest_scan.created_at}")
            
            if latest_scan.id == scan_id:
                print(f"\n✅ PERSISTENCE TEST PASSED!")
                print("   The file scan record was successfully saved and retrieved from database.")
                return True
    
    print(f"\n❌ PERSISTENCE TEST FAILED!")
    return False

if __name__ == "__main__":
    result = asyncio.run(test_persistence())
    print("\n" + "=" * 70)
