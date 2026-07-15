import streamlit as st

st.title("🌐 Live AI Web Scraper Engine")
st.write("Welcome to the Scraper Control Center.")

# A simple text box to test input on this specific page
target_url = st.text_input("Enter a URL to analyze:")
if target_url:
    st.info(f"Target locked on: {target_url}")

import streamlit as st

st.title("📊 System Analytics Dashboard")
st.write("Review your historical data crawl speeds and performance logs below.")

# Quick metric scorecards for design testing
col1, col2 = st.columns(2)
col1.metric("⏱️ Avg Search Speed", "0.45 seconds")
col2.metric("💾 Memory Utilization", "14.2 MB")
