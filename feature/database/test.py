from create_tables import create_tables
from insert_data import add_child

# Create tables first
create_tables()

# Then insert data
add_child("Rahul", "2025-01-12", "Male", "Suresh", "9876543210", "Coimbatore")

print("Data inserted successfully!")