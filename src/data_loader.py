import pandas as pd
import numpy as np
import requests

def load_match_data(match_id, minutes=None):
    """
    Load and process tracking, player, and event data for a match.
    
    Args:
        match_id: The match ID to load
        minutes: Optional number of minutes to load from start (e.g., 10 for first 10 minutes)
    
    Returns:
        DataFrame with synced tracking and event data
    """
    
    # Load tracking data
    tracking_url = f'https://media.githubusercontent.com/media/SkillCorner/opendata/741bdb798b0c1835057e3fa77244c1571a00e4aa/data/matches/{match_id}/{match_id}_tracking_extrapolated.jsonl'
    raw_data = pd.read_json(tracking_url, lines=True)
    
    # Normalize tracking data
    tracking_df = pd.json_normalize(
        raw_data.to_dict("records"),
        "player_data",
        ["frame", "timestamp", "period", "possession", "ball_data"],
    )
    
    # Extract possession info
    tracking_df["possession_player_id"] = tracking_df["possession"].apply(lambda x: x.get("player_id"))
    tracking_df["possession_group"] = tracking_df["possession"].apply(lambda x: x.get("group"))
    
    # Extract ball data
    tracking_df[["ball_x", "ball_y", "ball_z", "is_detected_ball"]] = pd.json_normalize(tracking_df.ball_data)
    
    # Clean up
    tracking_df = tracking_df.drop(columns=["possession", "ball_data"])
    tracking_df["match_id"] = match_id
    
    # Load match metadata
    meta_url = f'https://raw.githubusercontent.com/SkillCorner/opendata/741bdb798b0c1835057e3fa77244c1571a00e4aa/data/matches/{match_id}/{match_id}_match.json'
    raw_match_data = requests.get(meta_url).json()
    raw_match_df = pd.json_normalize(raw_match_data, max_level=2)
    
    # Normalize players
    players_df = pd.json_normalize(
        raw_match_df.to_dict("records"),
        record_path="players",
        meta=["home_team_score", "away_team_score", "date_time", "home_team_side",
              "home_team.name", "home_team.id", "away_team.name", "away_team.id"],
    )
    
    # Filter and enrich players
    players_df = players_df[~((players_df.start_time.isna()) & (players_df.end_time.isna()))]
    
    def time_to_seconds(time_str):
        if time_str is None:
            return 90 * 60
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    
    players_df["total_time"] = players_df["end_time"].apply(time_to_seconds) - players_df["start_time"].apply(time_to_seconds)
    players_df["is_gk"] = players_df["player_role.acronym"] == "GK"
    players_df["match_name"] = players_df["home_team.name"] + " vs " + players_df["away_team.name"]
    players_df["home_away_player"] = np.where(players_df.team_id == players_df["home_team.id"], "Home", "Away")
    players_df["team_name"] = np.where(players_df.team_id == players_df["home_team.id"], 
                                         players_df["home_team.name"], players_df["away_team.name"])
    
    # Handle sides
    players_df[["home_team_side_1st_half", "home_team_side_2nd_half"]] = (
        players_df["home_team_side"].astype(str).str.strip("[]").str.replace("'", "").str.split(", ", expand=True)
    )
    players_df["direction_player_1st_half"] = np.where(players_df.home_away_player == "Home",
                                                         players_df.home_team_side_1st_half,
                                                         players_df.home_team_side_2nd_half)
    players_df["direction_player_2nd_half"] = np.where(players_df.home_away_player == "Home",
                                                          players_df.home_team_side_2nd_half,
                                                          players_df.home_team_side_1st_half)
    
    # Keep relevant columns
    columns_to_keep = ["start_time", "end_time", "match_name", "date_time", "home_team.name", "away_team.name",
                       "id", "short_name", "number", "team_id", "team_name", "player_role.position_group",
                       "total_time", "player_role.name", "player_role.acronym", "is_gk",
                       "direction_player_1st_half", "direction_player_2nd_half"]
    players_df = players_df[columns_to_keep]
    
    # Merge tracking with players
    enriched_tracking_data = tracking_df.merge(players_df, left_on=["player_id"], right_on=["id"])
    
    # Convert timestamp and filter by minutes if specified
    enriched_tracking_data['timestamp'] = pd.to_datetime(enriched_tracking_data['timestamp'])
    
    if minutes is not None:
        start_time = enriched_tracking_data['timestamp'].min()
        enriched_tracking_data = enriched_tracking_data[
            enriched_tracking_data['timestamp'] <= start_time + pd.Timedelta(minutes=minutes)]
    
    # Load events
    de_url = f'https://media.githubusercontent.com/media/SkillCorner/opendata/master/data/matches/{match_id}/{match_id}_dynamic_events.csv'
    try:
        event_data = pd.read_csv(de_url)
    except:
        de_url = f'https://raw.githubusercontent.com/SkillCorner/opendata/master/data/matches/{match_id}/{match_id}_dynamic_events.csv'
        event_data = pd.read_csv(de_url)
    
    # Sync with events
    # event_priority = {
    # 'on_ball_engagement': 1,
    # 'player_possession': 2, 
    # 'passing_option': 3}

    # event_data['priority'] = event_data['event_type'].map(event_priority).fillna(999)
    # event_data_filtered = event_data.sort_values('priority').drop_duplicates(subset=['frame_end'], keep='first')

    synced = enriched_tracking_data.merge(
        event_data,
        left_on="frame", 
        right_on="frame_end", 
        how="left",
        suffixes=("_tracking", "_event"))
    
    synced["runner"] = synced.player_id_tracking == synced.player_id_event
    synced["ball_carrier"] = synced.player_id_tracking == synced.player_in_possession_id
    synced["tip"] = synced.team_id_tracking == synced.team_id_event
    
    return event_data, enriched_tracking_data, synced