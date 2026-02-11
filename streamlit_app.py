import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. INITIALIZE CONNECTION (The Final Precision Handshake)
try:
    # Get secrets and convert to a dictionary
    conf = st.secrets["connections"]["gsheets"].to_dict()
    
    # 1. Pull out the Spreadsheet URL (The library wants it named 'spreadsheet')
    target_url = conf.pop("spreadsheet_url", None)
    
    # 2. Pull out the 'type' to avoid the "multiple values" error
    conf.pop("type", None)
    
    # 3. Fix the private key line breaks
    if "private_key" in conf:
        conf["private_key"] = conf["private_key"].replace("\\n", "\n")
    
    # 4. Connect! Hand the URL to 'spreadsheet' and everything else to 'service_account'
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        spreadsheet=target_url, 
        service_account=conf
    )
except Exception as e:
    st.error(f"Connection Error: {e}")
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
    
    fig = px.bar(comparison, x='Category', y=['Amount', 'Monthly Goal'], 
                 barmode='group', title="Monthly Spending vs. Goals")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Start by adding your first Budget Goal in the sidebar!")

st.divider()
st.subheader("Recent Transactions")
st.dataframe(df_tx.sort_values(by="Date", ascending=False), use_container_width=True)
