import streamlit as st
import pandas as pd
import datetime
import sys
import os

# 8️⃣ IMPORT FIX (MANDATORY)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import feature.database.create_tables # Initialize database properly
from feature.database.insert_data import add_child, add_immunization_record
from feature.database.fetch_data import fetch_child_records
from feature.database.database import connect_db

from utils.vaccine_engine import get_vaccine_status
from utils.notifications import prompt_system

st.set_page_config(page_title="Immunization Assistant", page_icon="💉", layout="wide")

# ==================== HELPER FUNCTIONS ====================
@st.cache_data
def fetch_all_children():
    """Retrieve all children from DB"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT child_id, name, dob, gender, parent_name, phone, address FROM children")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        st.error(f"Database conn error: {e}")
        return []
        
    children = []
    for r in rows:
        children.append({
            "child_id": r[0],
            "name": r[1],
            "dob": r[2],
            "gender": r[3],
            "parent_name": r[4],
            "phone": r[5],
            "address": r[6]
        })
    return children

@st.cache_data
def fetch_vaccine_dictionary():
    """Return dict of existing vaccines from DB strictly (no auto-fill)"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT vaccine_id, vaccine_name FROM vaccines")
        rows = cursor.fetchall()
        conn.close()
        return {r[1]: r[0] for r in rows}, {r[0]: r[1] for r in rows}
    except Exception as e:
        return {}, {}

# Cache results per child to minimize DB hits during layout rendering loops
@st.cache_data
def get_child_records_parsed(child_id):
    """Retrieve child records with exact DB names"""
    # Requires dictionary to map vaccine_id natively
    name_to_id, id_to_name = fetch_vaccine_dictionary() 
    
    raw_records = fetch_child_records(child_id)
    records = []
    
    for r in raw_records:
        v_name = id_to_name.get(r[2], "Unknown/Deleted Vaccine")
        status = r[5]
        date_given = r[3]
        records.append({
            "Vaccine": v_name,
            "Date Given": date_given,
            "Status": status,
            "Remarks": r[6]
        })
    return records

