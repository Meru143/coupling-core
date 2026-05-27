# 2026-05-27 — coupling-core PRD

## Section 1 — Project Overview

**Name:** coupling-core  
**Type:** Python Library (PyPI package)  
**Language:** Python 3.11+  
**License:** MIT  
**Repository:** `Meru143/coupling-core`  
**PyPI package name:** `coupling-core`  
**Description:** coupling-core is the shared algorithm library powering the coupling ecosystem. It provides git history parsing, co-change matrix construction, normalization, and PR/file analysis as a clean, importable Python API. Both `couplingguard` (GitHub Action) and `churnmap` (CLI) depend on it. It has no CLI, no output formatting, and no platform-specific code — pure algorithm, pure Python.

---

## Section 2 — Problem Statement

- **Algorithm duplication.** Without a shared library, couplingguard and churnmap would independently implement the same co-change matrix logic. Any bug fix or normalization improvement would need to be applied twice.
- **Version skew.** Independently maintained copies drift apart. A fix to the matrix builder in churnmap doesn't automatically reach couplingguard users.
- **Import coupling.** Making churnmap import from couplingguard couples a analytics tool to a GitHub Action package — wrong abstraction boundary.
- **Testability.** A shared library can have a focused, comprehensive test suite for the algorithm independent of any platform integration.

---

## Section 3 — Solution

1. Extract the git history parser, co-change matrix builder, normalizer, and PR analyzer from couplingguard into `coupling-core`.
2. Publish `coupling-core` independently to PyPI with semver versioning.
3. Both `couplingguard` and `churnmap` declare `coupling-core>=X.Y` as a dependency.
4. All algorithm bug fixes and improvements ship once to `coupling-core` and are immediately available to both consumers via version pin upgrades.

---

## Section 4 — Target Users

- **couplingguard** — imports `from coupling_core import build_normalized_matrix, apply_excludes`
- **churnmap** — imports the same API plus `RepoAnalysis` for whole-repo analysis
- **Third-party tools** — any developer building coupling-aware tooling can depend on it

---

## Section 5 — Tech Stack Table

| Component | Library | Version | Purpose |
|-----------|---------|---------|---------|
| Git history parsing | `GitPython` | `3.1.50` | Walk commit log, extract per-commit file lists |
| Path glob matching | `fnmatch` (stdlib) | — | Exclude pattern matching |
| Testing | `pytest` | `9.0.3` | Unit tests |
| Coverage | `pytest-cov` | `6.1.0` | Coverage reporting |
| Linting | `ruff` | `0.11.x` | Fast Python linter |
| Type checking | `mypy` | `1.15.x` | Static typing (`--strict`) |
| Release | `python-semantic-release` | `9.x` | Automated versioning from Conventional Commits |

**No runtime dependencies beyond GitPython.** coupling-core must be lightweight — every consumer pays the import cost.

---

## Section 6 — Public API (v1)

> **Extraction note.** `coupling_core.git_parser` and `coupling_core.matrix` are
> extracted verbatim from `Meru143/couplingguard` with three mechanical changes:
> (1) `CouplingGuardError` → `CouplingCoreError`, (2) `from .models import` paths
> updated, (3) log prefixes updated from `"couplingguard:"` to `"coupling-core:"`.
> `coupling_core.analyzer` extracts only `classify_risk()` from couplingguard's
> `pr_analyzer.py`; `analyze_repo()` is new (written for churnmap, doesn't exist
> in couplingguard). `get_repo_name()` is also new — couplingguard never needed it.

### 6.1 Data Models (`coupling_core.models`)

**Extracted from** `src/couplingguard/models.py` — subset only. couplingguard-specific
fields (`max_pairs`, `fail_threshold`, `dry_run`, `publish_dashboard`) are NOT
extracted. coupling-core's `Config` is a strict subset.

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    lookback_days: int = 90
    min_occurrences: int = 3
    low_threshold: float = 0.3
    high_threshold: float = 0.7
    exclude: list[str] = field(default_factory=list)

