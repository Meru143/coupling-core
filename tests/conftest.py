from __future__ import annotations

from pathlib import Path

import git
import pytest


class RepoBuilder:
    """Wraps a fresh git.Repo so tests can make deterministic commits.

    Each ``commit(files)`` call appends a unique line to every named file
    (creating it if needed) and produces a single commit. Files keep their
    history so subsequent commits actually mutate them.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.repo = git.Repo.init(path, initial_branch="main")
        self._commit_count = 0
        with self.repo.config_writer() as cfg:
            cfg.set_value("user", "email", "test@example.com")
            cfg.set_value("user", "name", "Test User")
            cfg.set_value("commit", "gpgsign", "false")

    def commit(self, files: list[str], message: str | None = None) -> git.Commit:
        self._commit_count += 1
        msg = message or f"commit {self._commit_count}"
        for relpath in files:
            p = self.path / relpath
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("a", encoding="utf-8") as fh:
                fh.write(f"edit {self._commit_count}\n")
            self.repo.index.add([relpath])
        return self.repo.index.commit(msg)

    def make_shallow(self) -> None:
        """Mark the repo as shallow by writing .git/shallow."""
        shallow = Path(self.repo.git_dir) / "shallow"
        shallow.write_text(self.repo.head.commit.hexsha + "\n", encoding="utf-8")


@pytest.fixture
def fake_repo(tmp_path: Path) -> RepoBuilder:
    return RepoBuilder(tmp_path)
