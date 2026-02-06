import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# 1. SETUP & GOALS
BUDGET_GOALS = {
    "Groceries": 1800, 
    "Gas": 300, 
    "Dining": 300, 
    "General Spend": 1000, 
    "Electric": 250
}

# In the Cloud, we store data in a file named transactions.csv
FILE_NAME = "transactions.csv"

# Create the file if it doesn't exist yet
if not os.path.exists(FILE_NAME):
    pd.DataFrame(columns=["Date", "Category", "Amount", "Note"]).to_csv(FILE_NAME, index=False)

# 2. APP INTERFACE
st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("📊 Financial Command Center")
st.markdown("---")

# 3. SIDEBAR - DATA ENTRY
with st.sidebar:
    st.header("Add New Expense")
    with st.form("entry_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.now())
        cat = st.selectbox("Category", list(BUDGET_GOALS.keys()))
        amt = st.number_input("Amount ($)", min_value=0.0, step=1.0)
        note = st.text_input("Note (e.g., 'Costco Run')")
        
        submit = st.form_submit_button("Save Transaction")
        
        if submit:
            new_data = pd.DataFrame([[date, cat, amt, note]], columns=["Date", "Category", "Amount", "Note"])
            new_data.to_csv(FILE_NAME, mode='a', header=False, index=False)
            st.success("Saved!")
            st.rerun()

# 4. DASHBOARD CALCULATIONS
df = pd.read_csv(FILE_NAME)
df['Date'] = pd.to_datetime(df['Date'])

# Filter for the current month
current_month = datetime.now().month
month_df = df[df['Date'].dt.month == current_month]

# 5. DISPLAY GAUGES
st.subheader(f"Monthly Progress: {datetime.now().strftime('%B %Y')}")
cols = st.columns(len(BUDGET_GOALS))

for i, (category, goal) in enumerate(BUDGET_GOALS.items()):
    spent = month_df[month_df['Category'] == category]['Amount'].sum()
    
    with cols[i]:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=float(spent),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': category, 'font': {'size': 18}},
            gauge={
                'axis': {'range': [0, goal]},
                'bar': {'color': "#0083B8" if spent < goal else "#E74C3C"},
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': goal
                }
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

# 6. TRANSACTION LOG
st.markdown("---")
st.subheader("Recent Transactions")
st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
