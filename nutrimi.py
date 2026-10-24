import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Nutrimi 🥗")

# Crea la connessione leggendo automaticamente i dati dai Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Legge il foglio configurato nei Secrets (senza ripetere l'URL)
data = conn.read(ttl=0)

st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
