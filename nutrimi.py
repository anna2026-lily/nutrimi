import streamlit as st
import gspread
import pandas as pd
import json

st.title("Nutrimi 🥗")

# Carica le credenziali in modo sicuro dai Secrets
creds_dict = json.loads(st.secrets["gcp_json"])

# Connessione a Google Sheets tramite gspread
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1KbZzYVapAOS837QuWUnJ6oERICuvzD5WZSObe9Owgs/edit")
worksheet = sh.worksheet("Foglio1")

# Lettura dei dati in un DataFrame Pandas
data = pd.DataFrame(worksheet.get_all_records())

st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
