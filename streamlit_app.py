import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # Check for the existence of the connection header
    if "connections" not in st.secrets or "gsheets" not in st.secrets["connections"]:
        st.error("Missing [connections.gsheets] section in Secrets.")
        st.stop()
        
    s = st.secrets["connections"]["gsheets"]
    
    # Check for specific keys and alert if missing
    required_keys = ["project_id", "private_key", "client_email", "spreadsheet_url"]
    for key in required_keys:
        if key not in s:
            st.error(f"Secret key '{key}' is missing from [connections.gsheets]")
            st.write("Available keys in your secrets:", list(s.keys()))
            st.stop()

    processed_key = s["private_key"].replace("\\n", "\n")
    
    creds_dict = {
        "type": "service_account",
        "project_id": s["project_id"],
        "private_key_id": s.get("private_key_id"),
        "private_key": processed_key,
        "client_email": s["client_email"],
        "client_id": s.get("client_id"),
        "auth_uri": s.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": s.get("token_uri", "https://oauth2.googleapis.com/token"),
        "auth_provider_x509_cert_url": s.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": s.get("client_x509_cert_url"),
    }
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet_url"])
    
    tx_ws = sheet.worksheet("Transactions")
    goals_ws = sheet.worksheet("Goals")
    
    df_tx = pd.DataFrame(tx_ws.get_all_records())
    df_goals = pd.DataFrame(goals_ws.get_all_records())
    
    st.success("Connected to Sheets!")
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# Basic display to verify it works
st.subheader("Budget Goals")
st.dataframe(df_goals)

with st.sidebar:
    with st.form("add_goal"):
        cat = st.text_input("Category")
        val = st.number_input("Goal", min_value=0.0)
        if st.form_submit_button("Save"):
            goals_ws.append_row([cat, val])
            st.rerun()
