# 2026-05-27 — coupling-core TODO

<!--
## Phase 0 — Active skills (verified 2026-05-28)

Skills actually installed (from skills-lock.json):
  brainstorming, dispatching-parallel-agents, executing-plans,
  finishing-a-development-branch, git-commit, git-flow-branch-creator,
  github-actions-efficiency, receiving-code-review, requesting-code-review,
  subagent-driven-development, systematic-debugging, test-driven-development,
  using-git-worktrees, using-superpowers, verification-before-completion,
  writing-plans, writing-skills

Prompt-claimed skills NOT installed (substitutions):
  architecture-patterns      → none; apply PRD Section 6/7 as direct contract
  error-handling-patterns    → none; apply PRD Section 9 (edge cases) + Section 6.1 exception hierarchy
  devops-engineer            → github-actions-efficiency (covers CI + release workflow)

Per-phase skill mapping (using installed skills):
  Phase 1 — github-actions-efficiency, git-commit, executing-plans
  Phase 2 — (PRD Section 6.1 is the contract; no direct skill)
  Phase 3 — systematic-debugging, verification-before-completion
  Phase 4 — systematic-debugging, verification-before-completion
  Phase 5 — systematic-debugging, verification-before-completion
  Phase 6 — test-driven-development, systematic-debugging
  Phase 7 — git-commit (final commit), verification-before-completion
-->

---

## Phase 1: Project Setup

### 1.1 Repository Initialization
- [ ] `git init coupling-core` and push to `Meru143/coupling-core` on GitHub
- [ ] Create `README.md` with name, one-liner, install placeholder
- [ ] Create `LICENSE` (MIT)
- [ ] Create `.gitignore`: `__pycache__/`, `*.pyc`, `.coverage`, `dist/`, `.mypy_cache/`, `.ruff_cache/`, `*.egg-info/`
- [ ] Create `CHANGELOG.md` with `## [Unreleased]` section

### 1.2 Directory Structure
- [ ] Create `src/coupling_core/` package directory
- [ ] Create `src/coupling_core/__init__.py` with `__version__ = "1.0.0"`
- [ ] Create `src/coupling_core/models.py` (stub)
- [ ] Create `src/coupling_core/git_parser.py` (stub)
- [ ] Create `src/coupling_core/matrix.py` (stub)
- [ ] Create `src/coupling_core/analyzer.py` (stub)
- [ ] Create `tests/` with `__init__.py`
- [ ] Create `tests/conftest.py` (stub)
- [ ] Create `tests/test_git_parser.py` (stub)
- [ ] Create `tests/test_matrix.py` (stub)
- [ ] Create `tests/test_analyzer.py` (stub)
- [ ] Create `.github/workflows/` directory

### 1.3 Package Metadata
- [ ] Create `pyproject.toml` with `[project]`: `name = "coupling-core"`, `version = "1.0.0"`, `requires-python = ">=3.11"`
- [ ] Add `[project.dependencies]`: `GitPython>=3.1.50`
- [ ] Add `[project.optional-dependencies]` `dev`: `pytest>=9.0.3`, `pytest-cov>=6.1.0`, `ruff>=0.11`, `mypy>=1.15`
- [ ] Add `[tool.ruff]`: `select = ["E","F","I","UP"]`, `line-length = 100`
- [ ] Add `[tool.mypy]`: `strict = true`, `python_version = "3.11"`
- [ ] Add `[tool.pytest.ini_options]`: `testpaths = ["tests"]`, `addopts = "-v"`
- [ ] Add `[build-system]`: `requires = ["hatchling"]`, `build-backend = "hatchling.build"`

### 1.4 CI Workflow
- [ ] Create `.github/workflows/ci.yml`: trigger `push` to `main`, `pull_request` to `main`
- [ ] Add job `lint`: `ruff check src/ tests/`
- [ ] Add job `type-check`: `mypy src/ --strict`
- [ ] Add job `test`: matrix `python-version: ["3.11","3.12","3.13"]`, os: `ubuntu-latest`
- [ ] Add step: `pytest tests/ --cov=src/coupling_core --cov-report=xml`

