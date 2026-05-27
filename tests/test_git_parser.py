from __future__ import annotations

from pathlib import Path

import pytest

from coupling_core.git_parser import (
    BINARY_EXTENSIONS,
    _decode_unicode_path,
    _normalize_rename,
    apply_excludes,
    get_commits,
    get_file_commit_counts,
    get_repo_name,
    open_repo,
)
from coupling_core.models import CouplingCoreError, ShallowCloneError
from tests.conftest import RepoBuilder


def test_open_repo_invalid_path_raises(tmp_path: Path) -> None:
    with pytest.raises(CouplingCoreError, match="path does not exist"):
        open_repo(tmp_path / "does-not-exist")


def test_open_repo_not_a_git_repo_raises(tmp_path: Path) -> None:
    (tmp_path / "notgit").mkdir()
    with pytest.raises(CouplingCoreError, match="not a git repository"):
        open_repo(tmp_path / "notgit")


def test_open_repo_shallow_clone_raises(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    fake_repo.make_shallow()
    with pytest.raises(ShallowCloneError, match="shallow clone"):
        open_repo(fake_repo.path)


def test_open_repo_happy_path(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    repo = open_repo(fake_repo.path)
    assert repo.head.commit is not None


def test_get_commits_basic(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py", "b.py"])
    fake_repo.commit(["a.py", "b.py"])
    commits = get_commits(fake_repo.repo, lookback_days=30)
    assert len(commits) == 2
    assert all(set(c) == {"a.py", "b.py"} for c in commits)


def test_get_commits_empty_repo(tmp_path: Path) -> None:
    repo = __import__("git").Repo.init(tmp_path, initial_branch="main")
    assert get_commits(repo, lookback_days=30) == []


def test_get_commits_merge_excluded(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["base.py"])
    fake_repo.repo.git.checkout("-b", "feature")
    fake_repo.commit(["feature.py"])
    fake_repo.repo.git.checkout("main")
    fake_repo.commit(["main.py"])
    fake_repo.repo.git.merge("feature", "--no-ff", "-m", "merge feature")

    commits = get_commits(fake_repo.repo, lookback_days=30)
    # 3 real commits (base, feature, main) — the merge is excluded
    assert len(commits) == 3
    flat = {f for files in commits for f in files}
    assert flat == {"base.py", "feature.py", "main.py"}


def test_get_commits_binary_excluded(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py", "logo.png"])
    commits = get_commits(fake_repo.repo, lookback_days=30)
    assert commits == [["a.py"]]


def test_get_commits_glob_exclude(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["src/main.py", "docs/readme.md"])
    commits = get_commits(fake_repo.repo, lookback_days=30, exclude_patterns=["docs/**"])
    assert commits == [["src/main.py"]]


def test_normalize_rename_brace() -> None:
    assert _normalize_rename("src/{old.py => new.py}") == "src/new.py"
    assert _normalize_rename("{old/dir => new/dir}/file.py") == "new/dir/file.py"


def test_normalize_rename_plain_arrow() -> None:
    assert _normalize_rename("old.py => new.py") == "new.py"


def test_normalize_rename_passthrough() -> None:
    assert _normalize_rename("unchanged/path.py") == "unchanged/path.py"


def test_decode_unicode_path_octal() -> None:
    # "café.py" with é encoded as octal escape (\303\251 = 0xC3 0xA9 = é in UTF-8)
    encoded = '"caf\\303\\251.py"'
    assert _decode_unicode_path(encoded) == "café.py"


def test_decode_unicode_path_passthrough() -> None:
    assert _decode_unicode_path("plain/path.py") == "plain/path.py"


def test_apply_excludes() -> None:
    files = ["src/a.py", "docs/b.md", "tests/c.py"]
    assert apply_excludes(files, ["docs/*"]) == ["src/a.py", "tests/c.py"]
    assert apply_excludes(files, []) == files


def test_get_file_commit_counts() -> None:
    commits = [["a.py", "b.py"], ["a.py"], ["b.py", "c.py"]]
    counts = get_file_commit_counts(commits)
    assert counts == {"a.py": 2, "b.py": 2, "c.py": 1}
    assert not isinstance(counts, type({}.copy())) or not hasattr(counts, "default_factory")


def test_get_repo_name_https(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    fake_repo.repo.create_remote("origin", "https://github.com/owner/repo.git")
    assert get_repo_name(fake_repo.repo) == "owner/repo"


def test_get_repo_name_ssh(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    fake_repo.repo.create_remote("origin", "git@github.com:owner/repo.git")
    assert get_repo_name(fake_repo.repo) == "owner/repo"


def test_get_repo_name_ssh_url_scheme(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    fake_repo.repo.create_remote("origin", "ssh://git@github.com/owner/repo.git")
    assert get_repo_name(fake_repo.repo) == "owner/repo"


def test_get_repo_name_no_remote(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    assert get_repo_name(fake_repo.repo) == fake_repo.path.name


def test_get_repo_name_gitlab_subgroup(fake_repo: RepoBuilder) -> None:
    fake_repo.commit(["a.py"])
    fake_repo.repo.create_remote("origin", "https://gitlab.com/group/sub/project.git")
    # Last two path segments → sub/project
    assert get_repo_name(fake_repo.repo) == "sub/project"


def test_binary_extensions_includes_common_types() -> None:
    for ext in (".png", ".jpg", ".pdf", ".zip", ".exe"):
        assert ext in BINARY_EXTENSIONS
