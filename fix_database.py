# fix_time_data.py
import sqlite3
from pathlib import Path

db_path = Path("/app/data/amoria.db")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Cek kolom yang ada
cursor.execute("PRAGMA table_info(state_tracker)")
columns = [col[1] for col in cursor.fetchall()]

print(f"Existing columns: {columns}")

if 'time_data' not in columns:
    print("Adding time_data column...")
    cursor.execute("ALTER TABLE state_tracker ADD COLUMN time_data TEXT")
    conn.commit()
    print("✅ time_data column added")
else:
    print("✅ time_data already exists")

# Verifikasi
cursor.execute("PRAGMA table_info(state_tracker)")
columns = [col[1] for col in cursor.fetchall()]
print(f"\nFinal columns: {columns}")

if 'time_data' in columns:
    print("\n✅ SUCCESS! Bot ready to run")
else:
    print("\n❌ FAILED!")

conn.close()