### 1.5 Release Workflow
- [ ] Create `.github/workflows/release.yml`: trigger `push` to `main`
- [ ] Add job: `python-semantic-release publish`
- [ ] Configure Trusted Publishing for PyPI in `[tool.semantic_release]` block

### 1.6 Makefile
- [ ] Add target `make dev`: `pip install -e ".[dev]"`
- [ ] Add target `make lint`: `ruff check src/ tests/`
- [ ] Add target `make type-check`: `mypy src/ --strict`
- [ ] Add target `make test`: `pytest tests/ -v --cov=src/coupling_core --cov-report=term-missing`
- [ ] Add target `make build`: `python -m build`

---

## Phase 2: Data Models

### 2.1 Config Dataclass
- [ ] Define `@dataclass class Config` with `lookback_days: int = 90`
- [ ] Add `min_occurrences: int = 3`
- [ ] Add `low_threshold: float = 0.3`
- [ ] Add `high_threshold: float = 0.7`
- [ ] Add `exclude: list[str] = field(default_factory=list)`

### 2.2 CouplingPair Dataclass
- [ ] Define `@dataclass class CouplingPair` with `file_a: str`
- [ ] Add `file_b: str`
- [ ] Add `score: float`
- [ ] Add `co_changes: int`
- [ ] Add `total_commits: int`
- [ ] Add `risk: str`

### 2.3 RepoAnalysis Dataclass
- [ ] Define `@dataclass class RepoAnalysis` with `pairs: list[CouplingPair]`
- [ ] Add `total_commits_analyzed: int`
- [ ] Add `lookback_days: int`
- [ ] Add `repo_name: str`

### 2.4 Exceptions
- [ ] Define `class CouplingCoreError(Exception): pass`
- [ ] Define `class ShallowCloneError(CouplingCoreError): pass`

---

## Phase 3: Git Parser (EXTRACT from couplingguard)

> **Source file:** `Meru143/couplingguard/src/couplingguard/git_parser.py`
> Copy the file, then apply the three mechanical changes below.
> Do NOT rewrite logic — the real code is battle-tested across 177 tests.

### 3.1 Copy Source File
- [ ] Copy `src/couplingguard/git_parser.py` to `src/coupling_core/git_parser.py`
- [ ] Verify copy is byte-for-byte identical before making any edits

### 3.2 Mechanical Rename — Imports
- [ ] Replace `from .models import CouplingGuardError, ShallowCloneError` with `from .models import CouplingCoreError, ShallowCloneError`

### 3.3 Mechanical Rename — Raises
- [ ] Replace every `raise CouplingGuardError(` with `raise CouplingCoreError(`
- [ ] There are exactly 2 raises in `open_repo()` — verify both are updated

### 3.4 Mechanical Rename — Log Prefix
- [ ] Replace `"couplingguard: Error —` with `"coupling-core: Error —` in all log/raise strings
- [ ] Replace `log = logging.getLogger(__name__)` — keep as-is (`__name__` resolves correctly in new package)

### 3.5 Add `get_repo_name()` — NEW FUNCTION (not in couplingguard)
- [ ] Define `def get_repo_name(repo: git.Repo) -> str` at the bottom of the file
- [ ] Try `url = repo.git.remote("get-url", "origin")` — if no remote raises `git.exc.GitCommandError`, fall through to fallback
- [ ] For HTTPS URL (`https://github.com/owner/repo.git`): extract `owner/repo` by splitting on `github.com/` (or any host), strip `.git` suffix
- [ ] For SSH URL (`git@github.com:owner/repo.git`): extract `owner/repo` by splitting on `:`, strip `.git` suffix
- [ ] Fallback (no remote or parse fails): `return Path(str(repo.working_dir)).name`

### 3.6 Verify Extraction
- [ ] Run `python -c "from coupling_core.git_parser import open_repo, get_commits, get_file_commit_counts, apply_excludes, get_repo_name; print('OK')`
- [ ] Run `make lint` — zero ruff errors

