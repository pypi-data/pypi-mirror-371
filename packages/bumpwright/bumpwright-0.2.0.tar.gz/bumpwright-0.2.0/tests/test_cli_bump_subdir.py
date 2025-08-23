import argparse
import logging
from pathlib import Path

import pytest
from cli_helpers import run, setup_repo

from bumpwright.cli.bump import bump_command


def _args() -> argparse.Namespace:
    """Construct arguments for ``bump_command``."""
    return argparse.Namespace(
        config="bumpwright.toml",
        base=None,
        head="HEAD",
        output_fmt="text",
        repo_url=None,
        enable_analyser=[],
        disable_analyser=[],
        pyproject="pyproject.toml",
        version_path=[],
        version_ignore=[],
        commit=False,
        tag=False,
        dry_run=False,
        changelog=None,
        changelog_template=None,
        changelog_exclude=[],
    )


def test_no_bump_from_subdir_version_only(
    monkeypatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Running from a subdirectory skips bump when only version files changed."""
    repo, pkg, _ = setup_repo(tmp_path)
    pyproject = repo / "pyproject.toml"
    pyproject.write_text(
        "[project]\nname = 'demo'\nversion = '0.1.1'\n", encoding="utf-8"
    )
    run(["git", "add", "pyproject.toml"], repo)
    run(["git", "commit", "-m", "chore: bump version"], repo)

    monkeypatch.chdir(pkg)
    args = _args()
    args.config = "../bumpwright.toml"
    with caplog.at_level(logging.INFO):
        res = bump_command(args)
    assert res == 0
    assert "No version bump needed" in caplog.text
