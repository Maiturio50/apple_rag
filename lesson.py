import streamlit as st

st.title("🏗️ Week 1: Advanced Interface Layouts")
st.write("Type you information below to test Streamlit's reactive grid system")

# 1. Create three layout pillars side-by-side
left_col, center_col, right_col = st.columns(3)

# 2. Add an input component inside the Left column
with left_col:
    st.subheader("Pillar 1")
    user_name = st.text_input("MigIcy")

# 3. Add an interactive slider component inside the Center column
with center_col:
    st.subheader("Pillar 2")
    ai_creativity = st.slider("1.0")

# 4. Add a selection choice dropdown inside the Right column
with right_col:
    st.subheader("Pillar 3")
    selected_model = st.selectbox("Choose LLM Model:", ["gpt-4o-mini", "gpt-4o", "claude-3-5-sonnet"])

st.markdown("___")
st.subheader("📊 Real-Time Input Analytics")

st.success(f"Hello {user_name}! You configured {selected_model} with a creativity score of {ai_creativity}.")

st.markdown("---")
st.subheader("🕵️‍♂️ Hidden Configurations")

# 1. Draw an interactive checkbox widget on the screen
show_advanced_details = st.checkbox("Show Developer Debug Logs")

# 2. This conditional statement only executes if the checkbox is checked!
if show_advanced_details:
    st.warning("⚠️ INTERNAL SYSTEM DEBUG INFO:")
    st.code(f"Active Memory Address: Localhost:8501\nTarget Node: {selected_model}\nUser Token: Verified")
