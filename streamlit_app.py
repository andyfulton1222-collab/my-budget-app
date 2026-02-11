import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget (Auto-Save Active)")

# 1. Establish the Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Read Existing Data
try:
    df_tx = conn.read(worksheet="Transactions", ttl=0)
    df_goals = conn.read(worksheet="Goals", ttl=0)

    # --- DASHBOARD LAYOUT ---
    tab1, tab2 = st.tabs(["Daily Transactions", "Budget Planning"])

    with tab1:
        st.subheader("📝 Recent Spending")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)
        
        with st.form("new_tx"):
            st.write("**Log New Transaction**")
            d = st.date_input("Date")
            desc = st.text_input("Description")
            amt = st.number_input("Amount", min_value=0.0)
            if st.form_submit_button("Save to Google Sheets"):
                new_row = pd.DataFrame([{"Date": str(d), "Description": desc, "Amount": amt}])
                updated = pd.concat([df_tx, new_row], ignore_index=True)
                conn.update(worksheet="Transactions", data=updated)
                st.success("Transaction Logged!")
                st.rerun()

    with tab2:
        st.subheader("🎯 Monthly Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)
        
        with st.form("new_goal"):
            st.write("**Set New Category Goal**")
            cat = st.text_input("Category")
            g_amt = st.number_input("Monthly Limit", min_value=0.0)
            if st.form_submit_button("Update Goals"):
                new_row = pd.DataFrame([{"Category": cat, "Goal": g_amt}])
                updated = pd.concat([df_goals, new_row], ignore_index=True)
                conn.update(worksheet="Goals", data=updated)
                st.success("Goal Updated!")
                st.rerun()

except Exception as e:
    st.error(f"Connection Error: {e}")
