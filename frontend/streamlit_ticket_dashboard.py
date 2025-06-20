import streamlit as st
import requests
import pandas as pd

st.title("🎫 IT Ticket Dashboard")

API_URL = "http://127.0.0.1:8000/ticket/all"

try:
    response = requests.get(API_URL)
    response.raise_for_status()
    tickets = response.json()

    if not tickets:
        st.info("No tickets found.")
    else:
        df = pd.DataFrame(tickets)

        df.columns = [col.replace("_", " ").title() for col in df.columns]

        st.dataframe(df, use_container_width=True)

except requests.RequestException as e:
    st.error(f"Failed to fetch tickets: {e}")