from datetime import datetime, timedelta

# -------------------------------
# 1. AGE-BASED SCHEDULE (months)
# -------------------------------
AGE_SCHEDULE = {
    0: ["BCG", "Hepatitis B-1"],
    1: ["Hepatitis B-2"],
    2: ["DTP-1", "Polio-1"],
    4: ["DTP-2", "Polio-2"],
    6: ["DTP-3", "Polio-3"],
    9: ["Measles"]
}

# -------------------------------
# 2. DATE-BASED SCHEDULE (days)
# -------------------------------
DATE_SCHEDULE = {
    "BCG": 0,
    "Hepatitis B-1": 0,
    "Hepatitis B-2": 30,
    "DTP-1": 42,
    "Polio-1": 42,
    "DTP-2": 70,
    "Polio-2": 70,
    "DTP-3": 98,
    "Polio-3": 98,
    "Measles": 270
}

# -------------------------------
# 3. CALCULATE AGE
# -------------------------------
def calculate_age_in_months(dob):
    today = datetime.today()
    dob = datetime.strptime(dob, "%Y-%m-%d")

    return (today.year - dob.year) * 12 + (today.month - dob.month)

# -------------------------------
# 4. REQUIRED VACCINES (AGE)
# -------------------------------
def get_required_vaccines(age):
    required = []
    for month in AGE_SCHEDULE:
        if age >= month:
            required.extend(AGE_SCHEDULE[month])
    return required

# -------------------------------
# 5. MISSING VACCINES
# -------------------------------
def get_missing_vaccines(given, required):
    return [v for v in required if v not in given]

# -------------------------------
# 6. UPCOMING VACCINES
# -------------------------------
def get_upcoming_vaccines(age):
    for month in sorted(AGE_SCHEDULE):
        if month > age:
            return AGE_SCHEDULE[month]
    return []

# -------------------------------
# 7. DATE STATUS (Due/Missed)
# -------------------------------
def get_date_status(dob, vaccine, given):
    dob = datetime.strptime(dob, "%Y-%m-%d")
    due_date = dob + timedelta(days=DATE_SCHEDULE[vaccine])
    today = datetime.today()

    if vaccine in given:
        return "Completed"
    elif today > due_date:
        return "Missed"
    else:
        return "Due"

# -------------------------------
# 8. FINAL TRACKING FUNCTION
# -------------------------------
def generate_full_report(child):
    age = calculate_age_in_months(child["dob"])
    given = child["vaccines"]

    required = get_required_vaccines(age)
    missing = get_missing_vaccines(given, required)
    upcoming = get_upcoming_vaccines(age)

    print(f"\n👶 Child: {child['name']}")
    print(f"📅 Age: {age} months")

    print("\n📊 Vaccine Status:")
    for vaccine in DATE_SCHEDULE:
        status = get_date_status(child["dob"], vaccine, given)
        print(f"{vaccine}: {status}")

    print("\n⚠️ Missing Vaccines:")
    if missing:
        for v in missing:
            print(f"👉 {v} is pending")
    else:
        print("✅ None")

    print("\n📅 Upcoming Vaccines:")
    if upcoming:
        for v in upcoming:
            print(f"👉 {v}")
    else:
        print("✅ No upcoming vaccines")

# -------------------------------
# 9. TEST
# -------------------------------
if __name__ == "__main__":
    child = {
        "name": "Baby A",
        "dob": "2025-09-01",
        "vaccines": ["BCG", "Hepatitis B-1"]
    }

    generate_full_report(child)
