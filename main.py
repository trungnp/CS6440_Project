import streamlit as st
from fhirpy import SyncFHIRClient

st.set_page_config(page_title="CDC Immunization Schedule Reminder", layout="wide")
# FHIR server setup
# FHIR_SERVER_URL = "https://hapi.fhir.org/baseR4"  # Local HAPI instance
client = SyncFHIRClient('https://hapi.fhir.org/baseR4')
if 'client' not in st.session_state:
    st.session_state.client = client

# CDC group identifier
# CDC_GROUP_IDENTIFIER = {
#     "value": "pnguyen332"
# }
#
# # Simplified CDC immunization schedule data
# cdc_schedule = [
#     {
#         "vaccine": "Covid-19",
#         "cvx": "311",  # COVID-19, mRNA, LNP-Spike Protein
#         "disease": "COVID-19",
#         "total_series": 2,
#         "vaccine_info": "The COVID-19 vaccine helps protect you by teaching your body how to recognize and fight the virus that causes COVID-19. The vaccine is safe and effective. It is one of the best ways to protect yourself and others from the virus.",
#         "doses": [
#             {"dose": 1, "age": "6M-18Y", "series": 1, "description": "CDC recommends COVID-19 vaccination for everyone aged 6 months and older."},
#         ]
#     },
#     {
#         "vaccine": "RSV",
#         "cvx": "307",  # RSV, unspecified formulation
#         "disease": "Respiratory syncytial virus",
#         "total_series": 1,
#         "vaccine_info": "RSV is a common cause of severe respiratory illness in infants and young children. Those infected with RSV can have difficulty breathing and eating, and sometimes may need respiratory support or hydration in the hospital. An RSV immunization uses monoclonal antibodies to protect infants and young children from severe RSV disease. This immunization gives your baby's body extra help to fight an RSV infection. Infants younger than 8 months old during RSV season (typically fall through spring) should get a one-dose RSV immunization to protect them against RSV. This dose should be given shortly before or during the RSV season.",
#         "doses": [
#             {"dose": 1, "age": "0M", "series": 1, "description": "at birth"}
#         ]
#     },
#     {
#         "vaccine": "Hep B, adolescent or pediatric",
#         "cvx": "08",  # Hepatitis B vaccine, pediatric
#         "disease": "Type B viral hepatitis",
#         "total_series": 3,
#         "vaccine_info": "Hepatitis B is an infectious and potentially serious disease that can cause liver damage and liver cancer. If babies are infected at birth, hepatitis B can be a lifelong, chronic infection. There is no cure for hepatitis B, but the hepatitis B vaccine is the best way to prevent it.",
#         "doses": [
#             {"dose": 1, "age": "0M", "series": 3, "description": "at birth ", },
#             {"dose": 2, "age": "1M-2M", "series": 3, "description": "at least 4 weeks after 1st dose", },
#             {"dose": 3, "age": "6M-18M", "series": 3, "description": "at least 8 weeks after 2nd dose and 16 weeks after 1st dose"}
#         ]
#     },
#     {
#         "vaccine": "rotavirus, pentavalent",
#         "cvx": "116",  # Rotavirus, pentavalent (RotaTeq; 119 for Rotarix, 2-dose)
#         "disease": "Viral gastroenteritis caused by Rotavirus (disorder)",
#         "total_series": 3,
#         "vaccine_info": "Rotavirus can be very dangerous, even deadly for babies and young children. Doctors recommend that your child get two or three doses of the rotavirus vaccine (depending on the brand).",
#         "doses": [
#             {"dose": 1, "age": "2M", "series": 3, "description": "Minium age: 6 weeks"},
#             {"dose": 2, "age": "4M", "series": 3, "description": "at least 4 weeks after 1st dose"},
#             {"dose": 3, "age": "6M", "series": 3, "description": "at least 4 weeks after 2nd dose"}
#         ]
#     },
#     {
#         "vaccine": "DTaP",
#         "cvx": "107",  # DTaP, unspecified formulation
#         "disease": "diphtheria, tetanus toxoids and acellular pertussis vaccine, unspecified formulation",
#         "total_series": 5,
#         "vaccine_info": "A DTaP vaccine is the best protection from three serious diseases: diphtheria, tetanus, and whooping cough (pertussis). All three of these diseases can be deadly for people of any age, and whooping cough is especially dangerous for babies.",
#         "doses": [
#             {"dose": 1, "age": "2M", "series": 5, "description": "Minimum age: 6 weeks"},
#             {"dose": 2, "age": "4M", "series": 5, "description": "at least 4 weeks after 1st dose"},
#             {"dose": 3, "age": "6M", "series": 5, "description": "at least 4 weeks after 2nd dose"},
#             {"dose": 4, "age": "15M-18M", "series": 5, "description": "at least 6 months after 3rd dose"},
#             {"dose": 5, "age": "4Y-6Y", "series": 5, "description": "at least 4 years after 4th dose. A fifth dose is not necessary if the fourth dose was administered at age 4 years or older and at least 6 months after dose 3"}
#         ]
#     },
#     {
#         "vaccine": "Hib",
#         "cvx": "49",  # Hib, unspecified formulation (could vary by brand: e.g., 49 for PedvaxHIB)
#         "disease": "Haemophilus influenzae type b",
#         "total_series": 4,
#         "vaccine_info": "Hib disease is a serious illness caused by the bacteria Haemophilus influenzae type b (Hib). Babies and children younger than 5 years old are most at risk for Hib disease. It can cause lifelong disability and be deadly. Doctors recommend that your child get three or four doses of the Hib vaccine (depending on the brand).",
#         "doses": [
#             {"dose": 1, "age": "2M", "series": 4, "description": "Minimum age: 6 weeks"},
#             {"dose": 2, "age": "4M", "series": 4, "description": "No further doses needed if first dose was administered at age 15 months or older. 4 weeks if first dose was administered before the 1st birthday. 8 weeks (as final dose) if first dose was administered at age 12 through 14 months"},
#             {"dose": 3, "age": "6M", "series": 4,
#              "description": "No further doses needed if previous dose was administered at age 15 months or older. 4 weeks if current age is younger than 12 months and first dose was administered at younger than age 7 months and at least 1 previous dose was PRP-T (ActHib, Pentacel, Hiberix), Vaxelis or unknown. 8 weeks and age 12 through 59 months (as final dose) if current age is younger than 12 months and first dose was administered at age 7 through 11 months; OR if current age is 12 through 59 months and first dose was administered before the 1st birthday and second dose was administered at younger than 15 months; OR if both doses were PedvaxHIB and were administered before the 1st birthday"},
#             {"dose": 4, "age": "12M-15M", "series": 4, "description": "at least 8 weeks (as final dose) after 3rd dose. This dose only necessary for children age 12 through 59 months who received 3 doses before the 1st birthday."}
#         ]
#     },
#     {
#         "vaccine": "PCV",
#         "cvx": "216",  # PCV20 (updated for 2025; PCV15 is 152)
#         "disease": "Pneumococcal conjugate",
#         "total_series": 4,
#         "vaccine_info": "Pneumococcal disease can cause potentially serious and even deadly infections. The pneumococcal conjugate vaccine protects against the bacteria that cause pneumococcal disease.",
#         "doses": [
#             {"dose": 1, "age": "2M", "series": 4, "description": "Minimum age: 6 weeks"},
#             {"dose": 2, "age": "4M", "series": 4, "description": "No further doses needed for healthy children if first dose was administered at age 24 months or older 4 weeks if first dose was administered before the 1st birthday 8 weeks (as final dose for healthy children) if first dose was administered at the 1st birthday or after"},
#             {"dose": 3, "age": "6M", "series": 4, "description": "at least 4 weeks after 2nd dose"},
#             {"dose": 4, "age": "12M-15M", "series": 4, "description": "at least 8 weeks after 3rd dose"}
#         ]
#     },
#     {
#         "vaccine": "IPV",
#         "cvx": "10",  # Inactivated Poliovirus Vaccine
#         "disease": "Inactivated Poliovirus",
#         "total_series": 4,
#         "vaccine_info": "Polio is a disabling and life-threatening disease caused by poliovirus, which can infect the spinal cord and cause paralysis. It most often sickens children younger than 5 years old. Polio was eliminated in the United States with vaccination, and continued use of polio vaccine has kept this country polio-free.",
#         "doses": [
#             {"dose": 1, "age": "2M", "series": 4, "description": "Minimum age: 6 weeks"},
#             {"dose": 2, "age": "4M", "series": 4, "description": "at least 4 weeks after 1st dose"},
#             {"dose": 3, "age": "6M-18M", "series": 4, "description": "at least 4 weeks after 2nd dose if current age is <4 years. 6 months (as final dose) if current age is 4 years or older"},
#             {"dose": 4, "age": "4Y-6Y", "series": 4, "description": "at least 6 months after 3rd dose (minimum age 4 years for final dose)"}
#         ]
#     },
#     {
#         "vaccine": "Influenza",
#         "cvx": "161",  # Influenza, unspecified (annual, varies by formulation)
#         "disease": "Influenza",
#         # "disease_code": "6142004",
#         "total_series": 1,
#         "vaccine_info": "Flu illness is more dangerous than the common cold for children. Each year, millions of children get sick with seasonal flu; thousands of children are hospitalized, and some children die from flu. Children commonly need medical care because of flu, especially children younger than 5 years old.",
#         "doses": [
#             {"dose": 1, "age": "6M", "series": 1, "description": "Minimum age: 6 months then 1 dose annually"},
#         ]
#     },
#     {
#         "vaccine": "MMR",
#         "cvx": "03",  # Measles, Mumps, Rubella
#         "disease": "Measles, Mumps, Rubella",
#         # "disease_code": "14189004",  # Measles (representative code)
#         "total_series": 2,
#         "vaccine_info": "The MMR vaccine helps prevent three diseases: measles, mumps, and rubella (German measles). These diseases are contagious and can be serious.",
#         "doses": [
#             {"dose": 1, "age": "12M-15M", "series": 2, "description": "Minimum age: 12 months"},
#             {"dose": 2, "age": "4Y-6Y", "series": 2, "description": "at least 4 weeks after 1st dose"}
#         ]
#     },
#     {
#         "vaccine": "Varicella",
#         "cvx": "21",  # Varicella (chickenpox)
#         "disease": "Varicella",
#         # "disease_code": "38907003",
#         "total_series": 2,
#         "vaccine_info": "Varicella (Chickenpox) is a very contagious disease known for its itchy, blister-like rash and a fever. Chickenpox is a mild disease for many, but can be serious, even life-threatening, especially in babies, teenagers, pregnant women, and people with weakened immune systems.",
#         "doses": [
#             {"dose": 1, "age": "12M-15M", "series": 2, "description": "Minimum age: 12 months"},
#             {"dose": 2, "age": "4Y-6Y", "series": 2, "description": "at least 3 months after 1st dose"}
#         ]
#     },
#     {
#         "vaccine": "HepA",
#         "cvx": "83",  # Hepatitis A, pediatric
#         "disease": "Hepatitis A",
#         # "disease_code": "40468003",
#         "total_series": 2,
#         "vaccine_info": "Hepatitis A can be a serious, even fatal liver disease caused by the hepatitis A virus. Children with the virus often don't have symptoms, but they often pass the disease to others, including their unvaccinated parents or caregivers.",
#         "doses": [
#             {"dose": 1, "age": "12M-23M", "series": 2, "description": "Minimum age: 12 months"},
#             {"dose": 2, "age": "18M-29M", "series": 2, "description": "at least 6 months after 1st dose"}
#         ]
#     },
#     {
#         "vaccine": "Tdap",
#         "cvx": "115",  # Tetanus, Diphtheria, Pertussis (adolescent/adult formulation)
#         "disease": "Diphtheria, tetanus, acellular pertussis ",
#         # "disease_code": "27836007",  # Pertussis (representative)
#         "total_series": 1,
#         "vaccine_info": "A Tdap booster shot protects older children from three serious diseases—diphtheria, tetanus, and whooping cough (pertussis). While people of any age in the United States can get all three of these potentially deadly diseases, whooping cough is most common. Preteens and teens who get whooping cough may cough for 10 weeks or more, possibly leading to rib fractures from severe coughing.",
#         "doses": [
#             {"dose": 1, "age": "11Y-12Y", "series": 1, "description": "Minimum age: 11 years"}  # Single booster; DTaP series precedes
#         ]
#     },
#     {
#         "vaccine": "HPV",
#         "cvx": "165",  # HPV 9-valent (Gardasil 9)
#         "disease": "Human Papillomavirus",
#         # "disease_code": "240532009",
#         "total_series": 2,
#         "vaccine_info": "Human papillomavirus (HPV) is a common virus that can cause several cancers in men and women. HPV vaccination is recommended at ages 11-12 years to help protect against cancers caused by HPV infection. For best protection, most children this age will need two shots of the HPV vaccine, 6-12 months apart.",
#         "doses": [
#             {"dose": 1, "age": "11Y-12Y", "series": 2, "description": "Minimum age: 9 years"},
#             {"dose": 2, "age": "12Y-13Y", "series": 2, "description": "at least 6 months after 1st dose"}
#         ]
#     },
#     {
#         "vaccine": "MenACWY",
#         "cvx": "203",  # Meningococcal ACWY (e.g., Menveo, MenQuadfi)
#         "disease": "Meningococcal disease (serogroups A, C, W, Y)",
#         # "disease_code": "23511006",
#         "total_series": 2,
#         "vaccine_info": "Meningococcal disease can refer to any illness caused by a type of bacteria called Neisseria meningitidis. These bacteria can cause meningococcal meningitis or bloodstream infections, which can be serious, even deadly. The meningococcal vaccine called MenACWY helps protect against four types of the bacteria that causes meningococcal disease (serogroups A, C, W, and Y).",
#         "doses": [
#             {"dose": 1, "age": "11Y-12Y", "series": 2, "description": "Minimum age: 11 years"},
#             {"dose": 2, "age": "16Y", "series": 2, "description": "at least 8 weeks after 1st dose"}
#         ]
#     },
#     {
#         "vaccine": "MenB",
#         "cvx": "162",  # Meningococcal B (e.g., Bexsero, Trumenba)
#         "disease": "Meningococcal disease (serogroup B)",
#         # "disease_code": "23511006",
#         "total_series": 2,
#         "vaccine_info": "Meningococcal disease can refer to any illness caused by a type of bacteria called Neisseria meningitidis. These bacteria can cause meningococcal meningitis and bloodstream infections, which can be serious, even deadly. Meningococcal B vaccine, or MenB vaccine, helps protect against one type of the bacteria that causes meningococcal disease (serogroup B). Note: CDC does not routinely recommend MenB vaccine for all adolescents. Instead, healthcare providers and parents can discuss the risk of the disease and weigh the risks and benefits of vaccination.",
#         "doses": [
#             {"dose": 1, "age": "16Y-18Y", "series": 2, "description": "Consult clinician for shared clinical decision-making"},
#             {"dose": 2, "age": "18Y-19Y", "series": 2, "description": "Consult clinician for shared clinical decision-making"}
#         ]
#     }
# ]
#
#
# def search_patients_by_practitioner(practitioner_id):
#     """
#     Search for patients assigned to a specific practitioner.
#
#     :param practitioner_id: The ID of the practitioner.
#     :return: A list of patients assigned to the practitioner.
#     """
#     patients = client.resources('Patient').search(general_practitioner=practitioner_id).fetch()
#     return patients if patients else []
#
#
# @st.cache_resource(ttl=600)
# def search_practitioner(id=None):
#     """
#     Search for practitioners by name or identifier.
#
#     :param _id: The id of the practitioner.
#     """
#     search_params = {}
#     if id:
#         search_params['_id'] = id
#
#     practitioners = client.resources('Practitioner').search(**search_params).limit(10).fetch()
#     if practitioners:
#         practitioner_ids = [practitioner['id'] for practitioner in practitioners]
#         return practitioner_ids
#     return []
#
#
# @st.cache_resource(ttl=600)
# def search_patient_under_n_year_old(count=10, n=18):
#     """
#     Fetch all patients under 5 years old using FHIR search
#     """
#     five_years_ago = (datetime.now() - timedelta(days=n * 365)).strftime('%Y-%m-%d')
#     patients = client.resources('Patient').search(birthdate=f'gt{five_years_ago}').limit(count).fetch()
#
#     return patients
#
#
# def calculate_date_criterion(patient_dob, age):
#     """Calculate the date criterion based on patient date of birth and age."""
#     dob = datetime.strptime(patient_dob, "%Y-%m-%d")
#     if "-" in age:
#         start_age, end_age = age.split("-")
#         start_date = add_age_to_date(dob, start_age)
#         end_date = add_age_to_date(dob, end_age)
#         return start_date, end_date
#     else:
#         return add_age_to_date(dob, age), None
#
#
# def add_age_to_date(dob, age):
#     """Add age to date of birth."""
#     if "M" in age:
#         months = int(age.replace("M", ""))
#         return dob + dateutil.relativedelta.relativedelta(months=months)
#     elif "Y" in age:
#         years = int(age.replace("Y", ""))
#         return dob + dateutil.relativedelta.relativedelta(years=years)
#     else:
#         return dob
#
#
# def assign_immunization_recommendation_to_patient(patient_id, patient_dob, do_upload=False):
#     """Upload the CDC schedule to the FHIR server with a group identifier."""
#     results = []
#
#     for vaccine in cdc_schedule:
#         recommendation = client.resource(
#             "ImmunizationRecommendation",
#             identifier=[
#                 CDC_GROUP_IDENTIFIER,
#             ],
#             patient={"reference": f"Patient/{patient_id}"},
#             date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
#             recommendation=[
#                 {
#                     "vaccineCode": [{"coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": vaccine["cvx"], "display": f"{vaccine['vaccine']} vaccine"}]}],
#                     "targetDisease": [{"coding": [{"system": "http://snomed.info/sct", "display": vaccine["disease"]}]}],
#                     "dateCriterion": [
#                         {
#                             "value": calculate_date_criterion(patient_dob, dose["age"])[0].strftime("%Y-%m-%d")
#                         }
#                     ],
#                     "description": dose["description"],
#                     "doseNumberPositiveInt": dose["dose"],
#                     "seriesDosesPositiveInt": dose["series"],
#                 } for dose in vaccine["doses"]
#             ]
#         )
#         results.append(recommendation)
#         if do_upload:
#             try:
#                 recommendation.save()
#             except Exception as e:
#                 raise f"Failed to upload {vaccine['vaccine']}: {str(e)}"
#     return results
#
#
# def fetch_cdc_schedule_from_fhir():
#     """Retrieve only CDC schedule ImmunizationRecommendations using the group identifier."""
#     try:
#         # Search by the CDC group identifier
#         resources = client.resources("ImmunizationRecommendation").search(
#             identifier=f"{'|'.join([identifier for identifier in CDC_GROUP_IDENTIFIER.values()])}"
#         ).fetch()
#         schedules = [res.serialize() for res in resources]
#         if not schedules:
#             return [{"message": "No CDC schedule resources found on the server."}]
#         return schedules
#     except Exception as e:
#         st.error(f"Error fetching CDC schedule: {str(e)}")
#         return [{"error": str(e)}]
#
#
# # Streamlit app
# st.title("CDC Immunization Schedule Reminder")
# practice_id = st.text_input("Enter Practitioner ID")
# # if st.button("Search Practitioner"):
# practitioner_ids = search_practitioner(practice_id)
# selected_practitioner_id = st.selectbox("Select Practitioner ID", practitioner_ids)
# patients = search_patient_under_n_year_old(n=5)
# # st.write(patients[0])
# results = assign_immunization_recommendation_to_patient(patients[1]['id'], patients[1]['birthDate'], do_upload=True)
# st.write(results)
# identifier = results[0]["identifier"][0]["value"]
# patient = results[0]["patient"]["reference"]
# created_date = results[0]["date"]
# results_as_dict = [
#     {
#         "vaccine": rec["vaccineCode"][0]["coding"][0]["display"],
#         "disease": rec["targetDisease"]["coding"][0]["display"],
#         "description": rec["description"],
#         "recommended_date": rec["dateCriterion"][0]["value"],
#         "dose": rec["doseNumberPositiveInt"],
#         "series": rec["seriesDosesPositiveInt"],
#     }
#     for result in results for rec in result["recommendation"]
# ]
# st.write(results_as_dict)
# df = pd.DataFrame(results_as_dict).sort_values("recommended_date")
# st.dataframe(df, hide_index=True)
# st.stop()
# # Upload button
# if st.button("Upload CDC Schedule to FHIR"):
#     with st.spinner("Uploading to FHIR server..."):
#         results = assign_immunization_recommendation_to_patient(patients[0]['id'], patients[0]['birthDate'])
#         for result in results:
#             st.write(result)
#
# # Display current CDC schedule
# st.subheader("Current CDC Schedule on FHIR Server")
# if st.button("Refresh CDC Schedule"):
#     with st.spinner("Fetching CDC schedule from FHIR server..."):
#         schedule = fetch_cdc_schedule_from_fhir()
#         if schedule:
#             st.json(schedule)
#         else:
#             st.write("No CDC schedules retrieved.")
#
# # Option to view CDC data locally
# st.subheader("Local CDC Schedule Data")
# if st.checkbox("Show local CDC schedule"):
#     st.json(cdc_schedule)
