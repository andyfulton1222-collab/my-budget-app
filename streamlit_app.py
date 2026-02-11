import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 1. Try to connect using the "spreadsheet" secret
try:
    # We tell Streamlit exactly where to look
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Load the data
    # Note: Ensure your Google Sheet tabs are named "Goals" and "Transactions"
    df_goals = conn.read(worksheet="Goals")
    df_tx = conn.read(worksheet="Transactions")
    
    st.success("✅ Dashboard Connected!")

    # --- THE VIEW ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Recent Transactions")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

    # --- ADD DATA ---
    st.divider()
    with st.expander("➕ Add New Budget Goal"):
        with st.form("new_goal"):
            cat = st.text_input("Category")
            amt = st.number_input("Goal Amount", min_value=0)
            if st.form_submit_button("Save to Google Sheets"):
                if cat:
                    new_data = pd.DataFrame([{"Category": cat, "Goal": amt}])
                    updated_df = pd.concat([df_goals, new_data], ignore_index=True)
                    conn.update(worksheet="Goals", data=updated_df)
                    st.success("Saved!")
                    st.rerun()

except Exception as e:
    st.error("⚠️ Connection Secret Missing")
    st.write("Go to Secrets and ensure the line starts with **spreadsheet =**")
    st.info(f"Technical details: {e}")
