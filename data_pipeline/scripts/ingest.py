import os
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
import yaml
from utils import find_all_files, normalize_columns
import logging
import fnmatch
from urllib.parse import quote_plus
import pandas.errors

def load_db_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_table_mapping(mapping_path):
    if not os.path.exists(mapping_path):
        return {}
    with open(mapping_path, 'r') as f:
        return yaml.safe_load(f)

def get_engine(config):
    user = quote_plus(config['user'])
    password = quote_plus(config['password'])
    url = f"postgresql+psycopg2://{user}:{password}@{config['host']}:{config['port']}/{config['database']}"
    return create_engine(url)

def run_ddl(engine, ddl_path):
    with open(ddl_path, 'r') as f:
        ddl = f.read()
    with engine.connect() as conn:
        conn.execute(text(ddl))

def resolve_table_name(file_path, table_mapping):
    """
    Resolve the destination table name for a given file using the mapping.
    Raises ValueError if no mapping is found (strict enforcement).
    """
    file_name = os.path.basename(file_path)
    for pattern, table in table_mapping.items():
        if fnmatch.fnmatch(file_name, pattern):
            return table
    msg = f"[ERROR] No table mapping found for file: '{file_name}'. This file will NOT be ingested. Please update table_mapping.yaml if this is a valid file."
    print(msg)
    raise ValueError(msg)

def try_read_csv_with_resolutions(file_path):
    """
    Try to read a CSV file, applying dynamic resolutions if parsing errors occur.
    Returns: (DataFrame, resolution_used)
    """
    try:
        df = pd.read_csv(file_path)
        return df, 'default'
    except pd.errors.ParserError as e:
        # Try skipping up to 5 initial lines to find a valid header
        for skip in range(1, 6):
            try:
                df = pd.read_csv(file_path, skiprows=skip)
                return df, f'skiprows={skip}'
            except Exception:
                continue
        # Could add more resolutions here (e.g., try different delimiters)
        raise e

def get_ddl_columns(ddl_path):
    """
    Parse the DDL file to extract column names in order, stripping quotes and normalizing.
    Returns a list of (original_col, unquoted_col, normalized_col) tuples as they appear in the DDL.
    """
    import re
    columns = []
    with open(ddl_path, 'r') as f:
        ddl = f.read()
    # Find the table definition
    match = re.search(r'CREATE TABLE [^(]+\((.*?)\)\s*;', ddl, re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not parse columns from DDL: {ddl_path}")
    cols_block = match.group(1)
    for line in cols_block.splitlines():
        line = line.strip().rstrip(',')
        if not line or line.startswith('--'):
            continue
        col = line.split()[0]
        # Remove quotes if present
        col_unquoted = col.strip('"`[]')
        from utils import clean_column_name
        columns.append((col, col_unquoted, clean_column_name(col_unquoted)))
    return columns

def ingest_file(engine, file_path, ddl_dir, table_mapping):
    try:
        table_name = resolve_table_name(file_path, table_mapping)
    except ValueError as e:
        print(f"[WARNING] Skipping file due to mapping error: {e}")
        return
    print(f"[DEBUG] Processing file: {file_path}")
    print(f"[DEBUG] Resolved table name: {table_name}")
    ddl_path = os.path.join(ddl_dir, f'{table_name}.sql')
    if os.path.exists(ddl_path):
        print(f"[DEBUG] Found DDL for table: {ddl_path}")
        run_ddl(engine, ddl_path)
        ddl_columns = get_ddl_columns(ddl_path)
        print(f"[DEBUG] DDL columns: {ddl_columns}")
    else:
        print(f"[WARNING] No DDL found for table: {table_name}, skipping DDL execution.")
        ddl_columns = None
    try:
        df, resolution = try_read_csv_with_resolutions(file_path)
        print(f"[DEBUG] Read {len(df)} rows from {file_path} using resolution: {resolution}")
    except Exception as e:
        print(f"[ERROR] Failed to read {file_path}: {e}")
        raise
    from utils import normalize_columns, clean_column_name
    df.columns = normalize_columns(df.columns)
    print(f"[DEBUG] Normalized columns: {df.columns.tolist()}")
    # Special handling for landing_aub: always map first CSV column to 'data_field'
    if table_name == 'landing_aub' and ddl_columns and len(ddl_columns) == 1:
        first_col = df.columns[0]
        mapped = {ddl_columns[0][1]: df[first_col]}
        debug_mapping = {ddl_columns[0][1]: first_col}
        df = pd.DataFrame(mapped)
        print(f"[DEBUG] DDL->CSV column mapping (special landing_aub): {debug_mapping}")
        print(f"[DEBUG] DataFrame columns after DDL mapping: {df.columns.tolist()}")
    elif ddl_columns:
        # Map CSV columns to DDL columns if DDL is available
        # Build a new DataFrame with columns in DDL order, matching by normalized name
        mapped = {}
        csv_col_map = {clean_column_name(c): c for c in df.columns}
        debug_mapping = {}
        for orig_col, unquoted_col, norm_col in ddl_columns:
            if norm_col in csv_col_map:
                mapped[unquoted_col] = df[csv_col_map[norm_col]]
                debug_mapping[unquoted_col] = csv_col_map[norm_col]
            else:
                mapped[unquoted_col] = None
                debug_mapping[unquoted_col] = None
        df = pd.DataFrame(mapped)
        print(f"[DEBUG] DDL->CSV column mapping: {debug_mapping}")
        print(f"[DEBUG] DataFrame columns after DDL mapping: {df.columns.tolist()}")
    try:
        qualified_table = f"nse_raw.{table_name}"
        df.to_sql(qualified_table, engine, if_exists='append', index=False, method='multi')
        print(f"[SUCCESS] Ingested {file_path} into {qualified_table}")
    except Exception as e:
        print(f"[ERROR] Failed to ingest {file_path} into {qualified_table}: {e}")
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Ingest files from a specific date folder (YYYY-MM-DD)')
    parser.add_argument('--file', help='Ingest a specific file')
    parser.add_argument('--all', action='store_true', help='Ingest all files recursively')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    config = load_db_config(os.path.abspath(os.path.join(os.path.dirname(__file__), '../db_config.yaml')))
    table_mapping = load_table_mapping(os.path.abspath(os.path.join(os.path.dirname(__file__), '../table_mapping.yaml')))
    engine = get_engine(config)
    ddl_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/ddl'))
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/input/daily'))

    files = []
    if args.file:
        files = [args.file]
    elif args.date:
        date_dir = os.path.join(data_dir, args.date)
        files = find_all_files(date_dir)
    elif args.all:
        files = find_all_files(data_dir)
    else:
        logging.error('Specify --date, --file, or --all')
        return

    print(f"[DEBUG] Found {len(files)} files to ingest.")
    for file in files:
        try:
            ingest_file(engine, file, ddl_dir, table_mapping)
        except Exception as e:
            print(f"[FATAL] Stopping ingestion due to error on file: {file}")
            raise
    print("[DEBUG] Ingestion completed for all files.")

if __name__ == '__main__':
    main()
