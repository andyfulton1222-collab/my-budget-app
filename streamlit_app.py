import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

try:
    # Connect
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Read - We use a slightly different method to catch 404 errors
    df_goals = conn.read(worksheet="Goals", ttl=0) # ttl=0 ensures it doesn't use old, broken data
    df_tx = conn.read(worksheet="Transactions", ttl=0)
    
    st.success("✅ Connected to Google Sheets!")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Budget Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Recent Transactions")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("⚠️ Almost there! We have a '404' or Permission issue.")
    st.write("1. Open your Sheet and click **Share**.")
    st.write("2. Make sure it says **'Anyone with the link'** and **'Editor'**.")
    st.write("3. Ensure your Secrets link ends right after the long ID string.")
    st.divider()
    st.error(f"Technical Detail: {e}")
