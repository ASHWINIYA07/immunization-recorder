from feature.database.database import connect_db

def add_child(name, dob, gender, parent_name, phone, address):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO children (name, dob, gender, parent_name, phone, address)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, dob, gender, parent_name, phone, address))

    conn.commit()
    conn.close()


def add_immunization_record(child_id, vaccine_id, date_given, next_due_date, status, remarks):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO immunization_records (child_id, vaccine_id, date_given, next_due_date, status, remarks)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (child_id, vaccine_id, date_given, next_due_date, status, remarks))

    conn.commit()
    conn.close()