import sqlite3

conn = sqlite3.connect('rangard.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"  {table_name}: {count} rows")

# Check users table specifically
print("\nUsers in database:")
try:
    cursor.execute("SELECT id, email, is_verified FROM users LIMIT 5;")
    users = cursor.fetchall()
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Verified: {user[2]}")
except Exception as e:
    print(f"  Error: {e}")

# Check file_scans table
print("\nFile Scans in database:")
try:
    cursor.execute("SELECT id, user_id, original_filename, threat_level FROM file_scans LIMIT 5;")
    scans = cursor.fetchall()
    for scan in scans:
        print(f"  ID: {scan[0]}, User: {scan[1]}, File: {scan[2]}, Threat: {scan[3]}")
except Exception as e:
    print(f"  Error: {e}")

conn.close()
