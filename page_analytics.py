import streamlit as st

st.title("📊 System Analytics Dashboard")
st.write("Review your historical data crawl speeds and performance logs below.")

# Quick metric scorecards for design testing
col1, col2 = st.columns(2)
col1.metric("⏱️ Avg Search Speed", "0.45 seconds")
col2.metric("💾 Memory Utilization", "14.2 MB")
