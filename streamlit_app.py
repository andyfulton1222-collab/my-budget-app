import streamlit as st
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

try:
    # 1. Grab the ID directly from secrets
    sheet_id = st.secrets["spreadsheet_id"]
    
    # 2. These links are built specifically for your "Transactions" and "Goals" tabs
    url_tx = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Transactions"
    url_goals = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Goals"

    # 3. Read the data
    df_tx = pd.read_csv(url_tx)
    df_goals = pd.read_csv(url_goals)

    st.success("✅ CONNECTION ESTABLISHED!")

    # --- DISPLAY TABLES ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Recent Transactions")
        st.dataframe(df_tx, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("🎯 Budget Goals")
        st.dataframe(df_goals, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.info("Make sure your Google Sheet tabs are named 'Transactions' and 'Goals' exactly.")
    st.error(f"Error details: {e}")
