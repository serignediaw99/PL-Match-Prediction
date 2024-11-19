import numpy as np
import pandas as pd
from scipy import stats
import pymc as pm

def load_data():
    """Load match data from database"""
    from src.data_loader import load_from_database
    df = load_from_database('match_logs')
    
    # Standardize team names
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
    
    df['team'] = df['team'].replace(team_name_mapping)
    df['opponent'] = df['opponent'].replace(team_name_mapping)
    
    return df

def prepare_data(df, n_recent_matches=5):
    """Prepare data for MCMC model, including form indicators"""
    df['date'] = pd.to_datetime(df['date'])
    
    teams = sorted(df['team'].unique())
    team_idx = {team: i for i, team in enumerate(teams)}
    
    # Initialize lists to hold the processed data
    home_teams = []
    away_teams = []
    home_goals = []
    away_goals = []
    home_shots_on_target = []
    away_shots_on_target = []
    home_xg = []
    away_xg = []
    home_possession = []
    away_possession = []
    
    # Create a dictionary to hold recent form indicators
    recent_form = {team: [] for team in teams}
    
    for _, match in df.iterrows():
        if match['venue'] == 'Home':
            home_teams.append(team_idx[match['team']])
            home_goals.append(match['goals_for'])
            home_shots_on_target.append(match['shots_on_target'])
            home_xg.append(match['shooting_xG'])
            home_possession.append(match['possession'])
            
            # Find the corresponding away team statistics
            away_stats = df[(df['team'] == match['opponent']) & (df['date'] == match['date'])]
            away_teams.append(team_idx[away_stats['team'].values[0]])
            away_goals.append(away_stats['goals_for'].values[0])
            away_shots_on_target.append(away_stats['shots_on_target'].values[0])
            away_xg.append(away_stats['shooting_xG'].values[0])
            away_possession.append(away_stats['possession'].values[0])
            
            # Update recent form indicators
            recent_form[match['team']].append(match['goals_for'])
            recent_form[match['opponent']].append(away_stats['goals_for'].values[0])
            
            # Keep only the last n_recent_matches
            if len(recent_form[match['team']]) > n_recent_matches:
                recent_form[match['team']].pop(0)
            if len(recent_form[match['opponent']]) > n_recent_matches:
                recent_form[match['opponent']].pop(0)

    # Calculate average goals scored in the last n_recent_matches for each team
    avg_goals = {team: np.mean(recent_form[team]) if recent_form[team] else 0 for team in teams}

    # Normalization
    home_possession = np.array(home_possession) / 100.0  # Convert percentage to proportion
    away_possession = np.array(away_possession) / 100.0  # Convert percentage to proportion

    
    return {
        'home_teams': np.array(home_teams),
        'away_teams': np.array(away_teams),
        'home_goals': np.array(home_goals),
        'away_goals': np.array(away_goals),
        'home_shots_on_target': np.array(home_shots_on_target),
        'away_shots_on_target': np.array(away_shots_on_target),
        'home_xg': np.array(home_xg),
        'away_xg': np.array(away_xg),
        'home_possession': home_possession,
        'away_possession': away_possession,
        'n_teams': len(teams),
        'teams': teams,
        'team_idx': team_idx,
        'avg_goals': avg_goals  # Include average goals in the returned data
    }

def build_model(data):
    """Build PyMC model for soccer predictions"""
    with pm.Model() as model:
        # Priors for team attack and defense strengths
        home_advantage = pm.Normal('home_advantage', mu=0.2, sigma=0.1)
        
        # Team-specific parameters
        attack = pm.Normal('attack', mu=0, sigma=1, shape=data['n_teams'])
        defense = pm.Normal('defense', mu=0, sigma=1, shape=data['n_teams'])

        beta_home_xG = pm.Normal('beta_home_xG', mu=0, sigma=1)
        beta_away_xG = pm.Normal('beta_away_xG', mu=0, sigma=1)

        beta_home_possession = pm.Normal('beta_home_possession', mu=0, sigma=1)
        beta_away_possession = pm.Normal('beta_away_possession', mu=0, sigma=1)

        recent_form_coefficient = pm.Normal('recent_form_coefficient', mu=0, sigma=1)

        # Recent form effect
        recent_form_home = pm.math.stack([data['avg_goals'][team] for team in data['teams']])[data['home_teams']] * recent_form_coefficient
        recent_form_away = pm.math.stack([data['avg_goals'][team] for team in data['teams']])[data['away_teams']] * recent_form_coefficient


        # Expected goals 
        theta_home = pm.math.exp(
            attack[data['home_teams']] - 
            defense[data['away_teams']] + 
            home_advantage + 
            recent_form_home +
            beta_home_xG * data['home_xg'] +
            beta_home_possession * data['home_possession'] 
        )
        theta_away = pm.math.exp(
            attack[data['away_teams']] - 
            defense[data['home_teams']] + 
            recent_form_away +
            beta_away_xG * data['away_xg'] + 
            beta_away_possession * data['away_possession']
        )
        
        # Likelihood of observed goals
        home_goals = pm.Poisson('home_goals', mu=theta_home, observed=data['home_goals'])
        away_goals = pm.Poisson('away_goals', mu=theta_away, observed=data['away_goals'])
    
    return model

