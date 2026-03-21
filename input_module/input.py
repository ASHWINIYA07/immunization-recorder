import sys
import os

# Database module path add pannrom
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "feature", "database")
    )
)

from insert_data import add_child
from create_tables import create_tables


def get_child_details():
    name = input("Enter child name: ")
    dob = input("Enter DOB (YYYY-MM-DD): ")
    gender = input("Enter gender: ")
    parent_name = input("Enter parent name: ")
    phone = input("Enter phone number: ")
    address = input("Enter address: ")

    return name, dob, gender, parent_name, phone, address


def main():
    print("=== Child Registration Module ===")

    # Tables create aagattum
    create_tables()

    # User kitta data வாங்குறது
    child_data = get_child_details()

    # Database la save pannradhu
    add_child(*child_data)

    print("Data saved successfully!")


if __name__ == "__main__":
    main()