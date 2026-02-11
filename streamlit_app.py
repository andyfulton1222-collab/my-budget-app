import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📊 My Budget Dashboard")

# Create the connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Read the data
try:
    # This reads the 'Goals' tab from your public sheet
    df = conn.read(worksheet="Goals")
    
    st.success("✅ It's working!")
    st.write("Here is your data:")
    st.dataframe(df)
    
except Exception as e:
    st.error("Still having trouble. Make sure your Sheet is set to 'Anyone with the link'!")
    st.info(f"Technical error: {e}")