---

## Phase 4: Co-Change Matrix Builder (EXTRACT from couplingguard)

> **Source file:** `Meru143/couplingguard/src/couplingguard/matrix.py`
> Copy the file, then apply the two mechanical changes below.
> All type aliases, all logic, all comments copy verbatim.

### 4.1 Copy Source File
- [ ] Copy `src/couplingguard/matrix.py` to `src/coupling_core/matrix.py`
- [ ] Verify copy is byte-for-byte identical before making any edits

### 4.2 Mechanical Change — Config Import
- [ ] Replace `from .models import Config` with `from .models import Config`
- [ ] This resolves correctly already since coupling-core has its own `models.py` — just verify it imports coupling-core's `Config`, not couplingguard's

### 4.3 Mechanical Change — git_parser Import
- [ ] The line `from .git_parser import get_file_commit_counts` resolves correctly in the new package — verify it imports from `coupling_core.git_parser`, not couplingguard's

### 4.4 Verify Type Aliases Present
- [ ] Confirm `CoChangeMatrix`, `NormalizedPair`, `NormalizedMatrix` type aliases are present in the copied file
- [ ] Add to `__init__.py` re-exports if needed: `from coupling_core.matrix import NormalizedMatrix, CoChangeMatrix`

### 4.5 Verify Extraction
- [ ] Run `python -c "from coupling_core.matrix import build_normalized_matrix, normalize_pair, build_co_change_matrix, filter_by_min_occurrences; print('OK')"`
- [ ] Run `make lint` — zero ruff errors

---

## Phase 5: Analyzer (PARTIAL EXTRACT + NEW)

> **Extracted:** `classify_risk()` from `Meru143/couplingguard/src/couplingguard/pr_analyzer.py`
> **New:** `analyze_repo()` and `analyze_pr_files()` — do not exist in couplingguard

### 5.1 Extract `classify_risk()`
- [ ] Create `src/coupling_core/analyzer.py`
- [ ] Copy `classify_risk()` function verbatim from `couplingguard/pr_analyzer.py` — it's 4 lines, identical logic
- [ ] Update import: `from .models import Config` (coupling-core's Config, not couplingguard's)
- [ ] Verify: `classify_risk(0.29, Config())` → `"low"`, `classify_risk(0.70, Config())` → `"high"`

### 5.2 Write `analyze_repo()` — NEW
- [ ] Define `def analyze_repo(repo_path: Path, config: Config) -> RepoAnalysis`
- [ ] Import: `from .git_parser import open_repo, get_commits, get_repo_name`
- [ ] Import: `from .matrix import build_normalized_matrix`
- [ ] Import: `from .models import CouplingPair, RepoAnalysis`
- [ ] Step 1: `repo = open_repo(repo_path)` — let `CouplingCoreError`/`ShallowCloneError` propagate to caller
- [ ] Step 2: `commits = get_commits(repo, config.lookback_days, config.exclude)`
- [ ] Step 3: `matrix, file_counts = build_normalized_matrix(commits, config)`
- [ ] Step 4: build `CouplingPair` list — iterate `matrix.items()`: for each `(a, b), (score, co_count, total)` → `CouplingPair(file_a=a, file_b=b, score=score, co_changes=co_count, total_commits=total, risk=classify_risk(score, config))`
- [ ] Step 5: sort pairs by `score` descending
- [ ] Step 6: `repo_name = get_repo_name(repo)`
- [ ] Step 7: return `RepoAnalysis(pairs=pairs, total_commits_analyzed=len(commits), lookback_days=config.lookback_days, repo_name=repo_name)`

### 5.3 Write `analyze_pr_files()` — NEW
- [ ] Define `def analyze_pr_files(pr_files: list[str], matrix: NormalizedMatrix, file_counts: dict[str, int], config: Config, max_pairs: int = 10) -> list[CouplingPair]`
- [ ] Import `NormalizedMatrix` from `.matrix`
- [ ] Build `pr_set = set(pr_files)`
- [ ] Iterate `matrix.items()`: keep pairs where `a in pr_set or b in pr_set`
- [ ] For each kept pair `(a, b), (score, co_count, total)`: `file_a=a`, `file_b=b` (generic, not file_in_pr/coupled_file — couplingguard maps these itself after calling)
- [ ] Classify risk, sort by score desc, truncate to `max_pairs`
- [ ] Return `list[CouplingPair]`

