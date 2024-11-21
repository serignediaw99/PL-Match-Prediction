import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from src.modeling.mcmc import (
    load_data,
    prepare_data,
    build_model,
    sample_model,
    predict_match
)
from pathlib import Path


# Load and prepare data
df = load_data()
data = prepare_data(df)
model = build_model(data)
trace = sample_model(model)

team_name_mapping = {
        "Nott'ham Forest": "Nottingham-Forest",
        "Ipswich Town": "Ipswich-Town",
        "Leicester City": "Leicester-City",
        "Tottenham": "Tottenham-Hotspur",
        "Manchester City": "Manchester-City",
        "Newcastle Utd": "Newcastle-United",
        "West Ham": "West-Ham-United",
        "Aston Villa": "Aston-Villa",
        "Brighton": "Brighton-and-Hove-Albion",
        "Crystal Palace": "Crystal-Palace",
        "Wolves": "Wolverhampton-Wanderers",
        "Manchester Utd": "Manchester-United",
    }

def get_premier_league_matches_by_gameweek(target_gameweek):
    url = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the table by ID
    table = soup.find("table", {"id": "sched_2024-2025_9_1"})
    
    matches = []
    for row in table.find("tbody").find_all("tr"):
        # Get and clean the gameweek cell text
        gameweek_cell = row.find("th", {"data-stat": "gameweek"})
        gameweek_text = gameweek_cell.text.strip() if gameweek_cell else ""
        
        # Proceed only if gameweek matches the target
        if gameweek_text.isdigit() and int(gameweek_text) == target_gameweek:
            date = row.find("td", {"data-stat": "date"}).find("a").text
            home_team = row.find("td", {"data-stat": "home_team"}).text
            away_team = row.find("td", {"data-stat": "away_team"}).text
            
            # Map team names using the team_name_mapping
            home_team = team_name_mapping.get(home_team, home_team)
            away_team = team_name_mapping.get(away_team, away_team)

            matches.append([gameweek_text, date, home_team, away_team])
    
    return pd.DataFrame(matches, columns=["Gameweek", "Date", "Home Team", "Away Team"])

def get_predictions_for_gameweek(target_gameweek):
    # Function to get matches for the specified gameweek
    matches = get_premier_league_matches_by_gameweek(target_gameweek)
    predictions = []

    for match in matches.to_dict(orient='records'):
        prediction = predict_match(
            trace=trace,
            home_team=match['Home Team'],
            away_team=match['Away Team'],
            data=data
        )
        predictions.append({
            'Home Team': match['Home Team'],
            'Away Team': match['Away Team'],
            'Home Win Probability': prediction['home_win_prob'],
            'Draw Probability': prediction['draw_prob'],
            'Away Win Probability': prediction['away_win_prob'],
            'Expected Home Goals': prediction['expected_home_goals'],
            'Expected Away Goals': prediction['expected_away_goals']
        })

    return pd.DataFrame(predictions)

# Streamlit app layout
st.title("Premier League Match Prediction")
st.write("Enter a gameweek number to get predictions for that week.")

# Input for gameweek
gameweek = st.number_input("Gameweek", min_value=1, max_value=38, value=1)

if st.button("Get Predictions"):
    predictions_df = get_predictions_for_gameweek(gameweek)
    if not predictions_df.empty:
        st.write(predictions_df)
    else:
        st.write("No matches found for the selected gameweek.")