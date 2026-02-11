import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import json

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. INITIALIZE CONNECTION
# We pull the JSON string, fix the newlines, and turn it into a real dictionary
if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    service_account_info = json.loads(st.secrets["connections"]["gsheets"]["service_account_json"])
    conn = st.connection("gsheets", type=GSheetsConnection, service_account=service_account_info)
else:
    st.error("Secrets not found!")
    st.stop()

# 3. LOAD DATA
def load_data():
    try:
        transactions = conn.read(worksheet="Transactions")
        goals = conn.read(worksheet="Goals")
        return transactions, goals
    except Exception:
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
            categories = df_goals['Category'].unique().tolist() if not df_goals.empty else ["General"]
            category = st.selectbox("Category", options=categories)
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
    spend_summary = df_tx.groupby('Category')['Amount'].sum().reset_index()
    comparison = pd.merge(df_goals, spend_summary, on='Category', how='left').fillna(0)
    comparison['Remaining'] = comparison['Monthly Goal'] - comparison['Amount']
    
    cols = st.columns(len(comparison))
    for i, row in comparison.iterrows():
        color = "normal" if row['Remaining'] >= 0 else "inverse"
        cols[i].metric(label=row['Category'], value=f"${row['Amount']:,.2f}", delta=f"${row['Remaining']:,.2f} Left", delta_color=color)
    
    fig = px.bar(comparison, x='Category', y=['Amount', 'Monthly Goal'], barmode='group', title="Spending vs. Goals")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Start by adding a Budget Goal in the sidebar!")

st.divider()
st.subheader("Recent Transactions")
st.dataframe(df_tx.sort_values(by="Date", ascending=False), use_container_width=True)