### 5.4 Public Re-exports (`__init__.py`)
- [ ] Add: `from coupling_core.analyzer import analyze_repo, analyze_pr_files, classify_risk`
- [ ] Add: `from coupling_core.models import Config, CouplingPair, RepoAnalysis, CouplingCoreError, ShallowCloneError`
- [ ] Add: `from coupling_core.matrix import build_normalized_matrix, CoChangeMatrix, NormalizedMatrix`
- [ ] Add: `from coupling_core.git_parser import get_file_commit_counts, apply_excludes, get_repo_name`

### 5.5 Verify Full Import Surface
- [ ] Run: `python -c "from coupling_core import analyze_repo, analyze_pr_files, Config, RepoAnalysis, CouplingPair, build_normalized_matrix, get_file_commit_counts, CouplingCoreError, ShallowCloneError; print('OK')"`

---

## Phase 6: Unit Tests

### 6.1 Test Fixtures (conftest.py)
- [ ] Define `@pytest.fixture fake_repo(tmp_path)`: `git.Repo.init(tmp_path)` + configure user email/name
- [ ] Add helper method `commit(files)` on fixture: create files, stage, commit

### 6.2 Git Parser Tests
- [ ] Test: shallow clone raises `ShallowCloneError`
- [ ] Test: merge commits excluded from output
- [ ] Test: `.png` file excluded as binary
- [ ] Test: glob `"docs/**"` excludes matching file
- [ ] Test: `resolve_rename` resolves `{old => new}` pattern
- [ ] Test: `decode_git_filename` decodes octal-escaped unicode filename
- [ ] Test: `get_repo_name` extracts `owner/repo` from HTTPS remote URL
- [ ] Test: `get_repo_name` extracts `owner/repo` from SSH remote URL (`git@github.com:owner/repo.git`)
- [ ] Test: `get_repo_name` returns directory name when no remote

### 6.3 Matrix Tests
- [ ] Test: two files in same commit → co_change count = 1
- [ ] Test: two files in 5 commits → co_change count = 5
- [ ] Test: pair below `min_occurrences=3` → not in filtered matrix
- [ ] Test: `normalize_pair(10, 10, 20)` → `0.5`
- [ ] Test: `normalize_pair(0, 0, 0)` → `0.0` (no division by zero)
- [ ] Test: empty commits list → empty matrix, empty file_counts

### 6.4 Analyzer Tests
- [ ] Test: `classify_risk(0.29, config)` → `"low"`
- [ ] Test: `classify_risk(0.30, config)` → `"medium"`
- [ ] Test: `classify_risk(0.70, config)` → `"high"`
- [ ] Test: `analyze_repo` returns `RepoAnalysis` with correct `total_commits_analyzed`
- [ ] Test: pairs in `RepoAnalysis.pairs` sorted by score descending
- [ ] Test: `analyze_pr_files` returns only pairs involving pr_files
- [ ] Test: `analyze_pr_files` truncates to `max_pairs`

---

## Phase 7: Documentation

### 7.1 README
- [ ] Add install snippet: `pip install coupling-core`
- [ ] Add usage example: `from coupling_core import analyze_repo, Config`
- [ ] Add full `analyze_repo` usage with `RepoAnalysis` output
- [ ] Add `analyze_pr_files` usage example
- [ ] Add `Config` fields table with defaults
- [ ] Add "Used by" section: couplingguard, churnmap

### 7.2 Type Stubs
- [ ] Verify `mypy --strict` passes on a consumer that does `from coupling_core import analyze_repo, Config`
- [ ] No `py.typed` marker missing — add `src/coupling_core/py.typed` (empty file) to signal PEP 561 compliance
