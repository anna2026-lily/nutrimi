import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dei dati dal foglio "Nutrimi" (ttl=0 per aggiornamento in tempo reale)
data = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/1KbZzYVapAOS837QuWUnJ6oERICuvzD5WZSObe9Owgs/edit", ttl=0)

st.title("Nutrimi 🥗")
st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
