from database import connect_db

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS children (
        child_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        gender TEXT,
        parent_name TEXT,
        phone TEXT,
        address TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vaccines (
        vaccine_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vaccine_name TEXT,
        recommended_age TEXT,
        dose_no INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS immunization_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        child_id INTEGER,
        vaccine_id INTEGER,
        date_given TEXT,
        next_due_date TEXT,
        status TEXT,
        remarks TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()