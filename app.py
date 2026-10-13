
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)

st.title("🏏 Cricbuzz LiveStats")
st.subheader("Cricket Insights and SQL-Based Analytics")

# Load the CSV file
if os.path.exists("cricbuzz_matches.csv"):
    df = pd.read_csv("cricbuzz_matches.csv")
else:
    st.error("cricbuzz_matches.csv not found. Place it beside app.py.")
    st.stop()

# Clean column names
df.columns = df.columns.str.strip()

# Sidebar filters
st.sidebar.header("Match Filters")

if "match_format" in df.columns:
    formats = sorted(
        df["match_format"].dropna().astype(str).unique()
    )
    selected_formats = st.sidebar.multiselect(
        "Select match format",
        formats,
        default=formats
    )
    df = df[df["match_format"].isin(selected_formats)]

if "state" in df.columns:
    states = sorted(df["state"].dropna().astype(str).unique())
    selected_states = st.sidebar.multiselect(
        "Select match status",
        states,
        default=states
    )
    df = df[df["state"].isin(selected_states)]

# Overview metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Matches", len(df))

with col2:
    if "team1" in df.columns and "team2" in df.columns:
        teams = pd.concat([df["team1"], df["team2"]]).dropna().nunique()
    else:
        teams = 0
    st.metric("Unique Teams", teams)

with col3:
    if "series_name" in df.columns:
        series_count = df["series_name"].dropna().nunique()
    else:
        series_count = 0
    st.metric("Series", series_count)

st.divider()

# Match format chart
left, right = st.columns(2)

with left:
    st.subheader("Matches by Format")
    if "match_format" in df.columns:
        format_counts = (
            df["match_format"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("Format")
            .reset_index(name="Matches")
        )
        fig = px.bar(
            format_counts,
            x="Format",
            y="Matches",
            title="Match Format Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Matches by Status")
    if "state" in df.columns:
        state_counts = (
            df["state"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Matches")
        )
        fig = px.pie(
            state_counts,
            names="Status",
            values="Matches",
            title="Match Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# Match details
st.subheader("Match Details")

display_columns = [
    col for col in [
        "match_id",
        "match_date",
        "series_name",
        "match_description",
        "match_format",
        "team1",
        "team1_score",
        "team2",
        "team2_score",
        "venue",
        "city",
        "state",
        "status"
    ] if col in df.columns
]

st.dataframe(
    df[display_columns],
    use_container_width=True,
    hide_index=True
)

# Download filtered results
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Match Data",
    data=csv,
    file_name="cricbuzz_filtered_matches.csv",
    mime="text/csv"
)

st.caption(
    "Data is based on the imported Cricbuzz API response. "
    "Refresh the source data to obtain updated match information."
)
