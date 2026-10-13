
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests

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
    st.caption("Live cricket updates powered by Cricbuzz API")

    if st.button("🔄 Refresh Live Matches"):
        st.cache_data.clear()

    @st.cache_data(ttl=60)
    def get_live_matches():
        url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

        headers = {
            "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
            "X-RapidAPI-Host": st.secrets.get(
                "RAPIDAPI_HOST",
                "cricbuzz-cricket.p.rapidapi.com"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )
        response.raise_for_status()
        return response.json()

    try:
        data = get_live_matches()
        matches = []

        # Extract matches from the API response
        for match_type in data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                wrapper = series.get("seriesAdWrapper", {})
                for item in wrapper.get("matches", []):
                    info = item.get("matchInfo", {})
                    score = item.get("matchScore", {})

                    if info:
                        matches.append({
                            "info": info,
                            "score": score
                        })

        if not matches:
            st.info("No live matches were returned by the API.")
        else:
            st.success(f"Found {len(matches)} live match listings.")

            for match in matches:
                info = match["info"]
                score = match["score"]

                team1 = info.get("team1", {}).get(
                    "teamName", "Team 1"
                )
                team2 = info.get("team2", {}).get(
                    "teamName", "Team 2"
                )

                st.subheader(f"{team1} vs {team2}")
                st.write(
                    f"**Match:** {info.get('matchDesc', 'Cricket Match')}"
                )
                st.write(
                    f"**Format:** {info.get('matchFormat', 'N/A')}"
                )
                st.write(
                    f"**Venue:** "
                    f"{info.get('venueInfo', {}).get('ground', 'N/A')}, "
                    f"{info.get('venueInfo', {}).get('city', '')}"
                )
                st.write(
                    f"**Status:** {info.get('status', 'Status unavailable')}"
                )

                for team_key, team_name in [
                    ("team1Score", team1),
                    ("team2Score", team2)
                ]:
                    team_score = score.get(team_key, {})
                    for innings_key, innings in team_score.items():
                        if isinstance(innings, dict):
                            st.write(
                                f"**{team_name}** — "
                                f"{innings.get('runs', 0)}/"
                                f"{innings.get('wickets', 0)} "
                                f"({innings.get('overs', 0)} overs)"
                            )

                st.divider()

    except KeyError:
        st.error(
            "RAPIDAPI_KEY is missing. Check your Streamlit Cloud Secrets."
        )
    except requests.exceptions.HTTPError as error:
        st.error(
            f"The Cricbuzz API returned an HTTP error: {error}. "
            "Check your API key, subscription and endpoint access."
        )
    except requests.exceptions.RequestException as error:
        st.error(f"Could not connect to Cricbuzz API: {error}")
    except Exception as error:
        st.error(f"Could not load match data: {error}")


# ---------------- TOP PLAYER STATS PAGE ----------------


elif page == "Top Player Stats":
    st.title("📊 Top Player Stats")

    player_name = st.text_input(
        "Search Player",
        placeholder="Enter a player name, e.g. Virat Kohli"
    )

    if st.button("Search Player"):
        if not player_name.strip():
            st.warning("Please enter a player name.")
        else:
            try:
                headers = {
                    "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
                    "X-RapidAPI-Host": st.secrets.get(
                        "RAPIDAPI_HOST",
                        "cricbuzz-cricket.p.rapidapi.com"
                    )
                }

                response = requests.get(
                    "https://cricbuzz-cricket.p.rapidapi.com/"
                    "stats/v1/player/search",
                    headers=headers,
                    params={"plrN": player_name.strip()},
                    timeout=20
                )
                response.raise_for_status()
                data = response.json()

                players = data.get("player", [])

                if not players:
                    st.warning(
                        "No players found. Try another name."
                    )
                else:
                    player_options = {
                        f"{p.get('name', 'Unknown')} "
                        f"(ID: {p.get('id')})": p
                        for p in players
                        if p.get("id") is not None
                    }

                    if player_options:
                        selected = st.selectbox(
                            "Select Player",
                            list(player_options.keys())
                        )
                        player = player_options[selected]
                        player_id = player["id"]

                        st.subheader(
                            player.get("name", "Player Statistics")
                        )

                        tab1, tab2 = st.tabs(
                            ["Batting Statistics", "Bowling Statistics"]
                        )

                        for tab, stat_type in [
                            (tab1, "batting"),
                            (tab2, "bowling")
                        ]:
                            with tab:
                                url = (
                                    "https://cricbuzz-cricket.p."
                                    "rapidapi.com/stats/v1/player/"
                                    f"{player_id}/{stat_type}"
                                )

                                result = requests.get(
                                    url,
                                    headers=headers,
                                    timeout=20
                                )
                                result.raise_for_status()
                                stats = result.json()

                                rows = []
                                for block in stats.get("values", []):
                                    values = block.get("values", [])
                                    if values:
                                        rows.append({
                                            "Statistic": values[0],
                                            "Test": values[1]
                                                if len(values) > 1 else "-",
                                            "ODI": values[2]
                                                if len(values) > 2 else "-",
                                            "T20": values[3]
                                                if len(values) > 3 else "-",
                                            "IPL": values[4]
                                                if len(values) > 4 else "-"
                                        })

                                if rows:
                                    st.dataframe(
                                        pd.DataFrame(rows),
                                        use_container_width=True,
                                        hide_index=True
                                    )
                                else:
                                    st.info(
                                        "No statistics returned for "
                                        f"this player's {stat_type}."
                                    )
                    else:
                        st.warning("No valid player IDs were returned.")

            except KeyError:
                st.error(
                    "RAPIDAPI_KEY is missing from Streamlit Secrets."
                )
            except requests.exceptions.HTTPError as error:
                st.error(
                    f"API request failed: {error}. Check your "
                    "subscription and API endpoint access."
                )
            except requests.exceptions.RequestException as error:
                st.error(f"Connection error: {error}")
            except (ValueError, TypeError) as error:
                st.error(f"Could not process the API response: {error}")



# ---------------- SQL ANALYTICS PAGE ----------------

elif page == "SQL Queries & Analytics":
    st.title("📊 SQL Queries & Analytics")

    st.info(
        "Analytics are calculated from cricbuzz_matches.csv. "
        "Connect a hosted MySQL database to execute SQL queries directly."
    )

    df = pd.read_csv("cricbuzz_matches.csv")
    df.columns = df.columns.str.strip()

    st.subheader("1. Total Matches")
    st.metric("Total Matches", len(df))

    st.subheader("2. Matches by Format")
    if "match_format" in df.columns:
        st.dataframe(
            df["match_format"].value_counts().reset_index()
            .rename(columns={
                "match_format": "Format",
                "count": "Matches"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.subheader("3. Matches by Status")
    if "status" in df.columns:
        st.dataframe(
            df["status"].value_counts().reset_index()
            .rename(columns={
                "status": "Status",
                "count": "Matches"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.subheader("4. Matches by Team")
    team_counts = pd.concat([
        df["team1"].dropna(),
        df["team2"].dropna()
    ]).value_counts().reset_index()
    team_counts.columns = ["Team", "Matches"]

    st.dataframe(
        team_counts,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("5. Matches by Venue")
    if "venue" in df.columns:
        st.dataframe(
            df["venue"].value_counts().head(10).reset_index()
            .rename(columns={
                "venue": "Venue",
                "count": "Matches"
            }),
            use_container_width=True,
            hide_index=True
        )

# ---------------- CRUD PAGE ----------------

elif page == "CRUD Operations":
    st.title("✏️ CRUD Operations")
    st.write("Manage cricket match records.")

    if df.empty:
        st.warning("No CSV data available.")
    else:
        operation = st.selectbox(
            "Choose operation",
            ["Read", "Create", "Update", "Delete"]
        )

        if operation == "Read":
            st.subheader("View Match Records")
            st.dataframe(df, use_container_width=True, hide_index=True)

        elif operation == "Create":
            st.subheader("Add a Match Record")

            with st.form("create_match_form"):
                match_id = st.text_input("Match ID")
                series_name = st.text_input("Series Name")
                team1 = st.text_input("Team 1")
                team2 = st.text_input("Team 2")
                match_format = st.selectbox(
                    "Match Format", ["Test", "ODI", "T20"]
                )

                submitted = st.form_submit_button("Add Match")

                if submitted:
                    st.info(
                        "Form submitted. Saving records requires a "
                        "configured writable database."
                    )

        elif operation == "Update":
            st.subheader("Update a Match Record")
            st.info(
                "Update form requires a writable database connection "
                "to save changes."
            )

        elif operation == "Delete":
            st.subheader("Delete a Match Record")
            st.info(
                "Delete operation requires a writable database connection."
            )

