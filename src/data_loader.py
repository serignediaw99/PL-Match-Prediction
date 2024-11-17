import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


def load_from_database(table_name='match_logs'):

    # Load environment variables
    load_dotenv()

    # Database connection parameters
    db_params = {
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }

    # Create SQLAlchemy engine
    engine = create_engine(f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}")

    # Read data from PostgreSQL
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, engine)
    
    print(f"Loaded {len(df)} rows from {table_name}")
    return df

if __name__ == "__main__":
    df = load_from_database()
    print(f"DataFrame columns: {df.columns.tolist()}")