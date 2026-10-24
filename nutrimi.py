import streamlit as st
import gspread
import pandas as pd
import json
import tempfile

st.title("Nutrimi 🥗")

# Creazione di un file JSON temporaneo con le credenziali per aggirare i problemi di formattazione della chiave RSA
creds_data = {
    "type": "service_account",
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"].replace("\\n", "\n"),
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "token_uri": st.secrets["token_uri"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/nutrimi-bot%40nutrimi-512520.iam.gserviceaccount.com"
}

# Scrive i dati in un file JSON temporaneo sicuro sul server
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
    json.dump(creds_data, f)
    temp_creds_path = f.name

# Connessione a Google Sheets leggendo il file temporaneo
gc = gspread.service_account(filename=temp_creds_path)
sh = gc.open_by_url(st.secrets["spreadsheet"])
worksheet = sh.worksheet(st.secrets["worksheet"])

# Lettura dei dati in un DataFrame Pandas
data = pd.DataFrame(worksheet.get_all_records())

st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