def sample_model(model, samples=2000):
    """Sample from the model using MCMC"""
    with model:
        trace = pm.sample(
            draws=samples,
            tune=1000,
            return_inferencedata=True,
            cores=4
        )
    return trace

def predict_match(trace, home_team, away_team, data, n_samples=1000):
    """Predict the outcome of a match using the trained model, incorporating all model components."""
    
    # Validate team names
    if home_team not in data['team_idx']:
        raise ValueError(f"Home team '{home_team}' not found in data.")
    if away_team not in data['team_idx']:
        raise ValueError(f"Away team '{away_team}' not found in data.")
    
    home_idx = data['team_idx'][home_team]
    away_idx = data['team_idx'][away_team]
    
    # Extract parameter samples from the trace
    attack_samples = trace.posterior['attack'].values[..., home_idx].flatten()
    defense_samples = trace.posterior['defense'].values[..., away_idx].flatten()
    home_defense_samples = trace.posterior['defense'].values[..., home_idx].flatten()
    away_attack_samples = trace.posterior['attack'].values[..., away_idx].flatten()
    
    home_advantage_samples = trace.posterior['home_advantage'].values.flatten()
    beta_home_xG_samples = trace.posterior['beta_home_xG'].values.flatten()
    beta_away_xG_samples = trace.posterior['beta_away_xG'].values.flatten()
    beta_home_possession_samples = trace.posterior['beta_home_possession'].values.flatten()
    beta_away_possession_samples = trace.posterior['beta_away_possession'].values.flatten()
    recent_form_coeff_samples = trace.posterior['recent_form_coefficient'].values.flatten()
    
    # Retrieve recent form (average goals) for both teams
    recent_form_home = data['avg_goals'][home_team]
    recent_form_away = data['avg_goals'][away_team]
    
    # Calculate recent form effect
    recent_form_home_effect = recent_form_home * recent_form_coeff_samples
    recent_form_away_effect = recent_form_away * recent_form_coeff_samples
    
    home_xg = data['home_xg'][data['team_idx'][home_team]]
    away_xg = data['away_xg'][data['team_idx'][away_team]]

    home_possession = data['home_possession'][data['team_idx'][home_team]]
    away_possession = data['away_possession'][data['team_idx'][away_team]]
    
    # Calculate expected goals (theta) for home and away teams
    theta_home = np.exp(
        attack_samples - 
        defense_samples + 
        home_advantage_samples + 
        recent_form_home_effect +
        beta_home_xG_samples * home_xg +
        beta_home_possession_samples * home_possession
    )
    theta_away = np.exp(
        away_attack_samples - 
        home_defense_samples + 
        recent_form_away_effect +
        beta_away_xG_samples * away_xg +
        beta_away_possession_samples * away_possession
    )
    
    # Sample goals from Poisson distribution
    home_goals = stats.poisson.rvs(theta_home)
    away_goals = stats.poisson.rvs(theta_away)
    
    # Calculate outcome probabilities
    home_wins = np.mean(home_goals > away_goals)
    draws = np.mean(home_goals == away_goals)
    away_wins = np.mean(home_goals < away_goals)
    
    # Calculate expected goals
    expected_home_goals = np.mean(theta_home)
    expected_away_goals = np.mean(theta_away)
    
    return {
        'home_win_prob': home_wins,
        'draw_prob': draws,
        'away_win_prob': away_wins,
        'expected_home_goals': expected_home_goals,
        'expected_away_goals': expected_away_goals
    }


def main():
    # Load and prepare data
    df = load_data()
    data = prepare_data(df)
    
    # Build and sample from model
    model = build_model(data)
    trace = sample_model(model)
    
    # Example prediction
    prediction = predict_match(
        trace=trace,
        home_team='Liverpool',
        away_team='Manchester-City',
        data=data
    )
    
    print("\nMatch Prediction:")
    print(f"Home Win: {prediction['home_win_prob']:.2%}")
    print(f"Draw: {prediction['draw_prob']:.2%}")
    print(f"Away Win: {prediction['away_win_prob']:.2%}")
    print(f"Expected Goals: {prediction['expected_home_goals']:.2f} - {prediction['expected_away_goals']:.2f}")

if __name__ == "__main__":
    main()