import os
import glob
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from urllib.parse import quote_plus
import re

def split_sql_statements(sql):
    # Naive split on semicolon, ignoring those inside quotes
    statements = []
    statement = ''
    in_single_quote = False
    in_double_quote = False
    for char in sql:
        if char == "'":
            in_single_quote = not in_single_quote if not in_double_quote else in_single_quote
        elif char == '"':
            in_double_quote = not in_double_quote if not in_single_quote else in_double_quote
        if char == ';' and not in_single_quote and not in_double_quote:
            if statement.strip():
                statements.append(statement.strip())
            statement = ''
        else:
            statement += char
    if statement.strip():
        statements.append(statement.strip())
    return statements

def print_db_debug(conn):
    try:
        user = conn.execute(text('SELECT current_user')).scalar()
        db = conn.execute(text('SELECT current_database()')).scalar()
        schema = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'nse_raw'"))
        schema_exists = schema.fetchone() is not None
        print(f"[DEBUG] Connected as user: {user}, database: {db}, nse_raw schema exists: {schema_exists}")
        perms = conn.execute(text("SELECT has_schema_privilege(current_user, 'nse_raw', 'CREATE'), has_schema_privilege(current_user, 'nse_raw', 'USAGE')")).fetchone()
        print(f"[DEBUG] CREATE privilege on nse_raw: {perms[0]}, USAGE privilege: {perms[1]}")
    except Exception as e:
        print(f"[ERROR] DB debug info failed: {e}")
    # Try a test table create/drop
    try:
        conn.execute(text('CREATE TABLE IF NOT EXISTS nse_raw._test_perm (id INT)'))
        print("[DEBUG] Test CREATE TABLE succeeded.")
        conn.execute(text('DROP TABLE IF EXISTS nse_raw._test_perm'))
        print("[DEBUG] Test DROP TABLE succeeded.")
    except Exception as e:
        print(f"[ERROR] Test CREATE/DROP TABLE failed: {e}")

def main():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../db_config.yaml'))
    with open(config_path) as f:
        config = yaml.safe_load(f)
    user = quote_plus(config['user'])
    password = quote_plus(config['password'])
    host = config['host']
    port = config['port']
    database = config['database']
    # Show the actual connection string for debug (mask password)
    debug_url = f"postgresql+psycopg2://{user}:***@{host}:{port}/{database}"
    print(f"[DEBUG] Connection string: {debug_url}")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)
    ddl_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/ddl'))
    ddl_files = sorted(glob.glob(os.path.join(ddl_dir, '*.sql')))
    with engine.begin() as conn:
        print_db_debug(conn)
        # Set search_path to nse_raw
        try:
            conn.execute(text('SET search_path TO nse_raw,public'))
        except Exception as e:
            print(f"[ERROR] Could not set search_path: {e}")
        for ddl_file in ddl_files:
            print(f"\n[INFO] Executing {os.path.basename(ddl_file)}...")
            with open(ddl_file, 'r') as f:
                ddl = f.read()
            print(f"[DEBUG] DDL Content:\n{ddl}")
            statements = split_sql_statements(ddl)
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                    print(f"[SUCCESS] Executed statement:\n{stmt}")
                    # If CREATE TABLE, check if table exists
                    m = re.match(r'CREATE TABLE IF NOT EXISTS ([^ (]+)', stmt, re.IGNORECASE)
                    if m:
                        tbl = m.group(1)
                        tbl = tbl.replace('nse_raw.', '')
                        res = conn.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'nse_raw' AND table_name = '{tbl}'"))
                        exists = res.fetchone() is not None
                        print(f"[CHECK] Table nse_raw.{tbl} exists: {exists}")
                except Exception as e:
                    print(f"[ERROR] Failed to execute statement:\n{stmt}\nError: {e}")
        print("[DEBUG] Committed all DDL statements.")
        # Final list of tables
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'nse_raw'"))
        tables = [row[0] for row in result]
        print(f"[DEBUG] Tables in nse_raw schema after DDL execution: {tables}")

if __name__ == '__main__':
    main()
