import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Access secrets
    s = st.secrets["connections"]["gsheets"]
    
    # Clean the key: Replace literal '\n' and ensure it's a string
    raw_key = str(s["private_key"]).replace("\\n", "\n")
    
    # DEBUG: See how much data the app is actually getting
    st.write(f"DEBUG: Key length detected: {len(raw_key)} characters.")

    creds_dict = {
        "type": "service_account",
        "project_id": s["project_id"],
        "private_key": raw_key,
        "client_email": s["client_email"],
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    url = st.secrets["connections"]["gsheets"]["spreadsheet_url"]
    sheet = client.open_by_url(url)
    
    # Test read
    df_goals = pd.DataFrame(sheet.worksheet("Goals").get_all_records())
    st.success("✅ Connection Successful!")
    st.dataframe(df_goals)

except Exception as e:
    st.error(f"Connection Error: {e}")
    st.info("Check: 1. Did you use triple quotes in Secrets? 2. Did you copy the WHOLE key?")
