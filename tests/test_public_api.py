"""Public API surface test.

These imports MUST work. They are part of coupling-core's public contract.
Removing or renaming any of these symbols is a breaking change requiring a
major version bump.
"""

from __future__ import annotations

import inspect


def test_top_level_imports_resolve() -> None:
    from coupling_core import get_commits, open_repo

    assert callable(get_commits)
    assert callable(open_repo)

    from coupling_core import git_parser

    assert inspect.signature(get_commits) == inspect.signature(git_parser.get_commits)
    assert inspect.signature(open_repo) == inspect.signature(git_parser.open_repo)


def test_full_public_surface_present() -> None:
    """Every name in __all__ must actually exist on the module."""
    import coupling_core

    for name in coupling_core.__all__:
        assert hasattr(coupling_core, name), f"missing public name: {name}"
