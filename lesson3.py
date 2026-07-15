import streamlit as st

# 1. Define the pages and hook them to their file paths
scraper_page = st.Page("page_scraper.py", title="Web Scraper Engine", icon="🌐")
analytics_page = st.Page("page_analytics.py", title="System Analytics", icon="📊")

# 2. Feed the pages into the Navigation system menu
pg = st.navigation([scraper_page, analytics_page])

# 3. Configure the global layout wrapper settings
st.set_page_config(page_title="Multi-Page App", page_icon="⚙️", layout="wide")

# 4. Boot up the selected page engine!
pg.run()
