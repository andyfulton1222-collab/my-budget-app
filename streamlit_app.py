import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 1. Setup the Google Sheets Links
try:
    sheet_id = st.secrets["spreadsheet_id"]
    url_tx = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Transactions"
    url_goals = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Goals"

    # 2. Load the Data
    df_tx = pd.read_csv(url_tx)
    df_goals = pd.read_csv(url_goals)

    # --- TOP METRICS ---
    st.subheader("Executive Summary")
    total_spent = df_tx['Amount'].sum() if 'Amount' in df_tx.columns else 0
    total_budget = df_goals['Goal'].sum() if 'Goal' in df_goals.columns else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Budgeted", f"${total_budget:,.2f}")
    m2.metric("Total Spent", f"${total_spent:,.2f}")
    m3.metric("Remaining", f"${total_budget - total_spent:,.2f}")

    st.divider()

    # --- TWO COLUMN INPUT SECTION ---
    col_input1, col_input2 = st.columns(2)

    with col_input1:
        st.subheader("💰 Input New Transaction")
        with st.form("transaction_form", clear_on_submit=True):
            date = st.date_input("Date")
            desc = st.text_input("Description (e.g., Starbucks, Rent)")
            amt = st.number_input("Amount ($)", min_value=0.0, step=0.01)
            submitted_tx = st.form_submit_button("Log Transaction")
            if submitted_tx:
                st.info("To save this permanently, paste it into the 'Transactions' tab of your Google Sheet. (Direct writing requires a Private Key).")

    with col_input2:
        st.subheader("🎯 Set New Budget Goal")
        with st.form("goal_form", clear_on_submit=True):
            category = st.text_input("Category (e.g., Groceries)")
            goal_val = st.number_input("Monthly Goal ($)", min_value=0.0, step=10.0)
            submitted_goal = st.form_submit_button("Update Goal")
            if submitted_goal:
                st.info("To save this permanently, add it to the 'Goals' tab of your Google Sheet.")

    st.divider()

    # --- DATA TABLES VIEW ---
    st.subheader("Current Financial Records")
    view_col1, view_col2 = st.columns(2)
    
    with view_col1:
        st.write("**Transactions Log**")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

    with view_col2:
        st.write("**Budget Targets**")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
