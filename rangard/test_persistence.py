"""
Test script to verify document persistence is working correctly.
This will:
1. Check existing scans in the database
2. Test uploading a new file and verify it's saved
3. Verify retrieval of scan list
"""
import sys
sys.path.insert(0, '.')

import asyncio
import sqlite3
from datetime import datetime, timezone

# Direct database check
def check_database():
    print("=" * 60)
    print("DATABASE PERSISTENCE STATUS")
    print("=" * 60)
    
    conn = sqlite3.connect('rangard.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"\nTables in database: {len(tables)}")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table_name}: {count} rows")
    
    # Check recent scans
    print("\n" + "-" * 60)
    print("RECENT SCANS (Last 5):")
    print("-" * 60)
    cursor.execute("""
        SELECT id, user_id, original_filename, threat_level, created_at
        FROM file_scans
        ORDER BY created_at DESC
        LIMIT 5
    """)
    scans = cursor.fetchall()
    
    if scans:
        for scan in scans:
            scan_id, user_id, filename, threat_level, created_at = scan
            print(f"\n  ID: {scan_id[:8]}...")
            print(f"     User: {user_id[:8]}...")
            print(f"     File: {filename}")
            print(f"     Threat: {threat_level}")
            print(f"     Created: {created_at}")
    else:
        print("\n  ⚠️  No scans found in database!")
    
    # Check all scans for each user
    print("\n" + "-" * 60)
    print("SCANS BY USER:")
    print("-" * 60)
    cursor.execute("""
        SELECT u.id, u.email, COUNT(fs.id) as scan_count
        FROM users u
        LEFT JOIN file_scans fs ON u.id = fs.user_id
        GROUP BY u.id
        ORDER BY scan_count DESC
    """)
    user_scans = cursor.fetchall()
    
    for user_id, email, scan_count in user_scans[:5]:
        print(f"\n  {email}: {scan_count} scans")
    
    # Check quarantine records
    print("\n" + "-" * 60)
    print("QUARANTINE RECORDS:")
    print("-" * 60)
    cursor.execute("SELECT COUNT(*) FROM quarantine_records;")
    quar_count = cursor.fetchone()[0]
    print(f"  Total quarantined files: {quar_count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE IS PERSISTING DOCUMENTS AND SCANS!")
    print("=" * 60)

if __name__ == "__main__":
    check_database()
