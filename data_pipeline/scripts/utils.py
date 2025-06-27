import os
import re
import logging
import pandas as pd
from typing import List, Dict, Tuple

def setup_logging(log_file: str = None):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.FileHandler(log_file) if log_file else logging.StreamHandler()]
    )

def find_all_files(root_dir: str, exts: Tuple[str] = ('.csv', '.txt')) -> List[str]:
    files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.lower().endswith(exts):
                files.append(os.path.join(dirpath, f))
    return files

def clean_column_name(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r'[^a-z0-9_]', '_', col)
    col = re.sub(r'_+', '_', col)
    col = col.strip('_')
    return col

def normalize_columns(cols: List[str]) -> List[str]:
    return [clean_column_name(c) for c in cols]

def infer_dtype(series: pd.Series) -> str:
    try:
        pd.to_numeric(series.dropna())
        return 'NUMERIC'
    except Exception:
        pass
    try:
        pd.to_datetime(series.dropna())
        return 'DATE'
    except Exception:
        pass
    if series.dropna().astype(str).str.lower().isin(['true', 'false', 'yes', 'no', '0', '1']).all():
        return 'BOOLEAN'
    return 'TEXT'

def infer_schema(df: pd.DataFrame) -> Dict[str, str]:
    schema = {}
    for col in df.columns:
        schema[col] = infer_dtype(df[col])
    return schema
