import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. THE HANDSHAKE FIX
# This converts the text "\n" from your Secrets into real line breaks for Google
if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
    if "private_key" in st.secrets["connections"]["gsheets"]:
        raw_key = st.secrets["connections"]["gsheets"]["private_key"]
        st.secrets["connections"]["gsheets"]["private_key"] = raw_key.replace("\\n", "\n")

# 2. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# Initialize Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. LOAD DATA
def load_data():
    try:
        transactions = conn.read(worksheet="Transactions")
        goals = conn.read(worksheet="Goals")
        return transactions, goals
    except Exception:
        # Create empty DataFrames if sheets are new/empty
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
            # Pull categories from goals sheet
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
    # Summarize spending
    spend_summary = df_tx.groupby('Category')['Amount'].sum().reset_index()
    
    # Merge with goals
    comparison = pd.merge(df_goals, spend_summary, on='Category', how='left').fillna(0)
    comparison['Remaining'] = comparison['Monthly Goal'] - comparison['Amount']
    
    # Metrics
    cols = st.columns(len(comparison))
    for i, row in comparison.iterrows():
        color = "normal" if row['Remaining'] >= 0 else "inverse"
        cols[i].metric(
            label=row['Category'], 
            value=f"${row['Amount']:,.2f}", 
            delta=f"${row['Remaining']:,.2f} Left",
            delta_color=color
        )
    
    # Chart
    fig = px.bar(comparison, x='Category', y=['Amount', 'Monthly Goal'], 
                 barmode='group', title="Spending vs. Goals")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Start by adding a Budget Goal in the sidebar!")

st.divider()
st.subheader("Recent Transactions")
st.dataframe(df_tx.sort_values(by="Date", ascending=False), use_container_width=True)
