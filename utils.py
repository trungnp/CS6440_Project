import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from fhirpy import SyncFHIRClient


def get_fhir_client():
    if 'client' not in st.session_state:
        st.session_state.client = SyncFHIRClient('https://hapi.fhir.org/baseR4')

    return st.session_state.client


client = get_fhir_client()


def is_over_18(dob: datetime):
    # Current date: March 19, 2025
    current_date = datetime.now()

    try:
        # Parse the DOB string (assuming format YYYY-MM-DD)
        # dob = datetime.strptime(dob_str, '%Y-%m-%d')

        # Calculate age
        age = current_date.year - dob.year

        # Adjust age if birthday hasn't occurred this year
        if (current_date.month, current_date.day) < (dob.month, dob.day):
            age -= 1

        # Check if under 18
        return age >= 18

    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD"


@st.cache_data(ttl=600)
def search_patient(count=10, under_age=18, id=None, first_name=None, last_name=None, dob: datetime = None):
    """
    Fetch all patients under 5 years old using FHIR search
    """
    # if under_age > 18:
    #     st.error("Only patients under 18 years old are supported.")
    #     return
    #
    # if dob and is_over_18(dob):
    #     st.error("Patient is over 18 years old.")
    #     return

    if id is None and first_name is None and last_name is None and dob is None:
        params = {
            "birthdate": f"gt{(datetime.now() - timedelta(days=under_age * 365)).strftime('%Y-%m-%d')}"
        }
    elif id is not None:
        params = {
            "_id": id
        }
    elif first_name is not None and last_name is not None and dob is not None:
        params = {
            "given": first_name,
            "family": last_name,
            "birthdate": dob,
        }
    else:
        st.error("Invalid parameters. Please provide either ID or First Name, Last Name, and DOB.")
        st.stop()

    patients = client.resources('Patient').search(**params).limit(count).fetch()
    # patients = client.resources('Patient').search(birthdate=f'gt{five_years_ago}').limit(count).fetch()
    patients_list = [patient.serialize() for patient in patients]

    return patients_list


def display_calendar(events):
    colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFF5", "#FF8C33", "#8CFF33", "#338CFF", "#FF338C"]
    date_to_events = {}

    for event in events:
        event_date = event["start"].split("T")[0]
        if event_date not in date_to_events:
            date_to_events[event_date] = []
        date_to_events[event_date].append(event)

    for event_date, events_on_date in date_to_events.items():
        for i, event in enumerate(events_on_date):
            event["color"] = colors[i % len(colors)]
            # start_date = event["start"].split("T")[0]
            # end_date = event["end"].split("T")[0]
            # if start_date != end_date:
            #     event["classNames"] = ["event-range", "event-start", "event-end"]
            # event["startClassNames"] = ["event-start"]
            # event["endClassNames"] = ["event-end"]

    options = {
        # "editable": True,
        "selectable": True,
        # "headerToolbar": {
        #     # "left": "prev,next",
        #     # "center": "title",
        #     # "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
        # },
        # "slotMinTime": "06:00:00",
        # "slotMaxTime": "18:00:00",
        "initialView": "multiMonthYear",
        # "dayMaxEventRows": 3,
        # "size": "1000x300",
        "height": "550px",
        # "months": 4,
    }

    custom_css = """
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """

    cld = calendar(
        events=events,
        options=options,
        custom_css=custom_css,
        key='calendar',  # Assign a widget key to prevent state loss
    )

    st.write(cld)


