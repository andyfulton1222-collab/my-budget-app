import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. THE FAIL-SAFE CONNECTION ENGINE
try:
    # A. Pull secrets into a modifiable dictionary
    # This prevents the "Secrets does not support item assignment" error
    conf = st.secrets["connections"]["gsheets"].to_dict()
    
    # B. THE RSA KEY CLEANER
    # This ensures the private key is properly formatted even if the Secrets box messes it up
    if "private_key" in conf:
        p_key = conf["private_key"]
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        # Strip everything and rebuild the 64-character block format Google requires
        core_key = p_key.replace(header, "").replace(footer, "").strip().replace(" ", "").replace("\n", "").replace("\\n", "")
        formatted_key = header + "\n"
        for i in range(0, len(core_key), 64):
            formatted_key += core_key[i:i+64] + "\n"
        formatted_key += footer
        conf["private_key"] = formatted_key

    # C. RESOLVE KEYWORD CONFLICTS
    # We pull the URL out and delete the conflicting 'type' and 'spreadsheet_url' keys
    target_url = conf.pop("spreadsheet_url", None)
    conf.pop("type", None)

    # D. INITIALIZE
    # We pass 'spreadsheet' as the primary argument, then unpack the rest (**conf)
    conn = st.connection(
        "gsheets", 
        type=GSheetsConnection, 
        spreadsheet=target_url,
        **conf
    )
    
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.info("Check that your Secrets box has the [connections.gsheets] header.")
    st.stop()

# 3. DATA LOADING LOGIC
def load_data():
    try:
        transactions = conn.read(worksheet="Transactions")
        goals = conn.read(worksheet="Goals")
        return transactions, goals
    except Exception as e:
        # If sheets don't exist yet, return empty dataframes with correct columns
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
            # Get categories from Goals sheet, default to "General" if empty
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
                new_goal = pd.DataFrame([{"Category": str(new_cat), "Monthly Goal": float(goal_val)}])
                updated_goals = pd.concat([df_goals, new_goal], ignore_index=True)
                conn.update(worksheet="Goals", data=updated_goals)
                st.success("Goal Saved!")
                st.rerun()

# 5. MAIN DASHBOARD VISUALS
if not df_goals.empty:
    # Process numeric data
    df_tx['Amount'] = pd.to_numeric(df_tx['Amount'], errors='coerce').fillna(0)
    spend_summary = df_tx.groupby('Category')['Amount'].sum().reset_index()
    
    # Merge goals with actual spending
    comparison = pd.merge(df_goals, spend_summary, on='Category', how='left').fillna(0)
    comparison['Remaining'] = comparison['Monthly Goal'] - comparison['Amount']
    
    # KPI Metrics
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
    
    # Spending Chart
    fig = px.bar(
        comparison, 
        x='Category', 
        y=['Amount', 'Monthly Goal'], 
        barmode='group', 
        title="Monthly Spending vs. Goals",
        color_discrete_sequence=["#00CC96", "#636EFA"]
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Welcome! Start by adding your first Budget Goal in the sidebar.")

st.divider()
st.subheader("Recent Transactions")
st.dataframe(df_tx.sort_values(by="Date", ascending=False), use_container_width=True)
