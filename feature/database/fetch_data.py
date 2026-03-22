from feature.database.database import connect_db

def fetch_child_records(child_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM immunization_records
    WHERE child_id = ?
    """, (child_id,))

    data = cursor.fetchall()
    conn.close()
    return data