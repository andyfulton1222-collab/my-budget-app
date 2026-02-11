import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget (Auto-Save Active)")

# 1. Setup Direct Connection
@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Pulling from your specific secrets structure
    sa_info = st.secrets["connections"]["gsheets"]["service_account"]
    creds = Credentials.from_service_account_info(sa_info, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # Using your specific Sheet ID
    sheet_id = "1L-jzVCQoQW7OOfgZCgL6ySBnGz_fd1cIZsk5oeL06kc"
    sh = client.open_by_key(sheet_id)
    
    # 2. Load Data
    ws_tx = sh.worksheet("Transactions")
    ws_goals = sh.worksheet("Goals")
    
    df_tx = pd.DataFrame(ws_tx.get_all_records())
    df_goals = pd.DataFrame(ws_goals.get_all_records())

    # --- UI LAYOUT ---
    tab1, tab2 = st.tabs(["Daily Transactions", "Budget Planning"])

    with tab1:
        st.subheader("📝 Recent Spending")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)
        
        with st.form("new_tx", clear_on_submit=True):
            st.write("**Log New Transaction**")
            col_d, col_desc, col_a = st.columns(3)
            with col_d: d = st.date_input("Date")
            with col_desc: desc = st.text_input("Description")
            with col_a: amt = st.number_input("Amount", min_value=0.0)
            
            if st.form_submit_button("Save to Google Sheets"):
                ws_tx.append_row([str(d), desc, amt])
                st.success("✅ Transaction Saved!")
                st.rerun()

    with tab2:
        st.subheader("🎯 Monthly Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)
        
        with st.form("new_goal", clear_on_submit=True):
            st.write("**Set New Category Goal**")
            cat = st.text_input("Category")
            g_amt = st.number_input("Monthly Limit", min_value=0.0)
            
            if st.form_submit_button("Update Goals"):
                ws_goals.append_row([cat, g_amt])
                st.success("✅ Goal Updated!")
                st.rerun()

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write("If you see a 'Worksheet not found' error, check your tab names.")
    st.error(f"Details: {e}")
