from __future__ import annotations

from coupling_core.matrix import (
    build_co_change_matrix,
    build_normalized_matrix,
    filter_by_min_occurrences,
    normalize_pair,
)
from coupling_core.models import Config


def test_build_co_change_matrix_single_commit() -> None:
    co, counts = build_co_change_matrix([["a.py", "b.py"]])
    assert co["a.py"]["b.py"] == 1
    assert co["b.py"]["a.py"] == 1
    assert counts == {"a.py": 1, "b.py": 1}


def test_build_co_change_matrix_five_commits() -> None:
    commits = [["a.py", "b.py"]] * 5
    co, counts = build_co_change_matrix(commits)
    assert co["a.py"]["b.py"] == 5
    assert co["b.py"]["a.py"] == 5
    assert counts == {"a.py": 5, "b.py": 5}


def test_build_co_change_matrix_three_files() -> None:
    commits = [["a.py", "b.py", "c.py"]]
    co, _counts = build_co_change_matrix(commits)
    # All three pairs counted once
    assert co["a.py"]["b.py"] == 1
    assert co["a.py"]["c.py"] == 1
    assert co["b.py"]["c.py"] == 1


def test_build_co_change_matrix_empty() -> None:
    co, counts = build_co_change_matrix([])
    assert dict(co) == {}
    assert counts == {}


def test_filter_by_min_occurrences_drops_below() -> None:
    co_change = {
        "a.py": {"b.py": 5, "c.py": 2},
        "b.py": {"a.py": 5},
        "c.py": {"a.py": 2},
    }
    filtered = filter_by_min_occurrences(co_change, min_occurrences=3)
    assert filtered == {"a.py": {"b.py": 5}, "b.py": {"a.py": 5}}
    assert "c.py" not in filtered


def test_filter_returns_plain_dict() -> None:
    co_change = {"a.py": {"b.py": 5}, "b.py": {"a.py": 5}}
    filtered = filter_by_min_occurrences(co_change, min_occurrences=3)
    # Returned dict has no defaultdict semantics
    assert type(filtered) is dict
    assert type(filtered["a.py"]) is dict


def test_normalize_pair_half() -> None:
    assert normalize_pair(10, 10, 20) == 0.5


def test_normalize_pair_full() -> None:
    assert normalize_pair(5, 5, 5) == 1.0


def test_normalize_pair_zero_denominator() -> None:
    # Defensive: no division by zero
    assert normalize_pair(0, 0, 0) == 0.0


def test_normalize_pair_rounding_to_4_decimals() -> None:
    # 1 / 3 = 0.3333... → rounded to 0.3333
    assert normalize_pair(1, 3, 3) == 0.3333


def test_build_normalized_matrix_canonical_keys() -> None:
    commits = [["a.py", "b.py"]] * 3
    matrix, counts = build_normalized_matrix(commits, Config(min_occurrences=3))
    assert matrix == {("a.py", "b.py"): (1.0, 3, 3)}
    assert ("b.py", "a.py") not in matrix  # canonical: alphabetical
    assert counts == {"a.py": 3, "b.py": 3}


def test_build_normalized_matrix_filters_below_min() -> None:
    commits = [["a.py", "b.py"]] * 2  # below default min_occurrences=3
    matrix, _ = build_normalized_matrix(commits, Config())
    assert matrix == {}


def test_build_normalized_matrix_empty() -> None:
    matrix, counts = build_normalized_matrix([], Config())
    assert matrix == {}
    assert counts == {}
