import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    s = st.secrets["connections"]["gsheets"]
    
    # This replaces the literal characters '\n' with actual line breaks
    raw_key = s["private_key"].replace("\\n", "\n")
    
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
    sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet_url"])
    
    # Just show the data to confirm it's alive!
    df_goals = pd.DataFrame(sheet.worksheet("Goals").get_all_records())
    st.success("✅ THE CONNECTION IS LIVE!")
    st.dataframe(df_goals)

except Exception as e:
    st.error(f"Connection Error: {e}")
