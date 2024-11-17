from data_cleaner import load_data, clean_data
from database_manager import DatabaseManager

def main():
    df = load_data()
    cleaned_df = clean_data(df)
    
    db_manager = DatabaseManager()
    db_manager.save_to_database(cleaned_df)

if __name__ == "__main__":
    main()