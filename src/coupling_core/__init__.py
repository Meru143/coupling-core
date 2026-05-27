__version__ = "1.0.0"

from coupling_core.analyzer import analyze_pr_files, analyze_repo, classify_risk
from coupling_core.git_parser import apply_excludes, get_file_commit_counts, get_repo_name
from coupling_core.matrix import (
    CoChangeMatrix,
    NormalizedMatrix,
    NormalizedPair,
    build_normalized_matrix,
)
from coupling_core.models import (
    Config,
    CouplingCoreError,
    CouplingPair,
    RepoAnalysis,
    ShallowCloneError,
)

__all__ = [
    "__version__",
    "CoChangeMatrix",
    "Config",
    "CouplingCoreError",
    "CouplingPair",
    "NormalizedMatrix",
    "NormalizedPair",
    "RepoAnalysis",
    "ShallowCloneError",
    "analyze_pr_files",
    "analyze_repo",
    "apply_excludes",
    "build_normalized_matrix",
    "classify_risk",
    "get_file_commit_counts",
    "get_repo_name",
]
