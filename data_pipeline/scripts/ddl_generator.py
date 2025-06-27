import os
import re
import pandas as pd
from utils import find_all_files, normalize_columns, infer_schema

# List of reserved PostgreSQL keywords (partial, can be extended)
RESERVED_KEYWORDS = set([
    'all', 'analyse', 'analyze', 'and', 'any', 'array', 'as', 'asc', 'asymmetric', 'authorization',
    'binary', 'both', 'case', 'cast', 'check', 'collate', 'column', 'concurrently', 'constraint',
    'create', 'cross', 'current_catalog', 'current_date', 'current_role', 'current_schema',
    'current_time', 'current_timestamp', 'current_user', 'default', 'deferrable', 'desc', 'distinct',
    'do', 'else', 'end', 'except', 'false', 'fetch', 'for', 'foreign', 'from', 'grant', 'group',
    'having', 'in', 'initially', 'inner', 'intersect', 'into', 'is', 'isnull', 'join', 'lateral',
    'leading', 'left', 'like', 'limit', 'localtime', 'localtimestamp', 'natural', 'not', 'notnull',
    'null', 'offset', 'on', 'only', 'or', 'order', 'outer', 'overlaps', 'placing', 'primary',
    'references', 'returning', 'right', 'select', 'session_user', 'similar', 'some', 'symmetric',
    'table', 'then', 'to', 'trailing', 'true', 'union', 'unique', 'user', 'using', 'variadic',
    'verbose', 'when', 'where', 'window', 'with', 'authorization', 'between', 'bigint', 'boolean',
    'character', 'coalesce', 'date', 'double', 'exists', 'extract', 'float', 'int', 'integer',
    'interval', 'national', 'nchar', 'none', 'numeric', 'real', 'smallint', 'substring', 'time',
    'timestamp', 'varchar'
])

def quote_identifier(identifier: str) -> str:
    """Quote the identifier if it is a reserved keyword or contains special chars."""
    if identifier.lower() in RESERVED_KEYWORDS or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        return f'"{identifier}"'
    return identifier

def make_unique_columns(columns):
    seen = {}
    unique_cols = []
    for col in columns:
        base = col
        i = 1
        while col in seen:
            i += 1
            col = f"{base}_{i}"
        seen[col] = True
        unique_cols.append(col)
    return unique_cols

def generate_ddl(table_name: str, schema: dict) -> str:
    # Ensure unique column names
    orig_cols = list(schema.keys())
    unique_cols = make_unique_columns(orig_cols)
    col_map = dict(zip(orig_cols, unique_cols))
    # Use fully qualified table name with nse_raw schema
    qualified_table_name = f"nse_raw.{table_name}"
    ddl = "CREATE SCHEMA IF NOT EXISTS nse_raw;\n"
    ddl += f"CREATE TABLE IF NOT EXISTS {qualified_table_name} (\n"
    cols = []
    for orig_col, dtype in schema.items():
        col = col_map[orig_col]
        # Always quote every column name
        col = quote_identifier(col)
        if dtype == 'NUMERIC':
            sql_type = 'NUMERIC(18,4)'
        elif dtype == 'DATE':
            sql_type = 'DATE'
        elif dtype == 'TIMESTAMP':
            sql_type = 'TIMESTAMP'
        else:
            sql_type = 'TEXT'
        cols.append(f"    {col} {sql_type}")
    ddl += ',\n'.join(cols)
    ddl += '\n);'
    return ddl

def clean_table_name(filename: str) -> str:
    # Remove date patterns and add landing_ prefix
    name = os.path.splitext(os.path.basename(filename))[0].lower()
    # Remove trailing date patterns (e.g., _26062025, _2025120_26062025, etc.)
    name = re.sub(r'(_\d{6,8})+$', '', name)
    name = re.sub(r'(_\d{6,8})+_', '_', name)
    name = re.sub(r'_\d{8,}', '', name)
    name = re.sub(r'_\d{6,}', '', name)
    # Remove any remaining date-like patterns
    name = re.sub(r'_\d{4,}', '', name)
    # Add landing_ prefix
    if not name.startswith('landing_'):
        name = f'landing_{name}'
    return name

def safe_columns(cols):
    safe = []
    for i, c in enumerate(cols):
        c = str(c).strip()
        if not c or c.isdigit():
            c = f'col_{i+1}'
        c = re.sub(r'[^a-zA-Z0-9_]', '_', c)
        if not re.match(r'^[a-zA-Z_]', c):
            c = f'col_{i+1}_{c}'
        safe.append(c.lower())
    return safe

def deduplicate_columns(cols, max_length=63):
    # PostgreSQL max identifier length is 63
    counts = {}
    unique_cols = []
    for col in cols:
        base = col[:max_length]
        new_col = base
        i = 1
        while new_col in counts:
            i += 1
            # Reserve space for suffix
            suffix = f"_{i}"
            trunc_length = max_length - len(suffix)
            new_col = f"{base[:trunc_length]}{suffix}"
        counts[new_col] = True
        unique_cols.append(new_col)
    return unique_cols

def main():
    # Updated to point to the correct data directory
    input_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/input/daily'))
    ddl_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../schema/ddl'))
    os.makedirs(ddl_dir, exist_ok=True)
    files = find_all_files(input_dir)
    seen_structures = {}
    for file in files:
        try:
            df = pd.read_csv(file, nrows=5)
            if all(str(c).isdigit() or not str(c).strip() for c in df.columns):
                df.columns = [f"col_{i+1}" for i in range(len(df.columns))]
            normalized_cols = normalize_columns(df.columns)
            deduped_cols = deduplicate_columns(normalized_cols)
            if len(set(deduped_cols)) != len(deduped_cols):
                print(f"[ERROR] Duplicate columns remain after deduplication for {file}:\n{deduped_cols}")
                continue
            if 'reg1_ind260625' in file.lower():
                print(f"[DEBUG] Deduplicated columns for {file}:\n{deduped_cols}")
            df.columns = deduped_cols
            schema = {col: infer_schema(df)[col] for col in deduped_cols}
            struct_key = tuple(sorted(schema.items()))
            if struct_key not in seen_structures:
                table_name = clean_table_name(file)
                ddl = generate_ddl(table_name, schema)
                with open(os.path.join(ddl_dir, f'{table_name}.sql'), 'w') as f:
                    f.write(ddl)
                seen_structures[struct_key] = table_name
        except Exception as e:
            print(f"Failed to process {file}: {e}")

if __name__ == '__main__':
    main()
