import streamlit as st
from fhirpy import SyncFHIRClient

st.set_page_config(page_title="CDC Immunization Schedule Reminder", layout="wide")

st.title("CDC Immunization Schedule Reminder")
st.markdown("*Please Choose a Role In Sidebar to Continue*")