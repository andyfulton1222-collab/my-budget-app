import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. APP SETUP
st.set_page_config(page_title="Executive Budget Tracker", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 2. KEY REPAIR & CONNECTION
def get_clean_connection():
    try:
        # Get secrets
        conf = st.secrets["connections"]["gsheets"].to_dict()
        
        # MANUALLY REPAIR THE KEY: Google requires a specific line-break format
        raw_key = conf.get("private_key", "")
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        
        # Remove headers, footers, and all whitespace/newlines
        clean_key = raw_key.replace(header, "").replace(footer, "").strip().replace("\\n", "").replace("\n", "").replace(" ", "")
        
        # Reconstruct the key with a newline every 64 characters (Standard PEM format)
        rebuilt_key = header + "\n"
        for i in range(0, len(clean_key), 64):
            rebuilt_key += clean_key[i:i+64] + "\n"
        rebuilt_key += footer
        
        # Inject fixed key back into config
        conf["private_key"] = rebuilt_key
        
        # Connect using the "Service Account Info" bundle
        return st.connection("gsheets", type=GSheetsConnection, service_account_info=conf)
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.stop()

conn = get_clean_connection()

# 3. DATA LOADING
try:
    df_tx = conn.read(worksheet="Transactions")
    df_goals = conn.read(worksheet="Goals")
except:
    df_tx = pd.DataFrame(columns=['Date', 'Category', 'Amount', 'Note'])
    df_goals = pd.DataFrame(columns=['Category', 'Monthly Goal'])

# 4. SIDEBAR - DATA ENTRY
with st.sidebar:
    st.header("Add New Entry")
    with st.form("add_goal"):
        st.subheader("Set Monthly Goal")
        new_cat = st.text_input("Category Name")
        goal_val = st.number_input("Goal Amount", min_value=0.0)
        
        if st.form_submit_button("Save Goal"):
            new_row = pd.DataFrame([{"Category": new_cat, "Monthly Goal": goal_val}])
            updated_goals = pd.concat([df_goals, new_row], ignore_index=True)
            
            # THE STABLE UPDATE CALL
            try:
                conn.update(worksheet="Goals", data=updated_goals)
                st.success("Goal Saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed. This is likely a Google Permission issue. Error: {e}")

# 5. DASHBOARD
st.subheader("Budget Goals")
st.dataframe(df_goals, use_container_width=True)

st.subheader("Recent Transactions")
st.dataframe(df_tx, use_container_width=True)
