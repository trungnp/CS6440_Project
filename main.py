import streamlit as st
from fhirpy import SyncFHIRClient

st.set_page_config(page_title="CDC Immunization Schedule Reminder", layout="wide")
# FHIR server setup
# FHIR_SERVER_URL = "https://hapi.fhir.org/baseR4"  # Local HAPI instance
# client = SyncFHIRClient('https://hapi.fhir.org/baseR4')
# if 'client' not in st.session_state:
#     st.session_state.client = client