# NOTE: coupling-core uses file_a/file_b (generic pair).
# couplingguard keeps its own CouplingPair with file_in_pr/coupled_file
# (PR-specific). These are different types — do not conflate.
@dataclass
class CouplingPair:
    file_a: str
    file_b: str
    score: float          # normalized 0–1
    co_changes: int       # raw co-change count
    total_commits: int    # max(file_a_commits, file_b_commits)
    risk: str             # "low" | "medium" | "high"

@dataclass
class RepoAnalysis:
    pairs: list[CouplingPair]
    total_commits_analyzed: int
    lookback_days: int
    repo_name: str

# Rename from CouplingGuardError during extraction
class CouplingCoreError(Exception): pass
class ShallowCloneError(CouplingCoreError): pass
```

### 6.2 Git Parser (`coupling_core.git_parser`)

**Extracted verbatim** from `src/couplingguard/git_parser.py`. Real signatures confirmed
from source. Only rename: `CouplingGuardError` → `CouplingCoreError` in imports and raises.

```python
# Type aliases (copy from source)
BINARY_EXTENSIONS: frozenset[str]  # already defined in source

# Extracted as-is:
def open_repo(repo_path: Path) -> git.Repo
    # raises CouplingCoreError (was CouplingGuardError) on invalid repo
    # raises ShallowCloneError on shallow clone

def get_commits(
    repo: git.Repo,
    lookback_days: int,
    exclude_patterns: list[str] | None = None,
) -> list[list[str]]
    # no-merges, since=lookback_days, binary filtered, renames resolved, excludes applied

def get_file_commit_counts(commits: list[list[str]]) -> dict[str, int]

def apply_excludes(files: list[str], exclude_patterns: list[str]) -> list[str]

# NEW — does not exist in couplingguard; written fresh for churnmap:
def get_repo_name(repo: git.Repo) -> str
    # tries: repo.git.remote("get-url", "origin") → extract owner/repo from HTTPS or SSH URL
    # fallback: Path(repo.working_dir).name
```

Private helpers extracted unchanged (keep as private `_` prefixed):
`_decode_unicode_path`, `_normalize_rename`, `_is_binary`, `_normalize_files`

### 6.3 Matrix Builder (`coupling_core.matrix`)

**Extracted verbatim** from `src/couplingguard/matrix.py`. Real type aliases and
signatures confirmed from source. Only changes: update `from .models import Config`
to coupling-core's slimmer `Config`; update `from .git_parser import get_file_commit_counts`.

```python
# Type aliases (copy from source):
CoChangeMatrix = dict[str, dict[str, int]]
NormalizedPair = tuple[float, int, int]  # (score, co_count, max_total_commits)
NormalizedMatrix = dict[tuple[str, str], NormalizedPair]

# Extracted as-is:
def build_co_change_matrix(
    commits: list[list[str]]
) -> tuple[CoChangeMatrix, dict[str, int]]
    # symmetric matrix: co_change[a][b] == co_change[b][a]
    # also returns file_counts via get_file_commit_counts(commits)

def filter_by_min_occurrences(
    co_change: CoChangeMatrix,
    min_occurrences: int,
) -> CoChangeMatrix
    # returns plain dict (no defaultdict), drops pairs below threshold

def normalize_pair(co_count: int, count_a: int, count_b: int) -> float
    # score = round(co_count / max(count_a, count_b), 4)
    # returns 0.0 if max == 0

def build_normalized_matrix(
    commits: list[list[str]],
    config: Config,          # coupling-core Config (only min_occurrences used here)
) -> tuple[NormalizedMatrix, dict[str, int]]
    # canonical key: (a, b) where a < b (alphabetically)
    # returns (matrix, file_counts)
```

### 6.4 Analyzer (`coupling_core.analyzer`)

**Partially extracted.** `classify_risk()` is extracted from `src/couplingguard/pr_analyzer.py`
(line-for-line identical). `analyze_repo()` is NEW — it does not exist in couplingguard.
`analyze_pr_files()` wraps the extraction for couplingguard-style callers.

```python
# Extracted from couplingguard/pr_analyzer.py:
def classify_risk(score: float, config: Config) -> str
    # "low" if score < config.low_threshold
    # "medium" if score < config.high_threshold
    # "high" otherwise

