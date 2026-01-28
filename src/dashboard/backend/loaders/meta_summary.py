from dashboard.backend.utils.filesystem import read_markdown_safe, META_DIR
from typing import Dict, Any

def load_meta_summary() -> Dict[str, Any]:
    content = read_markdown_safe(META_DIR / "evolution_comparative_summary.md")
    
    # We could parse sections here if needed
    # For now returning raw content
    return {
        "content": content,
        "key_findings": [], 
        "what_changed": [],
        "what_did_not_change": []
    }
