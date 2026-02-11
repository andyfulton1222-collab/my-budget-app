import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")

@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Directly pulling the formatted dictionary from secrets
    sa_info = st.secrets["connections"]["gsheets"]["service_account"]
    creds = Credentials.from_service_account_info(sa_info, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    sh = client.open_by_key("1L-jzVCQoQW7OOfgZCgL6ySBnGz_fd1cIZsk5oeL06kc")
    
    ws_tx = sh.worksheet("Transactions")
    ws_goals = sh.worksheet("Goals")
    
    # Load and display
    df_tx = pd.DataFrame(ws_tx.get_all_records())
    st.title("📊 Executive Dashboard")
    st.success("✅ System Authenticated")
    st.dataframe(df_tx, use_container_width=True)

except Exception as e:
    st.error(f"Setup Error: {e}")
