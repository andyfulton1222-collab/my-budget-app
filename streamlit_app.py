import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. INITIALIZE CONNECTION (The Precision Handshake)
try:
    # Get all secrets
    raw_secrets = st.secrets["connections"]["gsheets"].to_dict()
    
    # 1. Extract the URL (Streamlit usually wants 'spreadsheet_url')
    target_url = raw_secrets.get("spreadsheet_url")
    
    # 2. Fix the private key line breaks for Google's RSA requirements
    if "private_key" in raw_secrets:
        raw_secrets["private_key"] = raw_secrets["private_key"].replace("\\n", "\n")
    
    # 3. Build the Google Service Account "Envelope"
    sa_info = {
        "type": "service_account",
        "project_id": raw_secrets.get("project_id"),
        "private_key_id": raw_secrets.get("private_key_id"),
        "private_key": raw_secrets.get("private_key"),
        "client_email": raw_secrets.get("client_email"),
        "client_id": raw_secrets.get("client_id"),
        "auth_uri": raw_secrets.get("auth_uri"),
        "token_uri": raw_secrets.get("token_uri"),
        "auth_provider_x509_cert_url": raw_secrets.get("auth_provider_x509_cert_url"),
        "client_x509_cert_url": raw_secrets.get("client_x509_cert_url"),
    }

    # 4. Connect! Using 'spreadsheet_url' as the designated keyword
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        spreadsheet_url=target_url, 
        service_account_info=sa_info
    )
    
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# 3. LOAD DATA
def load_data():
    try:
        # Pulling data from the named tabs in your Google Sheet
        transactions = conn.read(worksheet="Transactions")
        goals = conn.read(worksheet="Goals")
        return transactions, goals
    except Exception:
        # Create empty dataframes if the sheet hasn't been set up yet
        return pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note']), \
               pd.DataFrame(columns=['Category', 'Monthly Goal'])

df_tx, df_goals = load_data()

# 4. SIDEBAR - DATA ENTRY
with st.sidebar:
    st.header("Add New Entry")
    tab1, tab2 = st.tabs(["Transaction", "Set Goal"])
    
    with tab1:
        with st.form("add_transaction"):
            date = st.date_input("Date")
            cat_list = df_goals['Category'].unique().tolist() if not df_goals.empty else ["General"]
            category = st.selectbox("Category", options=cat_list)
            amount = st.number_input("Amount", min_value=0.0, step=0.01)
            note = st.text_input("Note")
            
            if st.form_submit_button("Log Expense"):
                new_data = pd.DataFrame([{"Date": str(date), "Category": category, "Amount": amount, "Note": note}])
                updated_df = pd.concat([df_tx, new_data], ignore_index=True)
                conn.update(worksheet="Transactions", data=updated_df)
                st.success("Expense Logged!")
                st.rerun()

    with tab2:
        with st.form("add_goal"):
            new_cat = st.text_input("New Category Name")
            goal_val = st.number_input("Monthly Budget Goal", min_value=0.0)
            
            if st.form_submit_button("Save Goal"):
                new_goal = pd.DataFrame([{"Category": new_cat, "Monthly Goal": goal_val}])
                updated_goals = pd.concat([df_goals, new_goal], ignore_index=True)
                conn.update(worksheet="Goals", data=updated_goals)
                st.success("Goal Saved!")
                st.rerun()

# 5. MAIN DASHBOARD
if not df_goals.empty:
    df_tx['Amount'] = pd.to_numeric(df_tx['Amount'], errors='coerce').fillna(0)
    spend_summary = df_tx.groupby('Category')['Amount'].sum().reset_index()
    comparison = pd.merge(df_goals, spend_summary, on='Category', how='left').fillna(0)
    comparison['Remaining'] = comparison['Monthly Goal'] - comparison['Amount']
    
    cols = st.columns(min(len(comparison), 4))
    for i, row in comparison.iterrows():
        col_idx = i % 4
        color = "normal" if row['Remaining'] >= 0 else "inverse"
        cols[col_idx].metric(
            label=row['Category'], 
            value=f"${row['Amount']:,.2f}", 
            delta=f"${row['Remaining']:,.2f} Left", 
            delta_color=color
        )
    
    fig = px.bar(comparison, x='Category', y=['Amount', 'Monthly Goal'], barmode='group', title="Monthly Spending vs. Goals")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Start by adding your first Budget Goal in the sidebar!")

st.divider()
st.subheader("Recent Transactions")
st.dataframe(df_tx.sort_values(by="Date", ascending=False), use_container_width=True)
