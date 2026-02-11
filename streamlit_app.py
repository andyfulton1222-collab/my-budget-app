import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. PAGE SETUP
st.set_page_config(page_title="Executive Finance Tracker", layout="wide")

# 2. CONNECT TO GOOGLE SHEETS
# This uses the [connections.gsheets] section from your Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Helper functions to fetch data from specific tabs
def get_transactions():
    try:
        return conn.read(worksheet="Transactions", ttl="0s")
    except:
        return pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

def get_goals():
    try:
        return conn.read(worksheet="Goals", ttl="0s")
    except:
        return pd.DataFrame(columns=["Category", "Goal"])

# Load current data
df = get_transactions()
goals_df = get_goals()

# 3. SIDEBAR - LOG TRANSACTION & SET GOALS
with st.sidebar:
    st.header("⚙️ Settings & Entry")
    
    with st.expander("Add/Update Category Goals"):
        new_cat = st.text_input("Category Name")
        new_goal = st.number_input("Monthly Goal ($)", min_value=0.0, step=50.0)
        if st.button("Set Goal"):
            # If category exists, update it; otherwise, add it
            if not goals_df.empty and new_cat in goals_df['Category'].values:
                goals_df.loc[goals_df['Category'] == new_cat, 'Goal'] = new_goal
            else:
                new_row = pd.DataFrame([{"Category": new_cat, "Goal": new_goal}])
                goals_df = pd.concat([goals_df, new_row], ignore_index=True)
            
            conn.update(worksheet="Goals", data=goals_df)
            st.success(f"Goal set for {new_cat}!")
            st.rerun()

    st.markdown("---")
    st.header("📝 Log Transaction")
    if goals_df.empty:
        st.warning("Add a category goal first!")
    else:
        categories = goals_df['Category'].tolist()
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date", datetime.now())
            cat = st.selectbox("Category", categories)
            # Allows negative numbers for returns
            amt = st.number_input("Amount ($)", step=1.0)
            note = st.text_input("Note")
            
            if st.form_submit_button("Save"):
                new_entry = pd.DataFrame([[date.strftime('%Y-%m-%d'), cat, amt, note]], 
                                         columns=["Date", "Category", "Amount", "Note"])
                # Append to existing data
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                conn.update(worksheet="Transactions", data=updated_df)
                st.success("Saved to Google Sheets!")
                st.rerun()

# 4. MAIN DASHBOARD
st.title("📊 Executive Finance Summary")

if not df.empty:
    # Ensure Date is actually a datetime object for filtering
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month_Year'] = df['Date'].dt.strftime('%B %Y')
    
    # Month Selector
    available_months = sorted(df['Month_Year'].unique().tolist(), reverse=True)
    current_mo_str = datetime.now().strftime('%B %Y')
    if current_mo_str not in available_months: 
        available_months.insert(0, current_mo_str)
    
    selected_month = st.selectbox("Select View Month", available_months)
    view_df = df[df['Month_Year'] == selected_month]
else:
    selected_month = datetime.now().strftime('%B %Y')
    view_df = pd.DataFrame()

# 5. DISPLAY METRICS
if not goals_df.empty:
    total_goal = goals_df['Goal'].sum()
    total_spent = view_df['Amount'].sum() if not view_df.empty else 0
    remaining = total_goal - total_spent
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Budget", f"${total_goal:,.2f}")
    c2.metric("Total Spent", f"${total_spent:,.2f}")
    c3.metric("Remaining", f"${remaining:,.2f}", delta=f"{remaining:,.2f}")

    st.markdown("---")
    st.subheader(f"Breakdown: {selected_month}")
    
    # Display the Category List with Green/Red status
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
else:
    st.info("Start by adding categories and goals in the sidebar!")

# 6. DATA MANAGEMENT
st.markdown("---")
with st.expander("🛠️ Admin Tools"):
    if st.button("Clear Cache / Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    if not df.empty:
        if st.button("Delete Most Recent Entry", type="primary"):
            updated_df = df.iloc[:-1]
            # Remove helper column before saving back to Sheets
            if 'Month_Year' in updated_df.columns:
                updated_df = updated_df.drop(columns=['Month_Year'])
            conn.update(worksheet="Transactions", data=updated_df)
            st.warning("Last entry deleted!")
            st.rerun()
