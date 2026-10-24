import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Nutrimi 🥗")

# Connessione al Service Account
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dei dati passando esplicitamente l'URL del foglio
data = conn.read(
    spreadsheet="https://docs.google.com/spreadsheets/d/1KbZzYVapAOS837QuWUnJ6oERICuvzD5WZSObe9Owgs/edit",
    ttl=0
)

st.write("I tuoi dati sincronizzati in tempo reale:")
st.dataframe(data)
