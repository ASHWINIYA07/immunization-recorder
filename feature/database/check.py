import sqlite3

conn = sqlite3.connect("immunization.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM children")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()