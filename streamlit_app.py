import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# 1. SETUP & DATA PERSISTENCE
FILE_NAME = "transactions.csv"
GOAL_FILE = "goals.csv"

# Initialize files if they don't exist
for f, cols in [(FILE_NAME, ["Date", "Category", "Amount", "Note"]), (GOAL_FILE, ["Category", "Goal"])]:
    if not os.path.exists(f):
        pd.DataFrame(columns=cols).to_csv(f, index=False)

st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("📊 Financial Command Center")

# 2. SIDEBAR - CONFIGURATION & ENTRY
with st.sidebar:
    st.header("⚙️ Settings & Entry")
    
    # Section A: Add New Category/Goal
    with st.expander("Add/Update Category Goals"):
        new_cat = st.text_input("Category Name")
        new_goal = st.number_input("Monthly Goal ($)", min_value=0.0, step=50.0)
        if st.button("Set Goal"):
            goals_df = pd.read_csv(GOAL_FILE)
            if new_cat in goals_df['Category'].values:
                goals_df.loc[goals_df['Category'] == new_cat, 'Goal'] = new_goal
            else:
                goals_df = pd.concat([goals_df, pd.DataFrame([{"Category": new_cat, "Goal": new_goal}])])
            goals_df.to_csv(GOAL_FILE, index=False)
            st.success(f"Goal set for {new_cat}!")
            st.rerun()

    st.markdown("---")
    
    # Section B: Log Transaction
    st.header("📝 Log Expense")
    goals_df = pd.read_csv(GOAL_FILE)
    categories = goals_df['Category'].tolist()
    
    if not categories:
        st.warning("Add a category above first!")
    else:
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.now())
            cat = st.selectbox("Category", categories)
            amt = st.number_input("Amount ($)", min_value=0.0)
            note = st.text_input("Note")
            if st.form_submit_button("Save"):
                pd.DataFrame([[date, cat, amt, note]], columns=["Date", "Category", "Amount", "Note"]).to_csv(FILE_NAME, mode='a', header=False, index=False)
                st.rerun()

# 3. DASHBOARD
df = pd.read_csv(FILE_NAME)
df['Date'] = pd.to_datetime(df['Date'])
current_month = datetime.now().month
month_df = df[df['Date'].dt.month == current_month]

if not goals_df.empty:
    cols = st.columns(3) # Grid layout
    for i, row in goals_df.iterrows():
        cat, goal = row['Category'], row['Goal']
        spent = month_df[month_df['Category'] == cat]['Amount'].sum()
        
        with cols[i % 3]:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=float(spent),
                title={'text': f"{cat} (Goal: ${goal})"},
                gauge={'axis': {'range': [0, max(goal, spent+1)]},
                       'bar': {'color': "#0083B8" if spent <= goal else "#E74C3C"}}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Transaction History")
st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
