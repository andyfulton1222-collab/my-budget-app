import streamlit as st
import pandas as pd

st.set_page_config(page_title="Executive Budget", layout="wide")
st.title("📊 Executive Budget Dashboard")

# 1. Get the URL from secrets
try:
    # We clean the URL to ensure it's in 'export' mode
    base_url = st.secrets["spreadsheet"]
    
    # We create two direct links: one for Transactions, one for Goals
    # This bypasses the 'Bad Request' error
    url_tx = f"{base_url.split('/edit')[0]}/gviz/tq?tqx=out:csv&sheet=Transactions"
    url_goals = f"{base_url.split('/edit')[0]}/gviz/tq?tqx=out:csv&sheet=Goals"

    # 2. Read the Data
    df_tx = pd.read_csv(url_tx)
    df_goals = pd.read_csv(url_goals)

    st.success("✅ Dashboard Connected!")

    # --- THE VIEW ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Recent Transactions")
        st.dataframe(df_tx, use_container_width=True)
    with col2:
        st.subheader("🎯 Budget Goals")
        st.dataframe(df_goals, use_container_width=True)

except Exception as e:
    st.error("⚠️ Connection Error")
    st.write("Check your Secrets. It should just be: **spreadsheet = 'YOUR_URL'**")
    st.error(f"Details: {e}")
