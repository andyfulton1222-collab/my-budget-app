import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 1. Establish the Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Load the Data
try:
    # Read the 'Goals' and 'Transactions' tabs
    df_goals = conn.read(worksheet="Goals")
    df_tx = conn.read(worksheet="Transactions")
    
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
        new_category = st.text_input("Category (e.g., Rent, Groceries)")
        new_amount = st.number_input("Monthly Goal Amount", min_value=0)
        submit = st.form_submit_button("Save to Google Sheets")
        
        if submit:
            if new_category:
                # Create a new row of data
                new_row = pd.DataFrame([{"Category": new_category, "Goal": new_amount}])
                # Combine it with existing data
                updated_df = pd.concat([df_goals, new_row], ignore_index=True)
                # Upload it back to the sheet
                conn.update(worksheet="Goals", data=updated_df)
                st.success(f"Added {new_category} goal successfully!")
                st.rerun()
            else:
                st.warning("Please enter a category name.")

except Exception as e:
    st.error("Connection Error. Check if your Sheet is shared as 'Editor'.")
    st.info(f"Details: {e}")
