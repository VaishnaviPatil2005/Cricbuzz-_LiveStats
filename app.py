import streamlit as st

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Live Match",
        "Top Player Stats",
        "SQL Queries & Analytics",
        "CRUD Operations"
    ]
)

if page == "Home":
    st.title("🏏 Cricbuzz LiveStats")
    st.write("Cricket scores and analytics dashboard.")
    st.write("Technologies: Python, Streamlit, SQL, REST API, Pandas")

elif page == "Live Match":
    st.title("🏏 Live Match")
    st.info("Connect the Cricbuzz API to display match information.")

elif page == "Top Player Stats":
    st.title("📊 Top Player Stats")
    st.info("Display batting and bowling statistics here.")

elif page == "SQL Queries & Analytics":
    st.title("🗄️ SQL Queries & Analytics")
    st.info("Add your SQL analytics queries and results here.")

elif page == "CRUD Operations":
    st.title("✏️ CRUD Operations")
    st.info("Add database forms for Create, Read, Update and Delete.")
