import sqlite3
conn = sqlite3.connect('db/nova.db')
cols = [row[1] for row in conn.execute('PRAGMA table_info(memory_entries)')]
print('Columns:', cols)
conn.close()
