from sqlalchemy import create_engine
from data_cleaner import get_column_types
import os
from dotenv import load_dotenv


class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self.db_params = {
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }
        self.engine = self._create_engine()

    def _create_engine(self):
        return create_engine(
            f"postgresql://{self.db_params['user']}:{self.db_params['password']}"
            f"@{self.db_params['host']}:{self.db_params['port']}/{self.db_params['database']}"
        )

    def save_to_database(self, df, table_name='match_logs'):
        dtype_dict = get_column_types(df)
        df.to_sql(table_name, self.engine, if_exists='replace', index=False, dtype=dtype_dict)
        print(f"Saved cleaned DataFrame to PostgreSQL table: {table_name}")