def send_email(to_email, vaccine_name, date_to_get, dose):
    brevo_info = st.secrets["email"]
    SENDER = brevo_info["SENDER"]
    PWD = brevo_info["PWD"]
    SENDER_EMAIL = brevo_info["SENDER_EMAIL"]
    SENDER_PASSWORD = brevo_info["SENDER_PASSWORD"]
    SMTP_SERVER = brevo_info["SMTP_SERVER"]
    SMTP_PORT = brevo_info["SMTP_PORT"]
    subject = f"Upcoming Immunization Reminder: {vaccine_name}"
    body = f"""
    Dear User,

    This is a reminder for your upcoming immunization:
    - Vaccine: {vaccine_name}
    - Date: {date_to_get}
    - Dose: {dose}

    Please schedule your appointment if you haven’t already.
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER, PWD)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)


def write_schedule_to_csv(df):
    try:
        current_schedule = pd.read_csv("schedule.csv", header=0)
    except pd.errors.EmptyDataError:
        df.to_csv("schedule.csv", index=False)
        return

    if current_schedule.shape[0] > 0:
        # new_patient = tuple(df[['patient_id', 'email']].values[0])
        # patient_found = False
        # for _, row in current_schedule[['patient_id', 'email']].drop_duplicates().iterrows():
        #     if (row['patient_id'], row['email']) == new_patient:
        #         patient_found = True
        #         break
        #
        # if patient_found:
        #     current_schedule = current_schedule[
        #         (current_schedule['patient_id'] != new_patient[0]) |
        #         (current_schedule['email'] != new_patient[1])
        #         ]

        new_email = df['email'].values[0]
        if new_email in current_schedule['email'].values:
            current_schedule = current_schedule[current_schedule['email'] != new_email]
        df = pd.concat([current_schedule, df], ignore_index=True)
    df.to_csv("schedule.csv", index=False, header=True)


# Run every 3 hours
@st.fragment(run_every=10800)
def check_and_send_email():
    df = pd.read_csv("schedule.csv", header=0)
    df = df[df["is_sent"] is False]
    current_date = datetime.now().date()
    for idx, entry in df.iterrows():
        dose = entry["dose"]
        vaccine_name = entry["vaccine"]
        notification_date = entry["date_to_send"]
        notification_date = datetime.strptime(notification_date, "%Y/%m/%d").date()
        email = entry["email"]

        # st.write(f"- **{vaccine_name}**: {date_to_get} (Dose: {dose})")
        # st.write(f"  Notification date: {notification_date}")

        # Check if today is the notification date
        if current_date >= notification_date and not entry["is_sent"]:
            result = send_email(email, vaccine_name, entry["date_to_send"], dose)
            if result is True:
                df.loc[idx, "is_sent"] = True
                df.to_csv("schedule.csv", index=False, header=True)
                st.success(f"Reminder email sent to {email} for {vaccine_name}!")
                # st.stop()
            else:
                st.error(f"Failed to send email: {result}")
        #     if result is True:
        #         st.success(f"Reminder email sent to {email} for {vaccine_name}!")
        #     else:
        #         st.error(f"Failed to send email: {result}")
        # elif current_date < notification_date:
        #     st.write(f"  Reminder will be available on {notification_date}")
        # else:
        #     st.write(f"  Notification date has passed")

@st.cache_data(ttl=600)
def search_practitioner(id=None):
    """
    Search for practitioners by name or identifier.

    :param _id: The id of the practitioner.
    """
    search_params = {}
    if id:
        search_params['_id'] = id

    practitioners = client.resources('Practitioner').search(**search_params).limit(10).fetch()
    if practitioners:
        practitioner_ids = [practitioner['id'] for practitioner in practitioners]
        return practitioner_ids
    return []


def read_schedule_from_csv():
    try:
        return pd.read_csv("schedule.csv", header=0)
    except pd.errors.EmptyDataError:
        return None
    except FileNotFoundError:
        return None


def render_search_patient_form():
    patient = None
    patient_l, patient_r = st.columns([0.5, 3.5])
    with patient_l:
        has_patient_id = st.radio("Do you have a Patient ID?", ["Yes", "No"], index=0, horizontal=True)
    with patient_r:
        if has_patient_id == "Yes":
            with st.form(key='patient_form'):
                patient_id = st.text_input("Enter Patient ID")
                st.markdown("OR")
                f, l, d = st.columns(3)
                with f:
                    f_name = st.text_input("First Name")
                with l:
                    l_name = st.text_input("Last Name")
                with d:
                    dob = st.date_input(label="Date of Birth", min_value=datetime(1900, 1, 1), max_value=datetime.now(), value=None)
                submit_patient = st.form_submit_button("Search Patient")
                if submit_patient:
                    if patient_id and (f_name or l_name or dob):
                        st.error("Please search by either Patient ID or First Name, Last Name, and DOB.")
                        st.stop()
                    elif patient_id:
                        patient = search_patient(id=patient_id)
                        if not patient:
                            st.error("No Patients found with the given ID.")
                            st.stop()
                        else:
                            patient = patient[0]
                    elif f_name and l_name and dob:
                        patient = search_patient(first_name=f_name, last_name=l_name, dob=dob)
                        if not patient:
                            st.error("No Patients found with the given information.")
                            st.stop()
                        else:
                            patient = patient[0]
        else:
            patients = search_patient()
            patients_ids = [patient["id"] for patient in patients]
            patient = st.selectbox("Select Patient (for testing purpose)", patients_ids)
            patient = patients[patients_ids.index(patient)]

    return patient


def render_search_practitioner_form():
    practitioner_id = None if 'practitioner_id' not in st.session_state else st.session_state['practitioner_id']
    pract_l, pract_r = st.columns([0.5, 3.5])
    with pract_l:
        idx = 0 if practitioner_id else 1
        has_practitioner_id = st.radio("Do you have a Practitioner ID?", ["Yes", "No"], index=idx, horizontal=True)
    with pract_r:
        if has_practitioner_id == "Yes":
            with st.form(key='practitioner_form'):
                practitioner_id_input = st.text_input("Enter Practitioner ID")
                submit_practitioner = st.form_submit_button("Search Practitioner")
                if submit_practitioner:
                    if practitioner_id_input:
                        practitioner_id = search_practitioner(practitioner_id_input)
                        st.session_state['practitioner_id'] = practitioner_id
                        if not practitioner_id:
                            st.error("No Practitioner found with the given ID.")
                            st.stop()
                    else:
                        st.error("Please enter a Practitioner ID.")
                        st.stop()
        else:
            practitioner_ids = search_practitioner()
            practitioner_id = st.selectbox("Select Practitioner ID (for testing purpose)", practitioner_ids)

    st.session_state['practitioner_id'] = practitioner_id