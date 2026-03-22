import streamlit as st
import datetime
from utils.vaccine_engine import get_vaccine_status

def prompt_system(children, records_by_child):
    """
    Live notification system evaluating the exact DOB against the rules.
    Priority: Overdue UI -> Pending UI.
    """
    if not children:
        return
        
    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)
    
    # Pre-aggregate by status to ensure printing order
    overdue_alerts = []
    pending_alerts = []
    
    for child in children:
        dob_str = child['dob']
        c_name = child['name']
        c_id = child['child_id']
        
        # Map actual taken vaccines to list of strings
        taken_vaccines = [r['Vaccine'] for r in records_by_child.get(c_id, []) if r.get("Status", "").lower() in ["completed", "given", "done"]]
        
        _, pending, overdue = get_vaccine_status(dob_str, taken_vaccines)
        
        for vaccine, due_date in overdue:
            # deduplicate logic inherently handled by get_vaccine_status
            overdue_alerts.append(f"Missed vaccine: {c_name}'s {vaccine} was due on {due_date.strftime('%Y-%m-%d')}")
            
        for vaccine, due_date in pending:
            if today <= due_date <= next_week:
                pending_alerts.append(f"Upcoming vaccine: {c_name}'s {vaccine} due on {due_date.strftime('%Y-%m-%d')}")
                
    # 1. Show Overdues strictly first
    for alert in overdue_alerts:
        st.error(alert)
        
    # 2. Show Pending strictly second
    for alert in pending_alerts:
        st.warning(alert)
                
    # 3. If zero overdues and zero 7-day warnings, print success
    if not overdue_alerts and not pending_alerts:
        st.success("✔ All vaccinations up to date")
