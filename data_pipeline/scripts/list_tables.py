import os
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

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
    print('Tables in DB:')
    with engine.connect() as conn:
        res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        print([r[0] for r in res])

if __name__ == '__main__':
    main()
