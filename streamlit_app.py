import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 1. Establish the Connection
# This looks for [connections.gsheets] in your secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. Load the Data
    # Change "Goals" or "Transactions" to match your actual tab names
    df_goals = conn.read(worksheet="Goals")
    df_tx = conn.read(worksheet="Transactions")
    
    st.success("✅ Connection Active")

    # --- DASHBOARD VIEW ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Budget Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Recent Transactions")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

    # --- ADD DATA SECTION ---
    st.divider()
    st.subheader("Add a New Budget Goal")
    
    with st.form("new_goal_form"):
        new_category = st.text_input("Category")
        new_amount = st.number_input("Amount", min_value=0)
        submit = st.form_submit_button("Save to Google Sheets")
        
        if submit:
            if new_category:
                new_row = pd.DataFrame([{"Category": new_category, "Goal": new_amount}])
                updated_df = pd.concat([df_goals, new_row], ignore_index=True)
                conn.update(worksheet="Goals", data=updated_df)
                st.success(f"Added {new_category}!")
                st.rerun()

except Exception as e:
    st.error("⚠️ Connection Issue")
    st.write("The app can't find your spreadsheet link in the Secrets box.")
    st.info("Check that your Secrets box has: **spreadsheet = 'YOUR_URL'**")
    st.error(f"Error details: {e}")
