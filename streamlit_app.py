import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. SETUP & DATA PERSISTENCE
FILE_NAME = "transactions.csv"
GOAL_FILE = "goals.csv"

for f, cols in [(FILE_NAME, ["Date", "Category", "Amount", "Note"]), (GOAL_FILE, ["Category", "Goal"])]:
    if not os.path.exists(f):
        pd.DataFrame(columns=cols).to_csv(f, index=False)

st.set_page_config(page_title="Executive Finance Tracker", layout="wide")

# 2. DATA LOADING & PREP
df = pd.read_csv(FILE_NAME)
df['Date'] = pd.to_datetime(df['Date'])
goals_df = pd.read_csv(GOAL_FILE)

# 3. SIDEBAR - CONFIGURATION & ENTRY
with st.sidebar:
    st.header("⚙️ Settings & Entry")
    
    with st.expander("Add/Update Category Goals"):
        new_cat = st.text_input("Category Name")
        new_goal = st.number_input("Monthly Goal ($)", min_value=0.0, step=50.0)
        if st.button("Set Goal"):
            if new_cat in goals_df['Category'].values:
                goals_df.loc[goals_df['Category'] == new_cat, 'Goal'] = new_goal
            else:
                goals_df = pd.concat([goals_df, pd.DataFrame([{"Category": new_cat, "Goal": new_goal}])], ignore_index=True)
            goals_df.to_csv(GOAL_FILE, index=False)
            st.success(f"Goal set for {new_cat}!")
            st.rerun()

    st.markdown("---")
    st.header("📝 Log Expense")
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

# 4. MAIN DASHBOARD - MONTH SELECTOR
st.title("📊 Executive Finance Summary")

# Create a list of available months from the data for the dropdown
if not df.empty:
    df['Month_Year'] = df['Date'].dt.strftime('%B %Y')
    available_months = df['Month_Year'].unique().tolist()
    current_mo_str = datetime.now().strftime('%B %Y')
    
    if current_mo_str not in available_months:
        available_months.insert(0, current_mo_str)
    
    # The Selector
    selected_month = st.selectbox("Select View Month", available_months, index=available_months.index(current_mo_str))
    
    # Filter data for selected month
    view_df = df[df['Month_Year'] == selected_month]
else:
    selected_month = datetime.now().strftime('%B %Y')
    view_df = pd.DataFrame()
    st.info("No transactions found. Log an expense to begin!")

st.markdown("---")

# 5. DISPLAY RESULTS
if not goals_df.empty:
    total_goal = goals_df['Goal'].sum()
    total_spent = view_df['Amount'].sum() if not view_df.empty else 0
    remaining_total = total_goal - total_spent
    
    # Header Metric
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Budget", f"${total_goal:,.2f}")
    c2.metric("Total Spent", f"${total_spent:,.2f}")
    c3.metric("Remaining", f"${remaining_total:,.2f}", delta=f"{remaining_total:,.2f}")

    st.markdown("---")
    st.subheader(f"Breakdown: {selected_month}")
    
    # Table Header
    h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
    h1.write("**Category**")
    h2.write("**Budgeted**")
    h3.write("**Spent**")
    h4.write("**Status (+/-)**")
    st.divider()

    for _, row in goals_df.iterrows():
        cat, goal = row['Category'], row['Goal']
        spent = view_df[view_df['Category'] == cat]['Amount'].sum() if not view_df.empty else 0
        difference = goal - spent
        
        color = "green" if difference >= 0 else "red"
        symbol = "+" if difference >= 0 else ""
        
        r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
        r1.write(cat)
        r2.write(f"${goal:,.2f}")
        r3.write(f"${spent:,.2f}")
        r4.markdown(f":{color}[**{symbol}{difference:,.2f}**]")
else:
    st.info("Start by adding categories and goals in the sidebar!")

st.markdown("---")
st.subheader(f"Activity for {selected_month}")
if not view_df.empty:
    st.dataframe(view_df.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.write("No transactions for this month yet.")
