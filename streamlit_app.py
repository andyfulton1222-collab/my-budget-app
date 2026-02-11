import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# THE FAIL-SAFE HANDSHAKE
try:
    # We pull the secrets and build the exact object Google expects
    creds = st.secrets["connections"]["gsheets"]
    
    conn = st.connection(
        "gsheets",
        type=GSheetsConnection,
        spreadsheet=creds["spreadsheet_url"],
        project_id=creds["project_id"],
        private_key_id=creds["private_key_id"],
        private_key=creds["private_key"],
        client_email=creds["client_email"],
        client_id=creds["client_id"],
        auth_uri=creds["auth_uri"],
        token_uri=creds["token_uri"],
        auth_provider_x509_cert_url=creds["auth_provider_x509_cert_url"],
        client_x509_cert_url=creds["client_x509_cert_url"]
    )
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# LOAD DATA
def load_data():
    try:
        transactions = conn.read(worksheet="Transactions")
        goals = conn.read(worksheet="Goals")
        return transactions, goals
    except Exception:
        return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note']), \
               pd.DataFrame(columns=['Category', 'Monthly Goal'])

df_tx, df_goals = load_data()

# SIDEBAR & DASHBOARD (Rest of logic remains the same)
with st.sidebar:
    st.header("Add New Entry")
    tab1, tab2 = st.tabs(["Transaction", "Set Goal"])
    
    with tab1:
        with st.form("add_tx"):
            date = st.date_input("Date")
            cat_list = df_goals['Category'].unique().tolist() if not df_goals.empty else ["General"]
            category = st.selectbox("Category", options=cat_list)
            amount = st.number_input("Amount", min_value=0.0)
            if st.form_submit_button("Log Expense"):
                new_data = pd.DataFrame([{"Date": str(date), "Category": category, "Amount": amount}])
                updated_df = pd.concat([df_tx, new_data], ignore_index=True)
                conn.update(worksheet="Transactions", data=updated_df)
                st.success("Logged!")
                st.rerun()

    with tab2:
        with st.form("add_goal"):
            new_cat = st.text_input("New Category Name")
            goal_val = st.number_input("Monthly Budget Goal", min_value=0.0)
            if st.form_submit_button("Save Goal"):
                new_goal = pd.DataFrame([{"Category": str(new_cat), "Monthly Goal": float(goal_val)}])
                updated_goals = pd.concat([df_goals, new_goal], ignore_index=True)
                conn.update(worksheet="Goals", data=updated_goals)
                st.success("Goal Saved!")
                st.rerun()

# Display logic
if not df_goals.empty:
    st.dataframe(df_tx)
