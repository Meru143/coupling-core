# coupling-core

Shared Python library providing git co-change matrix analysis, normalization, and coupling scoring. It's the algorithm engine powering both [couplingguard](https://github.com/Meru143/couplingguard) (GitHub Action) and churnmap (CLI), and can be used directly by any tool that needs to know which files in a repo change together.

- Pure Python 3.11+, MIT licensed.
- One runtime dependency: GitPython.
- Typed (`py.typed`, ships PEP 561 markers; `mypy --strict` clean).

## Install

```bash
pip install coupling-core
```

## Quick example

```python
from pathlib import Path
from coupling_core import analyze_repo, Config

result = analyze_repo(Path("."), Config())

print(f"{result.repo_name} — {result.total_commits_analyzed} commits in last {result.lookback_days} days")
for pair in result.pairs[:5]:
    print(f"  [{pair.risk:>6}] {pair.score:.2f}  {pair.file_a} <-> {pair.file_b}")
```

## Public API

### `analyze_repo(repo_path, config) -> RepoAnalysis`

Open a local git repository and return every co-changed file pair sorted by coupling score (highest first).

```python
from pathlib import Path
from coupling_core import analyze_repo, Config, CouplingCoreError, ShallowCloneError

try:
    result = analyze_repo(
        Path("/path/to/repo"),
        Config(lookback_days=90, min_occurrences=3, exclude=["docs/**", "*.lock"]),
    )
except ShallowCloneError:
    print("Shallow clone — fetch full history first.")
except CouplingCoreError as exc:
    print(f"Could not analyze repo: {exc}")
else:
    print(f"{len(result.pairs)} coupled pairs over {result.total_commits_analyzed} commits")
```

`RepoAnalysis` fields:

| Field | Type | Description |
|-------|------|-------------|
| `pairs` | `list[CouplingPair]` | Sorted by `score` descending |
| `total_commits_analyzed` | `int` | Non-merge commits in the lookback window |
| `lookback_days` | `int` | Window size used (echoed from `Config`) |
| `repo_name` | `str` | `owner/repo` from origin, or working-dir name as fallback |

### `analyze_pr_files(pr_files, matrix, file_counts, config, max_pairs=10) -> list[CouplingPair]`

Project a pre-built normalized matrix down to pairs involving the given files. This is the entry point couplingguard uses to map a PR's changed file list against the repo-wide coupling matrix.

```python
from coupling_core import build_normalized_matrix, analyze_pr_files, Config

# Build the matrix once, then query it cheaply per PR:
matrix, counts = build_normalized_matrix(commits, Config())

pairs = analyze_pr_files(
    pr_files=["src/auth.py"],
    matrix=matrix,
    file_counts=counts,
    config=Config(),
    max_pairs=10,
)
for p in pairs:
    print(f"{p.score:.2f}  {p.file_a} <-> {p.file_b}  [{p.risk}]")
```

Returns generic `CouplingPair` (with `file_a` / `file_b` fields). Callers that need PR-specific naming (e.g. couplingguard's `file_in_pr` / `coupled_file`) remap them after this call.

### `CouplingPair`

| Field | Type | Description |
|-------|------|-------------|
| `file_a`, `file_b` | `str` | The two files in the pair (alphabetical) |
| `score` | `float` | Normalized 0–1 coupling, rounded to 4 decimals |
| `co_changes` | `int` | Raw count of commits where both files appeared |
| `total_commits` | `int` | `max(commits_for_a, commits_for_b)` |
| `risk` | `str` | `"low"` / `"medium"` / `"high"` per `Config` thresholds |

### `Config`

| Field | Default | Description |
|-------|---------|-------------|
| `lookback_days` | `90` | Commit window measured from today |
| `min_occurrences` | `3` | Drop pairs that co-changed fewer than this many times |
| `low_threshold` | `0.3` | `score < low` → `"low"` risk |
| `high_threshold` | `0.7` | `score >= high` → `"high"` risk (else `"medium"`) |
| `exclude` | `[]` | Glob patterns (`fnmatch` semantics) of paths to ignore |

### Exceptions

| Exception | Raised by | Meaning |
|-----------|-----------|---------|
| `CouplingCoreError` | `open_repo`, `analyze_repo` | Base class. Invalid path, not a git repo, etc. |
| `ShallowCloneError` | `open_repo`, `analyze_repo` | Repository is a shallow clone — full history is required. |

`ShallowCloneError` is a subclass of `CouplingCoreError`, so a single `except CouplingCoreError` handles both.

### Lower-level helpers

For tools that need direct access to the pipeline stages:

- `build_normalized_matrix(commits, config) -> (NormalizedMatrix, dict[str, int])`
- `get_file_commit_counts(commits) -> dict[str, int]`
- `apply_excludes(files, patterns) -> list[str]`
- `get_repo_name(repo) -> str`
- `classify_risk(score, config) -> str`

Type aliases (re-exported): `CoChangeMatrix`, `NormalizedPair`, `NormalizedMatrix`.

## Used by

- **[couplingguard](https://github.com/Meru143/couplingguard)** — GitHub Action that comments coupling risk on pull requests.
- **churnmap** — CLI that visualises whole-repo coupling.

## Development

```bash
git clone https://github.com/Meru143/coupling-core.git
cd coupling-core
make dev          # pip install -e ".[dev]"
make test         # pytest with coverage
make lint         # ruff
make type-check   # mypy --strict
make build        # python -m build
```

The repo follows [Conventional Commits](https://www.conventionalcommits.org/) and ships with [python-semantic-release](https://github.com/python-semantic-release/python-semantic-release) for automated PyPI releases on push to `main`.

## License

MIT — see [LICENSE](LICENSE).
