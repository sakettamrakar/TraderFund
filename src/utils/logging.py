import logging
import sys
import json
import datetime
import os
import getpass
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """
    Formatter to output JSON structured logs.
    Includes standard fields: timestamp, level, name, message.
    Includes context fields: user, pid.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "user": getattr(record, "user", getpass.getuser()),
            "pid": os.getpid(),
            "file": record.filename,
            "line": record.lineno
        }
        
        # Merge extra fields if present
        if hasattr(record, "props"):
            log_record.update(record.props)
            
        return json.dumps(log_record)

def setup_logging(name: str, log_dir: str = "logs", console_level: int = logging.INFO) -> logging.Logger:
    """
    Setup a logger with:
    1. Console Handler (Standard Text)
    2. File Handler (JSON Structured)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG) # Capture all, handlers filter
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Ensure log dir exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 1. Console Handler (Human Readable)
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(console_level)
    c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    
    # 2. File Handler (Machine Readable JSON)
    # Rotating file handler could be better, but simple FileHandler for now
    # Filename based on logger name (sanitized)
    safe_name = name.replace(" ", "_").lower()
    log_file = Path(log_dir) / f"{safe_name}.json"
    
    f_handler = logging.FileHandler(log_file)
    f_handler.setLevel(logging.DEBUG)
    f_handler.setFormatter(JSONFormatter())
    logger.addHandler(f_handler)
    
    return logger
