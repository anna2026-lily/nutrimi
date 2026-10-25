
import streamlit as st
import gspread
import pandas as pd
import json

st.title("Nutrimi 🥗")
# Connessione diretta che legge il file JSON delle credenziali presente nel repository GitHub
gc = gspread.service_account_from_dict(json.loads(st.secrets["gcp_json"]))


sh = gc.open("Nutrimi")
worksheet = sh.worksheet("Foglio1")

# Lettura dei dati in un DataFrame Pandas
data = pd.DataFrame(worksheet.get_all_records())

st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
