import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

try:
    # 1. Connect
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Load the Data (Matching your tab order)
    # We read Transactions first since it is your first tab
    df_tx = conn.read(worksheet="Transactions", ttl=0)
    df_goals = conn.read(worksheet="Goals", ttl=0)
    
    st.success("✅ Dashboard Sync Complete!")

    # --- DASHBOARD VIEW ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Recent Transactions")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("🎯 Budget Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)

    # --- ADD DATA SECTION ---
    st.divider()
    st.subheader("Add New Entry")
    
    tab1, tab2 = st.tabs(["Add Transaction", "Add Goal"])
    
    with tab1:
        with st.form("new_tx"):
            date = st.date_input("Date")
            desc = st.text_input("Description")
            amt = st.number_input("Amount", step=1)
            if st.form_submit_button("Save Transaction"):
                new_row = pd.DataFrame([{"Date": str(date), "Description": desc, "Amount": amt}])
                updated = pd.concat([df_tx, new_row], ignore_index=True)
                conn.update(worksheet="Transactions", data=updated)
                st.success("Transaction Saved!")
                st.rerun()

    with tab2:
        with st.form("new_goal"):
            cat = st.text_input("Category")
            goal_amt = st.number_input("Goal Amount", step=1)
            if st.form_submit_button("Save Goal"):
                new_row = pd.DataFrame([{"Category": cat, "Goal": goal_amt}])
                updated = pd.concat([df_goals, new_row], ignore_index=True)
                conn.update(worksheet="Goals", data=updated)
                st.success("Goal Saved!")
                st.rerun()

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write("Check if the tab names at the bottom of your Google Sheet are spelled exactly: **Transactions** and **Goals**")
    st.error(f"Details: {e}")
