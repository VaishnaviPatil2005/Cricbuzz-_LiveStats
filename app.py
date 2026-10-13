
import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Cricbuzz LiveStats",
    page_icon="🏏",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🏏 Cricbuzz LiveStats")

page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Live Match",
        "Top Player Stats",
        "SQL Queries & Analytics",
        "CRUD Operations"
    ]
)

# Load the CSV data
if os.path.exists("cricbuzz_matches.csv"):
    df = pd.read_csv("cricbuzz_matches.csv")
    df.columns = df.columns.str.strip()
else:
    df = pd.DataFrame()
    st.error("cricbuzz_matches.csv not found. Upload it beside app.py.")

# ---------------- HOME PAGE ----------------
if page == "Home":
    st.title("🏏 Cricbuzz LiveStats")
    st.subheader("Cricket Insights and SQL-Based Analytics")

    if df.empty:
        st.warning("No match data available.")
    else:
        filtered_df = df.copy()

        st.sidebar.header("Match Filters")

        if "match_format" in filtered_df.columns:
            formats = sorted(
                filtered_df["match_format"].dropna().astype(str).unique()
            )
            selected_formats = st.sidebar.multiselect(
                "Select match format", formats, default=formats
            )
            filtered_df = filtered_df[
                filtered_df["match_format"].astype(str).isin(selected_formats)
            ]

        if "state" in filtered_df.columns:
            states = sorted(
                filtered_df["state"].dropna().astype(str).unique()
            )
            selected_states = st.sidebar.multiselect(
                "Select match status", states, default=states
            )
            filtered_df = filtered_df[
                filtered_df["state"].astype(str).isin(selected_states)
            ]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Matches", len(filtered_df))

        with col2:
            if "team1" in filtered_df.columns and "team2" in filtered_df.columns:
                teams = pd.concat([
                    filtered_df["team1"], filtered_df["team2"]
                ]).dropna().nunique()
            else:
                teams = 0
            st.metric("Unique Teams", teams)

        with col3:
            series_count = (
                filtered_df["series_name"].dropna().nunique()
                if "series_name" in filtered_df.columns else 0
            )
            st.metric("Series", series_count)

        st.divider()
        left, right = st.columns(2)

        with left:
            st.subheader("Matches by Format")
            if "match_format" in filtered_df.columns:
                format_counts = (
                    filtered_df["match_format"]
                    .fillna("Unknown")
                    .value_counts()
                    .rename_axis("Format")
                    .reset_index(name="Matches")
                )
                fig = px.bar(
                    format_counts, x="Format", y="Matches",
                    title="Match Format Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Matches by Status")
            if "state" in filtered_df.columns:
                state_counts = (
                    filtered_df["state"]
                    .fillna("Unknown")
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Matches")
                )
                fig = px.pie(
                    state_counts, names="Status", values="Matches",
                    title="Match Status Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Match Details")

        display_columns = [
            col for col in [
                "match_id", "match_date", "series_name",
                "match_description", "match_format", "team1",
                "team1_score", "team2", "team2_score", "venue",
                "city", "state", "status"
            ] if col in filtered_df.columns
        ]

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Match Data",
            data=csv_data,
            file_name="cricbuzz_filtered_matches.csv",
            mime="text/csv"
        )

        st.caption(
            "Data is based on the imported Cricbuzz API response. "
            "Refresh the source data to obtain updated match information."
        )

# ---------------- LIVE MATCH PAGE ----------------
elif page == "Live Match":
    st.title("🏏 Live Match")
    st.info("Live API integration and detailed scorecards are not connected yet.")

    if not df.empty:
        if "state" in df.columns:
            live_df = df[
                df["state"].astype(str).str.contains(
                    "live|in progress", case=False, na=False
                )
            ]
            if not live_df.empty:
                st.dataframe(live_df, use_container_width=True, hide_index=True)
            else:
                st.warning(
                    "No matches identified as live in the CSV. "
                    "Connect the Cricbuzz API for current live scores."
                )
        else:
            st.warning("The CSV has no state column to identify live matches.")

# ---------------- TOP PLAYER STATS PAGE ----------------
elif page == "Top Player Stats":
    st.title("📊 Top Player Stats")
    st.info(
        "Batting and bowling leaderboards require player statistics "
        "from the Cricbuzz API or database."
    )

# ---------------- SQL ANALYTICS PAGE ----------------
elif page == "SQL Queries & Analytics":
    st.title("🗄️ SQL Queries & Analytics")
    st.info(
        "Your SQL database connection and analytics queries "
        "must be connected to display query results."
    )

# ---------------- CRUD PAGE ----------------
elif page == "CRUD Operations":
    st.title("✏️ CRUD Operations")
    st.info(
        "Create, Read, Update and Delete forms will be added "
        "after the database connection is configured."
    )
