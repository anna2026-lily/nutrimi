import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Nutrimi 🥗")

# Connessione automatica che legge URL e credenziali direttamente dai Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dei dati senza specificare l'URL nel codice
data = conn.read(ttl=0)

st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