# NEW — written fresh; primary entry point for churnmap:
def analyze_repo(repo_path: Path, config: Config) -> RepoAnalysis
    # 1. open_repo(repo_path)           → raises CouplingCoreError / ShallowCloneError
    # 2. get_commits(repo, ...)         → commits
    # 3. build_normalized_matrix(...)   → (matrix, file_counts)
    # 4. build CouplingPair list from matrix using file_a/file_b (not file_in_pr/coupled_file)
    # 5. classify_risk per pair
    # 6. sort by score desc
    # 7. get_repo_name(repo)
    # 8. return RepoAnalysis(pairs, total_commits_analyzed, lookback_days, repo_name)

# Convenience for couplingguard — wraps matrix lookup in generic pair form:
def analyze_pr_files(
    pr_files: list[str],
    matrix: NormalizedMatrix,
    file_counts: dict[str, int],
    config: Config,
    max_pairs: int = 10,
) -> list[CouplingPair]
    # returns CouplingPair(file_a, file_b, ...) — not file_in_pr/coupled_file
    # couplingguard maps these to its own CouplingPair after this call
```

### 6.5 Top-Level Convenience (`coupling_core.__init__`)

```python
from coupling_core import analyze_repo, analyze_pr_files, Config, RepoAnalysis
from coupling_core import build_normalized_matrix, get_file_commit_counts
from coupling_core import CouplingCoreError, ShallowCloneError
```

### 6.6 What couplingguard keeps (NOT extracted)

These stay in `Meru143/couplingguard` forever — do not put them in coupling-core:

| Module | Reason |
|--------|--------|
| `pr_analyzer.py` (except `classify_risk`) | Reads `GITHUB_EVENT_PATH`, does `git diff base...head` — GitHub-specific |
| `models.CouplingPair.file_in_pr/coupled_file` | PR-specific field names |
| `models.PRAnalysis` | PR-specific type |
| `models.Config.max_pairs/fail_threshold/dry_run/publish_dashboard` | Action-specific fields |
| `renderer.py` | GitHub markdown rendering |
| `github_poster.py` | GitHub API |
| `gitlab_poster.py` | GitLab API |
| `dashboard.py` | Chart.js dashboard |
| `delta.py` | Comment delta extraction |
| `codeowners_loader.py` | CODEOWNERS parsing |
| `config.py` | `INPUT_*` env var parsing |

---

## Section 7 — Package Structure

```
coupling-core/
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── src/
│   └── coupling_core/
│       ├── __init__.py        # re-exports: analyze_repo, analyze_pr_files, Config
│       ├── models.py          # Config, CouplingPair, RepoAnalysis, exceptions
│       ├── git_parser.py      # GitPython commit walk, exclude, rename, binary filter
│       ├── matrix.py          # co-change matrix, normalization, filtering
│       └── analyzer.py        # analyze_repo, analyze_pr_files, classify_risk
└── tests/
    ├── conftest.py            # fake_repo fixture using git.Repo.init(tmp_path)
    ├── test_git_parser.py
    ├── test_matrix.py
    └── test_analyzer.py
```

---

## Section 8 — Versioning Policy

- Semver: `MAJOR.MINOR.PATCH`
- Breaking changes to the public API → MAJOR bump
- New public functions or fields → MINOR bump
- Bug fixes only → PATCH bump
- Both couplingguard and churnmap pin `coupling-core>=1.0,<2.0` to avoid surprise breakage

---

## Section 9 — Edge Cases

Same as couplingguard PRD Section 11 (merge commits, renames, binary files, unicode filenames, empty history, shallow clones). coupling-core is the single place these are handled — consumers get them for free.

---

## Section 10 — Distribution

```bash
# Build
python -m build

# Publish (Trusted Publishing via GitHub Actions)
python -m twine upload dist/*

# Install (consumers)
pip install coupling-core>=1.0
```

---

## Section 11 — Success Metrics

- [ ] `from coupling_core import analyze_repo, Config` works in both couplingguard and churnmap with zero code duplication
- [ ] Unit test coverage ≥ 85%
- [ ] `mypy src/ --strict` passes
- [ ] `ruff check src/` passes
- [ ] `analyze_repo()` completes in < 10s for a repo with 90 days of history and < 10k commits
- [ ] No runtime deps beyond `GitPython`
