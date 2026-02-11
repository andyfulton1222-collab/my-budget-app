import streamlit as st
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

try:
    # 1. Grab the raw link from secrets
    raw_url = st.secrets["spreadsheet"]
    
    # 2. Extract just the ID part (the "ID" is the magic key Google needs)
    # This logic finds the part between /d/ and /edit
    spreadsheet_id = raw_url.split('/d/')[1].split('/')[0]
    
    # 3. Build perfect download links for your specific tabs
    url_tx = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Transactions"
    url_goals = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Goals"

    # 4. Load the data
    df_tx = pd.read_csv(url_tx)
    df_goals = pd.read_csv(url_goals)

    st.success("✅ CONNECTION SUCCESSFUL!")

    # --- DISPLAY ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Transactions (Tab 1)")
        st.dataframe(df_tx, use_container_width=True)
    with col2:
        st.subheader("🎯 Budget Goals (Tab 2)")
        st.dataframe(df_goals, use_container_width=True)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write("Double-check your Google Sheet tab names are exactly: **Transactions** and **Goals**")
    st.info("Make sure the sheet is shared: 'Anyone with the link' can 'Editor'")
    st.error(f"Technical Detail: {e}")
