# Premier League Match Prediction

This project aims to predict the outcomes of Premier League matches using historical data and Markov chain Monte Carlo methods. By analyzing match statistics, team performance, and player metrics, the model provides insights into potential match results.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [License](#license)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/serignediaw99/premier-league-match-prediction.git
   cd premier-league-match-prediction
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Imports

```python
from src.modeling.mcmc import (
    load_data,
    prepare_data,
    build_model,
    sample_model,
    predict_match
)
from src.modeling.model_evaluation import (
    split_data_by_date,
    evaluate_model,
    print_metrics
)
```

### Loading and Preparing Data

```python
# Load all data
df = load_data()

# Split into training and testing
split_date = '2024-11-06'  # Adjust this date as needed
train_df, test_df = split_data_by_date(df, split_date)

# Prepare training data and build model
train_data = prepare_data(train_df)
```

### Run Model

```python
model = build_model(train_data)
trace = sample_model(model)
```

### Evaluate Model

```python
metrics, predictions, actuals = evaluate_model(
    model_data=train_data,
    test_data=test_df,
    trace=trace,
    predict_match_fn=predict_match
)

print_metrics(metrics)
```

### Predicting Matches

```python
# Combine test_df and predictions
results_df = test_df.copy()  # Create a copy of test_df to avoid modifying the original

# Add predictions to the results DataFrame
results_df['home_win_prob'] = predictions['home_win_prob'].values
results_df['draw_prob'] = predictions['draw_prob'].values
results_df['away_win_prob'] = predictions['away_win_prob'].values
results_df['expected_home_goals'] = predictions['expected_home_goals'].values
results_df['expected_away_goals'] = predictions['expected_away_goals'].values

# Create matchup column
results_df['matchup'] = results_df['team'] + ' vs. ' + results_df['opponent']

# Format the result as score (goals_for - goals_against)
results_df['actual_score'] = results_df['goals_for'].astype(str) + '-' + results_df['goals_against'].astype(str)

# Select relevant columns to display
results_df = results_df[['date', 'matchup', 'actual_score', 'home_win_prob', 'draw_prob', 'away_win_prob', 'expected_home_goals', 'expected_away_goals']]

# Display the combined results
print(results_df.head(10).to_string(index=False))
```

## Features

- **Data Scraping**: Automatically scrape match statistics from fbref.com.
- **Data Cleaning**: Clean and preprocess the scraped data for analysis.
- **Statistical Modeling**: Use MCMC methods to build predictive models for match outcomes.
- **Visualization**: Generate visualizations to analyze team performance and match statistics.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.