def insert_new_vaccine_if_needed(vaccine_name):
    """Insert user-inputted vaccine name dynamically if strictly unavailable, returns ID"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT vaccine_id FROM vaccines WHERE vaccine_name = ?", (vaccine_name,))
    row = cursor.fetchone()
    if row:
        v_id = row[0]
    else:
        cursor.execute("INSERT INTO vaccines (vaccine_name) VALUES (?)", (vaccine_name,))
        conn.commit()
        v_id = cursor.lastrowid
        # Invalidate vaccine dictionary cache when new vaccine is added
        fetch_vaccine_dictionary.clear()
    conn.close()
    return v_id

def calculate_age(dob_str):
    try:
        dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        months = today.month - dob.month - ((today.day) < (dob.day))
        if months < 0:
            months += 12
        return f"{years}y {months}m"
    except Exception:
        return "Unknown"

# ==================== MAIN UI APP ====================
children_list = fetch_all_children()

# System pre-caching for Dashboard / Notifications
records_map = {}
for c in children_list:
    recs = get_child_records_parsed(c['child_id'])
    records_map[c['child_id']] = recs

st.sidebar.title("Smart Dashboard")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Child", "Add Vaccination", "View Records"])

# 1️⃣ Dashboard Panel
if page == "Dashboard":
    st.title("📊 Smart Immunization Dashboard")
    
    if not children_list:
        st.info("👶 No records found. Please add a child first.")
    else:
        prompt_system(children_list, records_map)
        
        st.markdown("---")
        
        # Simple Stats Grid
        cols = st.columns(2)
        cols[0].metric("👶 Total Children Assisting", len(children_list))
        cols[1].metric("💉 Total Logged Vaccinations", sum(len(v) for v in records_map.values()))
        
        st.subheader("Child Timelines & Vaccination Status")
        for child in children_list:
            cid = child['child_id']
            taken_list = [r['Vaccine'] for r in records_map[cid] if r.get('Status', '').lower() in ["completed", "given", "done"]]
            completed, pending, overdue = get_vaccine_status(child['dob'], taken_list)
            
            with st.container():
                c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1.5])
                with c1:
                    st.markdown(f"#### 👶 {child['name']}")
                    st.markdown(f"**Age:** {calculate_age(child['dob'])}")
                    st.markdown(f"**Parent:** {child['parent_name']}  |  **📞** {child['phone']}")
                with c2:
                    st.markdown("##### 💉 Completed")
                    if not completed:
                        st.info("No records")
                    else:
                        for v, _ in completed:
                            st.markdown(f"<span style='color:green'>✔ {v}</span>", unsafe_allow_html=True)
                with c3:
                    st.markdown("##### ⏳ Pending")
                    if not pending:
                         st.info("None")
                    else:
                        for v, d in pending:
                            st.write(f"{v} ({d.strftime('%b %d')})")
                with c4:
                    st.markdown("##### ⚠ Overdue")
                    if not overdue:
                         st.success("✔ None")
                    else:
                        df_overdue = pd.DataFrame([{"Vaccine": v, "Due Date": d.strftime('%Y-%m-%d')} for v, d in overdue])
                        st.dataframe(df_overdue.style.map(lambda _: 'color: red; font-weight: bold'), hide_index=True, use_container_width=True)
                st.divider()

# 2️⃣ Add Child Form
elif page == "Add Child":
    st.title("👶 Add Child Profile")
    
    with st.form("add_child_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child Name *")
            dob = st.date_input("Date of Birth *", max_value=datetime.date.today())
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col2:
            parent_name = st.text_input("Parent Name *")
            phone = st.text_input("Contact Number *")
            address = st.text_area("Address")
            
        st.markdown("*Required fields")
        submit = st.form_submit_button("Save Child Record")
        
        if submit:
            if not name.strip() or not parent_name.strip() or not phone.strip():
                st.error("Please fill in the required fields (Name, Parent Name, Phone).")
            elif dob > datetime.date.today():
                st.error("Date of Birth cannot be in the future.")
            else:
                try:
                    add_child(name.strip(), str(dob), gender, parent_name.strip(), phone.strip(), address.strip())
                    fetch_all_children.clear() # Invalidate cache natively
                    st.success(f"✔ Successfully created profile for {name}!")
                except Exception as e:
                    st.error(f"Database Error: {e}")

# 3️⃣ Add Vaccination Form
elif page == "Add Vaccination":
    st.title("💉 Log Vaccination")
    if not children_list:
        st.warning("No children found. Please add a child first.")
    else:
        child_options = {f"{c['name']} (ID: {c['child_id']})": c['child_id'] for c in children_list}
        selected_child = st.selectbox("Select Child", list(child_options.keys()))
        child_id = child_options[selected_child]
        
        name_to_id, _ = fetch_vaccine_dictionary()
        STANDARD_VACCINES = ["BCG", "Hep B (birth)", "DPT1 (6 weeks)", "DPT2 (10 weeks)", "DPT3 (14 weeks)", "MMR (9 months)"]
        existing_vaccine_names = list(set(list(name_to_id.keys()) + STANDARD_VACCINES))
        use_existing_vaccine = st.selectbox("Select Vaccine", ["Enter New"] + existing_vaccine_names)
        
        if use_existing_vaccine == "Enter New":
            vaccine_name = st.text_input("New Vaccine Name *")
        else:
            vaccine_name = use_existing_vaccine
            
        with st.form("add_vacc_form", clear_on_submit=False):
            date_given = st.date_input("Date Given", max_value=datetime.date.today())
            status = st.selectbox("Status", ["Completed", "Pending", "Missed"])
            remarks = st.text_input("Remarks / Notes")
            
            submit_vacc = st.form_submit_button("Save Vaccine Log")
            
            if submit_vacc:
                if not vaccine_name.strip():
                    st.error("Vaccine name is required.")
                else:
                    v_name_normalized = vaccine_name.strip().lower()
                    taken_normalized = [r['Vaccine'].strip().lower() for r in records_map.get(child_id, []) if r.get('Status', '').lower() in ["completed", "given", "done"]]
                    
                    if v_name_normalized in taken_normalized:
                        st.warning("⚠ Vaccine already securely recorded for this child.")
                    else:
                        try:
                            vaccine_id = insert_new_vaccine_if_needed(vaccine_name.strip())
                            
                            # Next Due Date is auto-calculated placeholder DB entry
                            add_immunization_record(child_id, vaccine_id, str(date_given), "Auto-Calculated", status, remarks)
                            
                            # Cache invalidation for this specific child
                            get_child_records_parsed.clear()
                            st.success(f"✔ Record securely stored for {selected_child.split(' (')[0]}!")
                        except Exception as e:
                            st.error(f"Error: {e}")

# 4️⃣ View Records
elif page == "View Records":
    st.title("📋 Full Vaccination History")
    if not children_list:
        st.info("No records available")
    else:
        search_query = st.text_input("🔍 Search child by name")
        
        filtered_children = children_list
        if search_query:
            filtered_children = [c for c in children_list if search_query.lower() in c['name'].lower()]
            
        if not filtered_children:
            st.info("No records available matching that search.")
            
        for child in filtered_children:
            with st.expander(f"👶 {child['name']} | Parent: {child['parent_name']} | 📞 {child['phone']}", expanded=True):
                st.write(f"**DOB:** {child['dob']} | **Age:** {calculate_age(child['dob'])}")
                
                records = records_map.get(child['child_id'], [])
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(df, hide_index=True, use_container_width=True)
                else:
                    st.info("No DB records available.")
                    
                st.markdown("---")
                st.markdown("**🧠 Smart Assistant Status**")
                taken_list = [r['Vaccine'] for r in records if r.get('Status', '').lower() in ["completed", "given", "done"]]
                completed, pending, overdue = get_vaccine_status(child['dob'], taken_list)
                
                if overdue:
                    st.error(f"⚠ Overdue: {', '.join([v for v, _ in overdue])}")
                if pending:
                    st.warning(f"⏳ Pending Timeline: {', '.join([v for v, _ in pending])}")
                if not overdue and not pending:
                    st.success("✔ Child is 100% up to date on mathematical schedule!")
