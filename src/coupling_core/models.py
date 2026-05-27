from dataclasses import dataclass, field


@dataclass
class Config:
    lookback_days: int = 90
    min_occurrences: int = 3
    low_threshold: float = 0.3
    high_threshold: float = 0.7
    exclude: list[str] = field(default_factory=list)


@dataclass
class CouplingPair:
    file_a: str
    file_b: str
    score: float
    co_changes: int
    total_commits: int
    risk: str


@dataclass
class RepoAnalysis:
    pairs: list[CouplingPair]
    total_commits_analyzed: int
    lookback_days: int
    repo_name: str


class CouplingCoreError(Exception):
    """Base exception for all coupling-core runtime errors."""


class ShallowCloneError(CouplingCoreError):
    """Raised when the repo is a shallow clone and full history is needed."""
