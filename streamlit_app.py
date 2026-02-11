import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. ROBUST AUTHENTICATION
@st.cache_resource
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Access the secrets directly
    s = st.secrets["connections"]["gsheets"]
    
    # CRITICAL: Clean the private key of any hidden characters or literal backslashes
    raw_key = s["private_key"]
    
    # Replace literal '\n' strings with actual newline characters
    processed_key = raw_key.replace("\\n", "\n")
    
    # Ensure the key starts and ends correctly
    if not processed_key.startswith("-----BEGIN PRIVATE KEY-----"):
        processed_key = "-----BEGIN PRIVATE KEY-----\n" + processed_key
    if not processed_key.endswith("-----END PRIVATE KEY-----"):
        processed_key = processed_key + "\n-----END PRIVATE KEY-----"

    creds_dict = {
        "type": "service_account",
        "project_id": s["project_id"],
        "private_key_id": s["private_key_id"],
        "private_key": processed_key,
        "client_email": s["client_email"],
        "client_id": s["client_id"],
        "auth_uri": s["auth_uri"],
        "token_uri": s["token_uri"],
        "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
        "client_x509_cert_url": s["client_x509_cert_url"],
    }
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

# 3. CONNECTION & DATA LOADING
try:
    client = get_gspread_client()
    url = st.secrets["connections"]["gsheets"]["spreadsheet_url"]
    sheet = client.open_by_url(url)
    
    # Access worksheets
    tx_worksheet = sheet.worksheet("Transactions")
    goals_worksheet = sheet.worksheet("Goals")
    
    df_tx = pd.DataFrame(tx_worksheet.get_all_records())
    df_goals = pd.DataFrame(goals_worksheet.get_all_records())
    
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.stop()

# 4. SIDEBAR - DATA ENTRY
with st.sidebar:
    st.header("Add New Entry")
    with st.form("add_goal"):
        st.subheader("Set Monthly Goal")
        new_cat = st.text_input("Category Name")
        goal_val = st.number_input("Goal Amount", min_value=0.0)
        
        if st.form_submit_button("Save Goal"):
            try:
                goals_worksheet.append_row([new_cat, goal_val])
                st.success(f"Goal for {new_cat} saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Save failed: {e}")

# 5. DASHBOARD DISPLAY
st.subheader("Current Budget Goals")
st.dataframe(df_goals, use_container_width=True)

st.subheader("Recent Transactions")
st.dataframe(df_tx, use_container_width=True)
