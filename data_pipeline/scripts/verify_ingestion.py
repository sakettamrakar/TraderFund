import yaml
from sqlalchemy import create_engine, text
import pandas as pd
from urllib.parse import quote_plus

# Load DB config
def load_db_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_db_config('data_pipeline/db_config.yaml')
    user = quote_plus(config['user'])
    password = quote_plus(config['password'])
    host = config['host']
    port = config['port']
    database = config['database']
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'nse_raw'"))
        tables = [row[0] for row in result]
        print('Tables:', tables)
        for t in tables:
            print(f'\nSample from nse_raw.{t}:')
            try:
                df = pd.read_sql_query(f'SELECT * FROM nse_raw.{t} LIMIT 5', engine)
                print(df)
            except Exception as e:
                print(f'Error reading table {t}: {e}')

if __name__ == '__main__':
    main() 