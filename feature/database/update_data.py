from database import connect_db

def update_record(record_id, status):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE immunization_records
    SET status = ?
    WHERE record_id = ?
    """, (status, record_id))

    conn.commit()
    conn.close()