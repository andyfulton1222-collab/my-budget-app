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

# 2. DATA LOADING
df = pd.read_csv(FILE_NAME)
df['Date'] = pd.to_datetime(df['Date'])
goals_df = pd.read_csv(GOAL_FILE)

# 3. SIDEBAR - LOG EXPENSE (Now allows negatives)
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
            st.rerun()

    st.markdown("---")
    st.header("📝 Log Transaction")
    categories = goals_df['Category'].tolist()
    
    if not categories:
        st.warning("Add a category first!")
    else:
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.now())
            cat = st.selectbox("Category", categories)
            # REMOVED min_value=0.0 to allow for negative return amounts
            amt = st.number_input("Amount ($) - Use negative for returns", step=1.0)
            note = st.text_input("Note")
            if st.form_submit_button("Save"):
                pd.DataFrame([[date, cat, amt, note]], columns=["Date", "Category", "Amount", "Note"]).to_csv(FILE_NAME, mode='a', header=False, index=False)
                st.rerun()

# 4. MAIN DASHBOARD - MONTH SELECTOR
st.title("📊 Executive Finance Summary")

if not df.empty:
    df['Month_Year'] = df['Date'].dt.strftime('%B %Y')
    available_months = sorted(df['Month_Year'].unique().tolist(), reverse=True)
    current_mo_str = datetime.now().strftime('%B %Y')
    if current_mo_str not in available_months: available_months.insert(0, current_mo_str)
    selected_month = st.selectbox("Select View Month", available_months)
    view_df = df[df['Month_Year'] == selected_month]
else:
    selected_month = datetime.now().strftime('%B %Y')
    view_df = pd.DataFrame()

# 5. DISPLAY METRICS & TABLE
if not goals_df.empty:
    total_goal = goals_df['Goal'].sum()
    total_spent = view_df['Amount'].sum() if not view_df.empty else 0
    remaining_total = total_goal - total_spent
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Budget", f"${total_goal:,.2f}")
    c2.metric("Total Spent", f"${total_spent:,.2f}")
    c3.metric("Remaining", f"${remaining_total:,.2f}", delta=f"{remaining_total:,.2f}")

    st.markdown("---")
    st.subheader(f"Breakdown: {selected_month}")
    
    for _, row in goals_df.iterrows():
        cat, goal = row['Category'], row['Goal']
        spent = view_df[view_df['Category'] == cat]['Amount'].sum() if not view_df.empty else 0
        diff = goal - spent
        color = "green" if diff >= 0 else "red"
        
        r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
        r1.write(cat)
        r2.write(f"${goal:,.2f}")
        r3.write(f"${spent:,.2f}")
        r4.markdown(f":{color}[**{'+' if diff >= 0 else ''}{diff:,.2f}**]")

# 6. EDIT/DELETE SECTION
st.markdown("---")
with st.expander("🛠️ Edit or Delete Transactions"):
    if not df.empty:
        df_display = df.copy()
        df_display['ID'] = df_display.index
        # Create a label for the dropdown
        df_display['Selector'] = df_display['Date'].dt.strftime('%Y-%m-%d') + " | " + df_display['Category'] + " | $" + df_display['Amount'].astype(str)
        
        to_edit = st.selectbox("Select transaction to modify", df_display['ID'], format_func=lambda x: df_display.loc[x, 'Selector'])
        
        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            new_date = st.date_input("Edit Date", df.loc[to_edit, 'Date'])
            new_cat = st.selectbox("Edit Category", categories, index=categories.index(df.loc[to_edit, 'Category']))
        with col_ed2:
            new_amt = st.number_input("Edit Amount", value=float(df.loc[to_edit, 'Amount']))
            new_note = st.text_input("Edit Note", df.loc[to_edit, 'Note'])
        
        btn1, btn2, _ = st.columns([1, 1, 4])
        if btn1.button("Update Entry"):
            df.loc[to_edit, ['Date', 'Category', 'Amount', 'Note']] = [pd.to_datetime(new_date), new_cat, new_amt, new_note]
            df.drop(columns=['Month_Year'], errors='ignore').to_csv(FILE_NAME, index=False)
            st.success("Updated!")
            st.rerun()
        if btn2.button("Delete Entry", type="primary"):
            df = df.drop(to_edit)
            df.drop(columns=['Month_Year'], errors='ignore').to_csv(FILE_NAME, index=False)
            st.warning("Deleted!")
            st.rerun()
    else:
        st.write("No transactions to edit.")
