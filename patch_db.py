import sqlite3, os, shutil

db_path = r"D:\Sammis Autonomous OS\factory_a\data\factory_a.db"
journal = db_path + "-journal"

# Step 1: Delete journal file if exists (force rollback on next open)
if os.path.exists(journal):
    os.remove(journal)
    print("Removed journal file")

# Step 2: Open and repair corrupted schema entry
conn = sqlite3.connect(db_path, timeout=10)
try:
    # Enable writable schema to fix corrupted sqlite_master entry
    conn.execute("PRAGMA writable_schema=ON")
    # Remove the bad sammis_pain_inputs entry from sqlite_master
    conn.execute("DELETE FROM sqlite_master WHERE name='sammis_pain_inputs' AND type='table'")
    conn.execute("PRAGMA writable_schema=OFF")
    conn.execute("PRAGMA integrity_check")
    conn.commit()
    print("Removed corrupted sammis_pain_inputs entry from schema")
except Exception as e:
    print(f"Schema repair error: {e}")

# Step 3: VACUUM to compact and rebuild schema
try:
    conn.execute("VACUUM")
    print("VACUUM done")
except Exception as e:
    print(f"VACUUM error: {e}")
conn.close()

# Step 4: Reopen and patch
conn = sqlite3.connect(db_path, timeout=10)

# Add missing columns to pipeline_runs
for col, dtype in [("quality_report_id", "TEXT"), ("deployment_report_id", "TEXT")]:
    try:
        conn.execute(f"ALTER TABLE pipeline_runs ADD COLUMN {col} {dtype}")
        print(f"Added column: pipeline_runs.{col}")
    except Exception as e:
        print(f"Skip {col}: {e}")

# Recreate sammis_pain_inputs cleanly
conn.execute("""CREATE TABLE IF NOT EXISTS sammis_pain_inputs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    raw_text TEXT NOT NULL,
    submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
    suggested_segment TEXT,
    notes TEXT,
    processed INTEGER NOT NULL DEFAULT 0,
    pain_archive_id TEXT
)""")
print("Created: sammis_pain_inputs")

conn.commit()

# Step 5: Verify
cols = [r[1] for r in conn.execute("PRAGMA table_info(pipeline_runs)").fetchall()]
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
check = conn.execute("PRAGMA integrity_check").fetchone()[0]
print(f"\nintegrity_check: {check}")
print("pipeline_runs columns:", cols)
print("all tables:", tables)
conn.close()
print("\nDONE")
