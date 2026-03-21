from datetime import datetime, timedelta

VACCINE_SCHEDULE = {
    "BCG": 0,
    "Hepatitis B": 0,
    "DTP 1": 42,
    "DTP 2": 70,
    "DTP 3": 98,
    "Measles": 270
}

def calculate_due_date(dob, vaccine_name):
    days = VACCINE_SCHEDULE[vaccine_name]
    return dob + timedelta(days=days)

def check_vaccination_status(child):
    dob = datetime.strptime(child["dob"], "%Y-%m-%d")
    given_vaccines = child["vaccines"]

    status = {}

    for vaccine in VACCINE_SCHEDULE:
        due_date = calculate_due_date(dob, vaccine)

        if vaccine in given_vaccines:
            status[vaccine] = "Completed"
        else:
            today = datetime.today()
            if today > due_date:
                status[vaccine] = "Missed"
            else:
                status[vaccine] = "Due"

    return status
