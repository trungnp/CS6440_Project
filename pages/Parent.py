import re
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import utils
from utils import check_and_send_email, write_schedule_to_csv

st.set_page_config(page_title="CDC Immunization Schedule Reminder", layout="wide")
st.title("CDC Immunization Schedule Reminder")

st.markdown("You are logged in as **Parent**")

client = utils.get_fhir_client()


def is_valid_email(email):
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(regex, email):
        return True
    st.error("Invalid email address. Please enter a valid email.")
    return False


# @st.cache_data(ttl=600)
def search_immunization_schedule(patient_id):
    schedule = client.resources('ImmunizationRecommendation').search(patient=patient_id).fetch()
    res = [s.serialize() for s in schedule]
    return res


patient = utils.render_search_patient_form()

if patient:
    schedule = search_immunization_schedule(patient['id'])
    # st.write(schedule)
    if not schedule:
        st.error("No Immunization Schedule found for the selected Patient.")
    else:
        schedule_as_dict = [
            {
                "vaccine": rec["vaccineCode"][0]["coding"][0]["display"],
                "disease": rec["targetDisease"]["coding"][0]["display"],
                "description": rec["description"],
                "recommended_date": ' - '.join([i['value'].replace('-', '/') for i in rec["dateCriterion"]]),
                "dose": rec["doseNumberPositiveInt"],
                "series": rec["seriesDosesPositiveInt"],
            }
            for _schedule in schedule for rec in _schedule["recommendation"]
        ]

        schedule_tab, health_record_tab = st.tabs(["Immunization Schedule", "Health Record Chart"])
        with schedule_tab:
            st.header("Immunization Recommendation Schedule")
            ident_col, patient_col, first_col, last_col, dob_col, date_col = st.columns(6)
            with ident_col:
                st.markdown(f'Group Identifier: **{schedule[0]["identifier"][0]["value"]}**', unsafe_allow_html=True)
            with patient_col:
                st.write(f'Patient: **{schedule[0]["patient"]["reference"]}**')
            with first_col:
                st.write(f'Patient First Name: **{patient["name"][0]["given"][0]}**')
            with last_col:
                st.write(f'Patient Last Name: **{patient["name"][0]["family"]}**')
            with dob_col:
                st.write(f'Patient DOB: **{patient["birthDate"]}**')
            with date_col:
                st.write(f'Created Date: **{schedule[0]["date"]}**')

            df = pd.DataFrame(schedule_as_dict).sort_values("recommended_date")
            st.dataframe(df, hide_index=True)
            with st.form(key='reminder_form'):
                e_label, email_col, d_label, d_col, send_btn = st.columns([3, 6, 0.7, 0.5, 1])
                with e_label:
                    st.write("Enter email to get notification of upcoming schedule:")
                with email_col:
                    email = st.text_input("Email Address", placeholder="example@gmail.com", label_visibility='collapsed')
                with d_label:
                    st.write("Before (Day):")
                with d_col:
                    day_ahead = st.number_input("Send Reminder Before (Day, Min = 3, Max = 30)", min_value=3, max_value=30, value=3, label_visibility='collapsed')
                with send_btn:
                    send = st.form_submit_button("Follow Schedule")
                if send:
                    if is_valid_email(email) and day_ahead:
                        df['patient_id'] = patient['id']
                        df['email'] = email
                        df['is_sent'] = False
                        df['first_day_to_get'] = df['recommended_date'].apply(lambda x: datetime.strptime(x.split(" - ")[0], "%Y/%m/%d"))
                        df['date_to_send'] = df['first_day_to_get'].apply(lambda x: x - timedelta(days=day_ahead))
                        df['date_to_send'] = df['date_to_send'].dt.strftime('%Y/%m/%d')
                        df = df.drop(columns=['first_day_to_get'])
                        write_schedule_to_csv(df)
                        st.success("Followed successfully!")
                        check_and_send_email()
                    else:
                        st.error("Please enter your email and number of days ahead to follow schedule.")
        with health_record_tab:
            utils.render_health_record_charts(patient['id'])
