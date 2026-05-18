from .archive_adapter import scan as scan_archives
from .candidate_readiness_adapter import scan as scan_candidate_readiness
from .candidate_plans_adapter import scan as scan_candidate_plans
from .docs_adapter import scan as scan_docs
from .logs_adapter import scan as scan_logs
from .live_testing_status_adapter import scan as scan_live_testing_status
from .node_audit_adapter import scan as scan_node_audit
from .next_step_outcomes_adapter import scan as scan_next_step_outcomes
from .particle_reports_adapter import scan as scan_particle_reports
from .research_data_adapter import scan as scan_research_data
from .scripts_adapter import scan as scan_scripts
from .sensitive_adapter import scan as scan_sensitive
from .stats_adapter import scan as scan_stats
from .v28_successor_candidates_adapter import scan as scan_v28_successor_candidates

ALL_ADAPTERS = [
    scan_stats,
    scan_logs,
    scan_particle_reports,
    scan_candidate_plans,
    scan_v28_successor_candidates,
    scan_next_step_outcomes,
    scan_node_audit,
    scan_research_data,
    scan_docs,
    scan_scripts,
    scan_archives,
    scan_sensitive,
    scan_candidate_readiness,
    scan_live_testing_status,
]

__all__ = ["ALL_ADAPTERS"]
