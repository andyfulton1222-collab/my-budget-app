import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. AUTHENTICATION (The Direct Way)
@st.cache_resource
def get_gspread_client():
    # Define the scope
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Pull secrets
    s = st.secrets["connections"]["gsheets"]
    
    # Create credentials dictionary
    # We use .replace("\\n", "\n") to fix the private key formatting on the fly
    creds_dict = {
        "type": s["type"],
        "project_id": s["project_id"],
        "private_key_id": s["private_key_id"],
        "private_key": s["private_key"].replace("\\n", "\n"),
        "client_email": s["client_email"],
        "client_id": s["client_id"],
        "auth_uri": s["auth_uri"],
        "token_uri": s["token_uri"],
        "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
        "client_x509_cert_url": s["client_x509_cert_url"],
    }
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # Open the sheet by its URL from secrets
    sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet_url"])
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.stop()

# 3. HELPER FUNCTIONS FOR DATA
def get_data(worksheet_name):
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

# Load Initial Data
try:
    df_tx, tx_worksheet = get_data("Transactions")
    df_goals, goals_worksheet = get_data("Goals")
except Exception as e:
    st.warning("Make sure your sheet has tabs named 'Transactions' and 'Goals'.")
    st.stop()

# 4. SIDEBAR - SET GOAL
with st.sidebar:
    st.header("Add New Entry")
    with st.form("add_goal"):
        st.subheader("Set Monthly Goal")
        new_cat = st.text_input("Category Name")
        goal_val = st.number_input("Goal Amount", min_value=0.0)
        
        if st.form_submit_button("Save Goal"):
            # Append directly to the sheet
            goals_worksheet.append_row([new_cat, goal_val])
            st.success(f"Goal for {new_cat} saved!")
            st.rerun()

# 5. DASHBOARD
st.subheader("Current Budget Goals")
st.dataframe(df_goals, use_container_width=True)

st.subheader("Recent Transactions")
st.dataframe(df_tx, use_container_width=True)
