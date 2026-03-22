import datetime
from datetime import timedelta

# IAP Vaccine Schedule (days from DOB)
vaccine_schedule = {
    "BCG": 0,
    "Hep B (birth)": 0,
    "DPT1 (6 weeks)": 42,
    "DPT2 (10 weeks)": 70,
    "DPT3 (14 weeks)": 98,
    "MMR (9 months)": 270
}

def get_vaccine_status(child_dob, taken_vaccines):
    """
    Returns: completed, pending, overdue
    """
    if isinstance(child_dob, str):
        try:
            child_dob = datetime.datetime.strptime(child_dob, "%Y-%m-%d").date()
        except Exception:
            child_dob = datetime.date.today()
    elif isinstance(child_dob, datetime.datetime):
        child_dob = child_dob.date()
    elif not isinstance(child_dob, datetime.date):
        child_dob = datetime.date.today()
        
    today = datetime.datetime.today().date()

    completed = []
    pending = []
    overdue = []

    # Normalize taken vaccines
    taken_vaccines = [str(v).strip().lower() for v in taken_vaccines]

    for vaccine, offset in vaccine_schedule.items():
        due_date = child_dob + timedelta(days=offset)

        if vaccine.lower() in taken_vaccines:
            completed.append((vaccine, due_date))
        else:
            if today < due_date:
                pending.append((vaccine, due_date))
            else:
                overdue.append((vaccine, due_date))

    return completed, pending, overdue
