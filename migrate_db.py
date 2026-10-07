import sqlite3

db_path = 'roadsense.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(detections)')
cols = [row[1] for row in cursor.fetchall()]
print('Existing columns:', cols)

additions = [
    ('repair_proof_path', 'TEXT'),
    ('street_name', 'TEXT'),
    ('priority', 'TEXT'),
    ('is_simulated_gps', 'INTEGER'),
    ('code', 'TEXT'),
    ('snapshot_path', 'TEXT'),
]

added = []
for col_name, col_type in additions:
    if col_name not in cols:
        cursor.execute(f'ALTER TABLE detections ADD COLUMN {col_name} {col_type}')
        added.append(col_name)

conn.commit()
conn.close()
print('Added missing columns:', added if added else 'none needed')
print('Migration complete.')
