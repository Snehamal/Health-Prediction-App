"""pyth
app.py
-------
Streamlit frontend for the Health Prediction Application.

Why Streamlit?
- Pure Python end-to-end (matches the "AI/ML developer" brief well).
- Lets us focus the review on data modeling, validation, and the
  ML/API integration rather than boilerplate HTML/CSS/JS.
- Built-in widgets (forms, dataframes, dialogs) make CRUD fast to build
  and easy to read.

Run with: streamlit run app.py
"""

from datetime import date, datetime

import pandas as pd
import streamlit as st

import database as db
from validators import validate_patient_form
from predictor import predict_remarks

st.set_page_config(page_title="Health Prediction App", page_icon="🩺", layout="wide")

# Ensure the patients table exists before anything else runs.
db.init_db()


def reset_form_state():
    st.session_state.editing_id = None


if "editing_id" not in st.session_state:
    st.session_state.editing_id = None


st.title("🩺 Health Prediction Application")
st.caption(
    "Enter a patient's blood test results to store their record and generate an "
    "AI-based health remark automatically."
)

tab_form, tab_records = st.tabs(["➕ Add / Edit Patient", "📋 Patient Records"])

# ---------------------------------------------------------------------------
# TAB 1: Create / Update form
# ---------------------------------------------------------------------------
with tab_form:
    editing_record = None
    if st.session_state.editing_id is not None:
        editing_record = db.get_patient_by_id(st.session_state.editing_id)
        st.info(f"Editing record #{st.session_state.editing_id} — {editing_record['full_name']}")

    with st.form("patient_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Name",
                value=editing_record["full_name"] if editing_record else "",
            )
            dob = st.date_input(
                "Date of Birth",
                value=(
                    datetime.strptime(editing_record["date_of_birth"], "%Y-%m-%d").date()
                    if editing_record else date(2000, 1, 1)
                ),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )
            email = st.text_input(
                "Email Address",
                value=editing_record["email"] if editing_record else "",
            )

        with col2:
            glucose = st.number_input(
                "Glucose (mg/dL)",
                min_value=0.0,
                max_value=1000.0,
                value=float(editing_record["glucose"]) if editing_record else 90.0,
                step=0.1,
            )
            haemoglobin = st.number_input(
                "Haemoglobin (g/dL)",
                min_value=0.0,
                max_value=30.0,
                value=float(editing_record["haemoglobin"]) if editing_record else 13.5,
                step=0.1,
            )
            cholesterol = st.number_input(
                "Cholesterol (mg/dL)",
                min_value=0.0,
                max_value=1000.0,
                value=float(editing_record["cholesterol"]) if editing_record else 180.0,
                step=0.1,
            )

        submit_label = "Update Patient" if editing_record else "Save Patient & Generate Remarks"
        submitted = st.form_submit_button(submit_label, type="primary")

    if submitted:
        is_valid, errors = validate_patient_form(full_name, dob, email, glucose, haemoglobin, cholesterol)

        if not is_valid:
            for err in errors:
                st.error(err)
        else:
            with st.spinner("Generating AI health remark..."):
                remarks = predict_remarks(glucose, haemoglobin, cholesterol)

            if editing_record:
                db.update_patient(
                    st.session_state.editing_id, full_name, dob, email,
                    glucose, haemoglobin, cholesterol, remarks,
                )
                st.success(f"Record #{st.session_state.editing_id} updated successfully.")
                st.session_state.editing_id = None
            else:
                new_id = db.create_patient(
                    full_name, dob, email, glucose, haemoglobin, cholesterol, remarks
                )
                st.success(f"Patient saved (record #{new_id}).")

            st.info(f"**AI Remark:** {remarks}")
            st.rerun()

    if editing_record and st.button("Cancel Edit"):
        reset_form_state()
        st.rerun()

# ---------------------------------------------------------------------------
# TAB 2: Read / Update / Delete records
# ---------------------------------------------------------------------------
with tab_records:
    records = db.get_all_patients()

    if not records:
        st.info("No patient records yet. Add one in the first tab.")
    else:
        df = pd.DataFrame(records)
        df_display = df.rename(columns={
            "id": "ID",
            "full_name": "Full Name",
            "date_of_birth": "Date of Birth",
            "email": "Email",
            "glucose": "Glucose",
            "haemoglobin": "Haemoglobin",
            "cholesterol": "Cholesterol",
            "remarks": "Remarks (AI)",
            "created_at": "Created At",
        })

        search = st.text_input("🔍 Search by name or email")
        if search:
            mask = (
                df_display["Full Name"].str.contains(search, case=False, na=False)
                | df_display["Email"].str.contains(search, case=False, na=False)
            )
            df_display = df_display[mask]

        st.dataframe(
            df_display[["ID", "Full Name", "Date of Birth", "Email", "Glucose",
                        "Haemoglobin", "Cholesterol", "Remarks (AI)"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("Manage a record")

        record_ids = df_display["ID"].tolist()
        selected_id = st.selectbox("Select record ID", record_ids)

        col_edit, col_delete = st.columns(2)
        with col_edit:
            if st.button("✏️ Edit selected record"):
                st.session_state.editing_id = int(selected_id)
                st.rerun()

        with col_delete:
            if st.button("🗑️ Delete selected record", type="secondary"):
                db.delete_patient(int(selected_id))
                st.success(f"Record #{selected_id} deleted.")
                st.rerun()
