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
    # Regular expression for validating an email
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

# patient = None
# patient_l, patient_r = st.columns([1, 3])
# with patient_l:
#     has_patient_id = st.radio("Do you have a Patient ID?", ["Yes", "No"], index=0, horizontal=True)
# with patient_r:
#     if has_patient_id == "Yes":
#         with st.form(key='patient_form'):
#             patient_id = st.text_input("Enter Patient ID")
#             submit_patient = st.form_submit_button("Search Patient")
#             if submit_patient:
#                 if patient_id:
#                     patient = search_patient(id=patient_id)
#                     if not patient:
#                         st.error("No Patients found with the given ID.")
#                     else:
#                         patient = patient[0]
#                 else:
#                     st.error("Please enter a Patient ID.")
#     else:
#         patients = search_patient()
#         patients_ids = [patient["id"] for patient in patients]
#         patient = st.selectbox("Select Patient (for testing purpose)", patients_ids)
#         patient = patients[patients_ids.index(patient)]

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
        st.header("Immunization Recommendation Schedule")
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
        # events1 = []
        # for _, row in df.iterrows():
        #     date_range = row["recommended_date"].replace("/", "-").split(" - ")
        #     events1.append({
        #         "title": row['vaccine'],
        #         "start": date_range[0] + "T00:00:00",
        #         "end": date_range[1] + "T23:59:59" if len(date_range) > 1 else date_range[0] + "T23:59:59",
        #         "description": row["description"],
        #         "allDay": True,
        #         "extendedProps": {
        #             "disease": row["disease"],
        #             "dose": row["dose"],
        #             "series": row["series"],
        #             "description": row["description"]
        #         }
        #     })
        # utils.display_calendar(events)
        # scheule_view_mode = st.selectbox("View Mode", ["Table", "Calendar"], index=1)
        # if scheule_view_mode == "Table":
        # st.dataframe(df, hide_index=True)
        # else:
        # st.write(events1)
        # display_calendar(events1)
        schedule, health_record = st.tabs(["Immunization Schedule", "Health Record Chart"])
        with schedule:
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

                        # st.write(f"Schedule for {email} (Notifications {day_ahead} days ahead):")
                        # current_date = datetime.now().date()
                        #
                        # for _, entry in df.iterrows():
                        #     vaccine_name = entry["vaccine"]
                        #     if '-' in entry["recommended_date"]:
                        #         date_to_get = datetime.strptime(entry["recommended_date"].split(" - ")[0], "%Y-%m-%d").date()
                        #     else:
                        #         date_to_get = datetime.strptime(entry["recommended_date"], "%Y-%m-%d").date()
                        #     dose = entry["dose"]
                        #     notification_date = date_to_get - timedelta(days=day_ahead)
                        #
                        #     st.write(f"- **{vaccine_name}**: {date_to_get} (Dose: {dose})")
                        #     st.write(f"  Notification date: {notification_date}")
                        #
                        #     # Check if today is the notification date
                        #     if current_date == notification_date:
                        #         result = follow(email, vaccine_name, entry["date_to_get"], dose)
                        #         if result is True:
                        #             st.success(f"Reminder email sent to {email} for {vaccine_name}!")
                        #         else:
                        #             st.error(f"Failed to send email: {result}")
                        #     elif current_date < notification_date:
                        #         st.write(f"  Reminder will be available on {notification_date}")
                        #     else:
                        #         st.write(f"  Notification date has passed")
                    else:
                        st.error("Please enter your email and number of days ahead to follow schedule.")
        with health_record:
            st.write("Health Record Chart")
