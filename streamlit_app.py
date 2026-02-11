import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import re

st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    # 1. Access the secrets
    s = st.secrets["connections"]["gsheets"]
    
    # 2. THE KEY SCRUBBER
    # This removes literal '\n', spaces, and weird hidden characters (like Byte 4 or underscores)
    raw_key = s["private_key"]
    header = "-----BEGIN PRIVATE KEY-----"
    footer = "-----END PRIVATE KEY-----"
    
    # Remove header/footer to clean the middle
    content = raw_key.replace(header, "").replace(footer, "")
    # Remove everything that isn't a letter, number, plus, or slash (standard Base64)
    content = re.sub(r'[^A-Za-z0-9+/=]', '', content)
    
    # Rebuild the key with proper line breaks every 64 characters
    clean_key = header + "\n"
    for i in range(0, len(content), 64):
        clean_key += content[i:i+64] + "\n"
    clean_key += footer

    creds_dict = {
        "type": "service_account",
        "project_id": s["project_id"],
        "private_key_id": s.get("private_key_id"),
        "private_key": clean_key,
        "client_email": s["client_email"],
        "client_id": s.get("client_id"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

# CONNECTION & APP LOGIC
try:
    client = get_gspread_client()
    sheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet_url"])
    
    # Load data from the specific tabs
    df_tx = pd.DataFrame(sheet.worksheet("Transactions").get_all_records())
    df_goals = pd.DataFrame(sheet.worksheet("Goals").get_all_records())
    
    st.success("✅ Securely Connected to Google Sheets!")
    
    st.subheader("Current Budget Goals")
    st.dataframe(df_goals, use_container_width=True)
    
    st.subheader("Recent Transactions")
    st.dataframe(df_tx, use_container_width=True)

except Exception as e:
    st.error(f"Final Connection Error: {e}")
    st.info("Ensure the Private Key in your Secrets starts with -----BEGIN PRIVATE KEY-----")
