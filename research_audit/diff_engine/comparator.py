import uuid
from datetime import datetime
from typing import Optional
from research_reports.core.models import ResearchReport
from research_audit.versioning.models import ReportDiff

class ReportComparator:
    """
    Logic to compare two reports and generate a Diff.
    """
    
    def compare(self, old: Optional[ResearchReport], new: ResearchReport) -> ReportDiff:
        if old is None:
            return ReportDiff(
                diff_id=str(uuid.uuid4()),
                old_version_id=None,
                new_version_id=new.report_id,
                generated_at=datetime.utcnow(),
                added_narrative_ids=new.included_narrative_ids,
                removed_narrative_ids=[],
                confidence_deltas={},
                avg_confidence_delta=0.0,
                classification="NEW_REPORT"
            )
            
        # 1. Narrative Sets
        old_ids = set(old.included_narrative_ids)
        new_ids = set(new.included_narrative_ids)
        
        added = list(new_ids - old_ids)
        removed = list(old_ids - new_ids)
        
        # 2. Confidence Deltas (for intersection)
        common = old_ids.intersection(new_ids)
        deltas = {}
        
        # Helper to map id to conf
        def get_conf_map(rep):
            return {n['id']: n['confidence'] for n in rep.narrative_summaries}
            
        old_map = get_conf_map(old)
        new_map = get_conf_map(new)
        
        for nid in common:
            d = new_map.get(nid, 0) - old_map.get(nid, 0)
            if abs(d) > 0.1: # Floating point tolerance
                deltas[nid] = d
                
        # 3. Avg Conf Delta
        old_avg = old.signal_stats.get('avg_conf', 0)
        new_avg = new.signal_stats.get('avg_conf', 0)
        
        # 4. Classification
        if not added and not removed and not deltas:
            cls = "NO_CHANGE"
        elif len(added) > 0 or len(removed) > 0 or abs(new_avg - old_avg) > 10:
            cls = "MAJOR_REVISION"
        else:
            cls = "MINOR_UPDATE"
            
        return ReportDiff(
            diff_id=str(uuid.uuid4()),
            old_version_id=old.report_id,
            new_version_id=new.report_id,
            generated_at=datetime.utcnow(),
            added_narrative_ids=added,
            removed_narrative_ids=removed,
            confidence_deltas=deltas,
            avg_confidence_delta=new_avg - old_avg,
            classification=cls
        )
