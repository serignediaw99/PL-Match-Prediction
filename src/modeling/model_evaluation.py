import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, brier_score_loss
from datetime import datetime

def split_data_by_date(df, split_date):
    """Split data into training and testing sets based on date and filter test set by venue"""
    df['date'] = pd.to_datetime(df['date'])
    train = df[df['date'] < split_date].copy()
    test = df[(df['date'] >= split_date) & (df['venue'] == 'Home')].copy()
    return train, test

def evaluate_predictions(predictions, actuals):
    """Calculate various prediction metrics"""
    metrics = {}
    
    # Calculate Brier scores for each outcome
    actual_home_wins = (actuals['home_goals'] > actuals['away_goals']).astype(int)
    actual_draws = (actuals['home_goals'] == actuals['away_goals']).astype(int)
    actual_away_wins = (actuals['home_goals'] < actuals['away_goals']).astype(int)
    
    metrics['brier_home'] = brier_score_loss(actual_home_wins, predictions['home_win_prob'])
    metrics['brier_draw'] = brier_score_loss(actual_draws, predictions['draw_prob'])
    metrics['brier_away'] = brier_score_loss(actual_away_wins, predictions['away_win_prob'])
    
    # Calculate average goals error
    metrics['mae_home_goals'] = np.mean(np.abs(predictions['expected_home_goals'] - actuals['home_goals']))
    metrics['mae_away_goals'] = np.mean(np.abs(predictions['expected_away_goals'] - actuals['away_goals']))
    
    # Calculate prediction accuracy
    predicted_outcomes = np.argmax([predictions['home_win_prob'], 
                                  predictions['draw_prob'], 
                                  predictions['away_win_prob']], axis=0)
    actual_outcomes = np.where(actual_home_wins == 1, 0,
                             np.where(actual_draws == 1, 1, 2))
    metrics['accuracy'] = np.mean(predicted_outcomes == actual_outcomes)
    
    return metrics

def evaluate_model(model_data, test_data, trace, predict_match_fn):
    """Evaluate model performance on test data"""
    predictions = []
    actuals = []
    
    for _, match in test_data.iterrows():
        # Get prediction for this match
        pred = predict_match_fn(
            trace=trace,
            home_team=match['team'],
            away_team=match['opponent'],
            data=model_data
        )
        
        predictions.append(pred)
        actuals.append({
            'home_goals': match['goals_for'],
            'away_goals': match['goals_against']
        })
    
    # Convert to DataFrames
    pred_df = pd.DataFrame(predictions)
    actual_df = pd.DataFrame(actuals)
    
    # Calculate metrics
    metrics = evaluate_predictions(pred_df, actual_df)
    
    return metrics, pred_df, actual_df

def print_metrics(metrics):
    """Print evaluation metrics in a readable format"""
    print("\nModel Evaluation Metrics:")
    print(f"Prediction Accuracy: {metrics['accuracy']:.3f}")
    print("\nBrier Scores (lower is better):")
    print(f"Home Win: {metrics['brier_home']:.3f}")
    print(f"Draw: {metrics['brier_draw']:.3f}")
    print(f"Away Win: {metrics['brier_away']:.3f}")
    print("\nMean Absolute Error in Goals:")
    print(f"Home Goals: {metrics['mae_home_goals']:.3f}")
    print(f"Away Goals: {metrics['mae_away_goals']:.3f}")