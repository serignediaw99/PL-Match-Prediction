import pandas as pd
import numpy as np
from sqlalchemy.types import String, Float, Integer, Date, Time
import os

def load_data(file_name='match_logs.csv'):
    file_path = os.path.join('data/backups', file_name)
    return pd.read_csv(file_path)

def clean_data(df):
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Replace empty strings with None (NULL in SQL)
    df = df.replace(r'^\s*$', np.nan, regex=True)

    # Rename columns (add your specific renaming logic here)
    column_mapping = {
        'Date': 'date',
        'Team': 'team',
        'Venue': 'venue',
        'Opponent': 'opponent',
        'shooting_Time': 'time',
        'shooting_Round': 'round',
        'shooting_Day': 'day',
        'shooting_Result': 'result',
        'shooting_GF': 'goals_for',
        'shooting_GA': 'goals_against',
        'shooting_Sh': 'shots',
        'shooting_SoT': 'shots_on_target',
        'shooting_SoT%': 'shots_on_target_percentage',
        'shooting_G/Sh': 'goals_per_shot',
        'shooting_G/SoT': 'goals_per_shot_on_target',
        'shooting_FK': 'free_kick_shots',
        'shooting_PK': 'penalty_kicks_made',
        'shooting_XG': 'expected_goals',
        'shooting_npxG': 'expected_goals_non_penalty',
        'shooting_npxG/Sh': 'expected_goals_per_shot',
        'shooting_G-xG': 'goals_minus_expected_goals',
        'shooting_np:G-xG': 'non_penalty_goals_minus_expected_goals',
        'keeper_SoTA': 'shots_on_target_against',
        'keeper_Saves': 'saves',
        'keeper_Save%': 'save_percentage',
        'keeper_CS': 'clean_sheets',
        'keeper_PSxG+/-': 'expected_goals_plus_minus',
        'keeper_Stp%': 'crosses_stopped_percentage',
        'keeper_Cmp': 'passes_completed',
        'keeper_Att': 'passes_attempted',
        'passing_Cmp%': 'passes_completed_percentage',
        'passing_TotDist': 'total_passing_distance',
        'passing_PrgDist': 'progressive_passing_distance',
        'passing_Ast': 'assists',
        'passing_xAG': 'expected_assisted_goals',
        'passing_xA': 'expected_assists',
        'passing_KP': 'key_passes',
        'passing_1/3': 'passes_final_third',
        'passing_PPA': 'passes_into_penalty_area',
        'passing_CrsPA': 'crosses_into_penalty_area',
        'passing_PrgP': 'progressive_passes',
        'gca_SCA': 'shot_creating_actions',
        'gca_PassLive': 'live_ball_gca',
        'gca_PassDead': 'dead_ball_gca',
        'gca_TO': 'take_on_gca',
        'gca_Sh': 'shot_gca',
        'gca_Fld': 'fouls_drawn_gca',
        'gca_Def': 'defensive_actions_gca',
        'gca_GCA': 'goal_creating_actions',
        'defense_Tkl': 'tackles',
        'defense_TklW': 'tackles_won',
        'defense_Blocks': 'blocks',
        'defense_Sh': 'shots_blocked',
        'defense_Pass': 'passes_blocked',
        'defense_Int': 'interceptions',
        'defense_Clr': 'clearances',
        'defense_Err': 'defensive_errors',
        'possession_Poss': 'possession',
        'possession_Touches': 'touches',
        'possession_Att 3rd': 'attacking_third_touches',
        'possession_Att Pen': 'penalty_area_touches',
        'possession_Att': 'take_ons_attempted',
        'possession_Succ': 'successful_take_ons',
        'possession_Succ%': 'successful_take_ons_%',
        'possession_Carries': 'carries',
        'possession_TotDist': 'total_carrying_distance',
        'possession_PrgDist': 'progressive_carrying_distance',
        'possession_PrgC': 'progressive_carries',
        'possession_1/3': 'carries_into_final_third',
        'possession_Dis': 'dispossessed',
        # Add more column mappings as needed
    }

    df = df.rename(columns=column_mapping)

    return df

def get_column_types(df):
    dtype_dict = {col: String for col in df.columns}  # Default all to String
    dtype_dict.update({
        'Date': Date,
        'Team': String,
        'Venue': String,
        'Opponent': String,
        'Time': Time,
        'Round': String,
        'Day': String,
        'Result': String
    })

    # Update numeric columns to appropriate types
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_columns:
        if df[col].dtype == 'int64':
            dtype_dict[col] = Integer
        else:
            dtype_dict[col] = Float

    return dtype_dict

