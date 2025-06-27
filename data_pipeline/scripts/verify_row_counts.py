import os
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd

def load_db_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../db_config.yaml'))
    with open(config_path) as f:
        config = yaml.safe_load(f)
    url = URL.create(
        drivername='postgresql+psycopg2',
        username=config['user'],
        password=config['password'],
        host=config['host'],
        port=config['port'],
        database=config['database']
    )
    engine = create_engine(url)
    print('Row counts and sample data for tables in nse_raw:')
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'nse_raw'"))
        tables = [row[0] for row in result]
        for table in sorted(tables):
            try:
                count = conn.execute(text(f'SELECT COUNT(*) FROM nse_raw."{table}"')).scalar()
                print(f'{table}: {count} rows')
                df = pd.read_sql_query(f'SELECT * FROM nse_raw."{table}" LIMIT 5', engine)
                print(df)
            except Exception as e:
                print(f'{table}: ERROR - {e}')

if __name__ == '__main__':
    main()
