import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. THE "KEY SURGERY" AUTHENTICATION
@st.cache_resource
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    s = st.secrets["connections"]["gsheets"]
    
    # --- KEY SURGERY START ---
    raw_key = s["private_key"]
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    # 1. Strip headers, footers, and ALL whitespace/newlines
    clean_key = raw_key.replace(header, "").replace(footer, "").strip()
    clean_key = "".join(clean_key.split()) # Removes all spaces, \n, and \r
    
    # 2. Reconstruct with a physical newline every 64 characters (Standard PEM)
    formatted_key = header + "\n"
    for i in range(0, len(clean_key), 64):
        formatted_key += clean_key[i:i+64] + "\n"
    formatted_key += footer
    # --- KEY SURGERY END ---
    
    creds_dict = {
        "type": s["type"],
        "project_id": s["project_id"],
        "private_key_id": s["private_key_id"],
        "private_key": formatted_key,
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
    sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet_url"])
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.stop()

# 3. DATA LOADING
def get_data(worksheet_name):
    worksheet = sheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data), worksheet

try:
    df_tx, tx_worksheet = get_data("Transactions")
    df_goals, goals_worksheet = get_data("Goals")
except Exception as e:
    st.warning("Ensure your Google Sheet has tabs named 'Transactions' and 'Goals'.")
    st.stop()

# 4. SIDEBAR - ADD GOAL
with st.sidebar:
    st.header("Add New Entry")
    with st.form("add_goal"):
        st.subheader("Set Monthly Goal")
        new_cat = st.text_input("Category Name")
        goal_val = st.number_input("Goal Amount", min_value=0.0)
        
        if st.form_submit_button("Save Goal"):
            goals_worksheet.append_row([new_cat, goal_val])
            st.success(f"Goal for {new_cat} saved!")
            st.rerun()

# 5. DASHBOARD
st.subheader("Current Budget Goals")
st.dataframe(df_goals, use_container_width=True)

st.subheader("Recent Transactions")
st.dataframe(df_tx, use_container_width=True)
