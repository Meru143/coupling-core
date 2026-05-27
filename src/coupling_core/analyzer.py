from __future__ import annotations

import logging
from pathlib import Path

from .git_parser import get_commits, get_repo_name, open_repo
from .matrix import NormalizedMatrix, build_normalized_matrix
from .models import Config, CouplingPair, RepoAnalysis

log = logging.getLogger(__name__)


def classify_risk(score: float, config: Config) -> str:
    if score < config.low_threshold:
        return "low"
    if score < config.high_threshold:
        return "medium"
    return "high"


def analyze_repo(repo_path: Path, config: Config) -> RepoAnalysis:
    """Run the full coupling analysis over a local repository.

    Opens the repo, walks the last ``config.lookback_days`` of history,
    builds the normalized co-change matrix, and returns a sorted list of
    CouplingPair (highest score first) wrapped in a RepoAnalysis.

    Raises CouplingCoreError / ShallowCloneError from open_repo when the
    path is invalid or the repo is a shallow clone. These propagate to
    the caller so they can be presented in the calling tool's UI.
    """
    repo = open_repo(repo_path)
    commits = get_commits(repo, config.lookback_days, config.exclude)
    matrix, _file_counts = build_normalized_matrix(commits, config)

    pairs = [
        CouplingPair(
            file_a=a,
            file_b=b,
            score=score,
            co_changes=co_count,
            total_commits=total,
            risk=classify_risk(score, config),
        )
        for (a, b), (score, co_count, total) in matrix.items()
    ]
    pairs.sort(key=lambda p: p.score, reverse=True)

    return RepoAnalysis(
        pairs=pairs,
        total_commits_analyzed=len(commits),
        lookback_days=config.lookback_days,
        repo_name=get_repo_name(repo),
    )


def analyze_pr_files(
    pr_files: list[str],
    matrix: NormalizedMatrix,
    file_counts: dict[str, int],
    config: Config,
    max_pairs: int = 10,
) -> list[CouplingPair]:
    """Project the global co-change matrix down to pairs touching ``pr_files``.

    Returns generic CouplingPair (file_a/file_b) — callers like
    couplingguard remap to their own PR-specific field names afterward.
    Pairs are sorted by score descending and truncated to ``max_pairs``.
    """
    del file_counts  # captured in matrix tuples; kept in signature per PRD section 6.4
    pr_set = set(pr_files)
    if not pr_set:
        return []

    pairs = [
        CouplingPair(
            file_a=a,
            file_b=b,
            score=score,
            co_changes=co_count,
            total_commits=total,
            risk=classify_risk(score, config),
        )
        for (a, b), (score, co_count, total) in matrix.items()
        if a in pr_set or b in pr_set
    ]
    pairs.sort(key=lambda p: p.score, reverse=True)
    return pairs[:max_pairs]
