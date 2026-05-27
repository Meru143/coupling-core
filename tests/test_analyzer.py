from __future__ import annotations

from coupling_core.analyzer import analyze_pr_files, analyze_repo, classify_risk
from coupling_core.models import Config, RepoAnalysis
from tests.conftest import RepoBuilder


def test_classify_risk_low() -> None:
    assert classify_risk(0.29, Config()) == "low"


def test_classify_risk_medium_at_low_boundary() -> None:
    # score == low_threshold → not low (uses <), so medium
    assert classify_risk(0.30, Config()) == "medium"


def test_classify_risk_medium_below_high() -> None:
    assert classify_risk(0.69, Config()) == "medium"


def test_classify_risk_high_at_boundary() -> None:
    # score == high_threshold → not medium (uses <), so high
    assert classify_risk(0.70, Config()) == "high"


def test_classify_risk_high_above() -> None:
    assert classify_risk(0.95, Config()) == "high"


def test_analyze_repo_returns_repo_analysis(fake_repo: RepoBuilder) -> None:
    for _ in range(3):
        fake_repo.commit(["a.py", "b.py"])
    fake_repo.repo.create_remote("origin", "https://github.com/owner/repo.git")

    result = analyze_repo(fake_repo.path, Config(min_occurrences=3))
    assert isinstance(result, RepoAnalysis)
    assert result.repo_name == "owner/repo"
    assert result.lookback_days == 90
    assert result.total_commits_analyzed == 3


def test_analyze_repo_pairs_sorted_desc(fake_repo: RepoBuilder) -> None:
    # Strong pair: a.py + b.py co-changed 5x; weaker pair: a.py + c.py co-changed 3x
    for _ in range(5):
        fake_repo.commit(["a.py", "b.py"])
    for _ in range(3):
        fake_repo.commit(["a.py", "c.py"])

    result = analyze_repo(fake_repo.path, Config(min_occurrences=3))
    scores = [p.score for p in result.pairs]
    assert scores == sorted(scores, reverse=True)
    # The a.py/b.py pair should rank highest (count 5 vs 3)
    assert result.pairs[0].file_a in {"a.py", "b.py"}
    assert result.pairs[0].file_b in {"a.py", "b.py"}


def test_analyze_repo_no_remote_falls_back_to_dirname(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    result = analyze_repo(fake_repo.path, Config(min_occurrences=1))
    assert result.repo_name == fake_repo.path.name


def test_analyze_pr_files_filters_to_pr_only() -> None:
    matrix = {
        ("a.py", "b.py"): (0.8, 8, 10),
        ("c.py", "d.py"): (0.5, 5, 10),
        ("a.py", "e.py"): (0.4, 4, 10),
    }
    pairs = analyze_pr_files(["a.py"], matrix, {}, Config())
    files_seen = {(p.file_a, p.file_b) for p in pairs}
    # Only pairs touching a.py survive
    assert files_seen == {("a.py", "b.py"), ("a.py", "e.py")}


def test_analyze_pr_files_sorted_and_truncated() -> None:
    matrix = {
        ("pr.py", "x.py"): (0.9, 9, 10),
        ("pr.py", "y.py"): (0.5, 5, 10),
        ("pr.py", "z.py"): (0.2, 2, 10),
    }
    pairs = analyze_pr_files(["pr.py"], matrix, {}, Config(), max_pairs=2)
    assert len(pairs) == 2
    assert pairs[0].score == 0.9
    assert pairs[1].score == 0.5


def test_analyze_pr_files_empty_pr_list() -> None:
    matrix = {("a.py", "b.py"): (0.8, 8, 10)}
    assert analyze_pr_files([], matrix, {}, Config()) == []


def test_analyze_pr_files_classifies_risk() -> None:
    matrix = {
        ("pr.py", "high.py"): (0.85, 8, 10),
        ("pr.py", "low.py"): (0.1, 1, 10),
    }
    pairs = analyze_pr_files(["pr.py"], matrix, {}, Config())
    by_other = {p.file_b: p for p in pairs}
    assert by_other["high.py"].risk == "high"
    assert by_other["low.py"].risk == "low"
