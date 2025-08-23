import argparse
import json
import logging
import os
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest
from cli_helpers import run, setup_repo

from bumpwright.cli.history import _commit_date, _diff_stats, history_command
from bumpwright.gitutils import GitCommandError, last_release_commit
from bumpwright.versioning import read_project_version


def _run_history(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    return subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "history", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


@contextmanager
def cwd(path: Path) -> Iterator[None]:
    """Temporarily change the current working directory."""

    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


def _release_repo(tmp_path: Path) -> tuple[Path, Path]:
    """Create a repository with a tagged bumpwright release."""

    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--commit",
            "--tag",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    return repo, pkg


def test_history_fetches_remote_tags(tmp_path: Path) -> None:
    """Remote tags are fetched automatically before listing history."""

    remote = tmp_path / "remote.git"
    run(["git", "init", "--bare", str(remote)], tmp_path)

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    repo, pkg, _ = setup_repo(work_dir)
    run(["git", "tag", "v0.1.0"], repo)
    run(["git", "remote", "add", "origin", str(remote)], repo)
    run(["git", "push", "-u", "origin", "master", "--tags"], repo)

    clone = tmp_path / "clone"
    run(["git", "clone", str(remote), str(clone)], tmp_path)
    assert "v0.2.0" not in run(["git", "tag"], clone)

    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    run(["git", "tag", "v0.2.0"], repo)
    run(["git", "push", "origin", "master", "--tags"], repo)

    res = _run_history(clone)
    assert "v0.2.0" in res.stderr
    assert "v0.2.0" in run(["git", "tag"], clone)


def test_history_outputs_in_all_formats(tmp_path: Path) -> None:
    """History subcommand renders tag information in all formats."""
    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    date = run(["git", "show", "-s", "--format=%cI", "v0.1.0"], repo)

    res = _run_history(repo)
    assert f"v0.1.0 0.1.0 {date}" in res.stderr

    res_md = _run_history(repo, "--format", "md")
    assert f"| v0.1.0 | 0.1.0 | {date}" in res_md.stderr

    res_json = _run_history(repo, "--format", "json")
    data = json.loads(res_json.stderr)
    assert data[0]["tag"] == "v0.1.0"
    assert data[0]["version"] == "0.1.0"
    assert data[0]["date"] == date


def test_history_local_time_formats(tmp_path: Path) -> None:
    """Commit dates can be rendered in local time across all formats."""

    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    date_iso = run(["git", "show", "-s", "--format=%cI", "v0.1.0"], repo)
    local = datetime.fromisoformat(date_iso).astimezone().strftime("%Y-%m-%d %H:%M:%S")

    res = _run_history(repo, "--local-time")
    assert f"v0.1.0 0.1.0 {local}" in res.stderr

    res_md = _run_history(repo, "--format", "md", "--local-time")
    assert f"| v0.1.0 | 0.1.0 | {local}" in res_md.stderr

    res_json = _run_history(repo, "--format", "json", "--local-time")
    data = json.loads(res_json.stderr)
    assert data[0]["date"] == local


def test_history_stats_and_dates(tmp_path: Path) -> None:
    """``--stats`` adds diff information and commit dates."""
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    run(["git", "tag", "v0.2.0"], repo)

    res = _run_history(repo, "--stats")
    date = run(["git", "show", "-s", "--format=%cI", "v0.2.0"], repo)
    assert "+2 -0" in res.stderr and date in res.stderr

    res_md = _run_history(repo, "--stats", "--format", "md")
    assert "+2 -0" in res_md.stderr and date in res_md.stderr

    res_json = _run_history(repo, "--stats", "--format", "json")
    json_text, _, _ = res_json.stderr.partition("Project version")
    data = json.loads(json_text)
    assert data[0]["date"] == date
    assert data[0]["stats"] == {"insertions": 2, "deletions": 0}


def test_history_warns_on_mismatch(tmp_path: Path) -> None:
    """Warn when project version differs from the latest tag."""
    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    (repo / "pyproject.toml").write_text(
        """[project]\nname='demo'\nversion='0.2.0'\n""", encoding="utf-8"
    )
    res = _run_history(repo)
    assert "Project version 0.2.0 differs from latest tag 0.1.0" in res.stderr


def test_history_no_tags(tmp_path: Path) -> None:
    """Return gracefully when the repository has no tags."""

    repo, _, _ = setup_repo(tmp_path)
    res = _run_history(repo)
    assert "No tags found." in res.stderr


def test_history_rollback_reverts_release(tmp_path: Path) -> None:
    """``--rollback`` removes the tag and restores versioned files only."""

    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)

    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--commit",
            "--tag",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert "v0.2.0" in run(["git", "tag"], repo)

    _run_history(repo, "--rollback", "v0.2.0")

    tags = run(["git", "tag"], repo)
    assert "v0.2.0" not in tags
    assert read_project_version(repo / "pyproject.toml") == "0.1.0"
    msg = run(["git", "log", "-1", "--pretty=%s"], repo)
    assert msg == "chore(release): undo v0.2.0"


def test_history_purge_uninitialises_project(tmp_path: Path) -> None:
    """``--purge`` removes bumpwright state and leaves the repo uninitialised."""

    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)

    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--commit",
            "--tag",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert "v0.2.0" in run(["git", "tag"], repo)

    _run_history(repo, "--purge")

    tags = run(["git", "tag"], repo)
    assert "v0.2.0" not in tags and "v0.1.0" in tags
    assert read_project_version(repo / "pyproject.toml") == "0.1.0"
    assert last_release_commit(str(repo)) is None


def test_history_purge_preserves_nonrelease_commits(tmp_path: Path) -> None:
    """Purge removes release commits while keeping later work intact."""

    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)

    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)

    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--commit",
            "--tag",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    (pkg / "more.py").write_text("def baz() -> int:\n    return 3\n", encoding="utf-8")
    run(["git", "add", "pkg/more.py"], repo)
    run(["git", "commit", "-m", "feat: add baz"], repo)

    _run_history(repo, "--purge")

    tags = run(["git", "tag"], repo)
    assert "v0.2.0" not in tags and "v0.1.0" in tags
    assert read_project_version(repo / "pyproject.toml") == "0.1.0"
    head_msg = run(["git", "log", "-1", "--pretty=%s"], repo)
    assert head_msg == "feat: add baz"
    assert last_release_commit(str(repo)) is None


def test_history_purge_retains_local_version_edits(tmp_path: Path) -> None:
    """Uncommitted version file changes persist after purge."""

    repo, _ = _release_repo(tmp_path)
    pyproject = repo / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8").replace("0.2.0", "0.2.1")
    pyproject.write_text(content, encoding="utf-8")

    _run_history(repo, "--purge")

    assert pyproject.read_text(encoding="utf-8") == content
    msg = run(["git", "log", "-1", "--pretty=%s"], repo)
    assert msg == "chore(version): restore version files after purge"


def test_history_rollback_refuses_dirty_worktree(tmp_path: Path) -> None:
    """Rollback aborts when uncommitted changes exist."""

    repo, pkg = _release_repo(tmp_path)
    (pkg / "notes.txt").write_text("hello", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "history",
            "--rollback",
            "v0.2.0",
        ],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert res.returncode == 1
    assert "Uncommitted changes present" in res.stderr
    assert "v0.2.0" in run(["git", "tag"], repo)


def test_history_purge_refuses_dirty_worktree(tmp_path: Path) -> None:
    """Purge aborts when uncommitted changes exist."""

    repo, pkg = _release_repo(tmp_path)
    (pkg / "notes.txt").write_text("hello", encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "history",
            "--purge",
        ],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert res.returncode == 1
    assert "Uncommitted changes present" in res.stderr
    assert "v0.2.0" in run(["git", "tag"], repo)


def test_history_rollback_conflict_aborts(tmp_path: Path) -> None:
    """Failed reverts leave the worktree clean."""

    repo, _ = _release_repo(tmp_path)
    (repo / "pyproject.toml").write_text(
        """[project]\nname='demo'\nversion='0.2.1'\n""", encoding="utf-8"
    )
    run(["git", "commit", "-am", "chore: bump"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "history",
            "--rollback",
            "v0.2.0",
        ],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert res.returncode == 1
    assert "Failed to revert" in res.stderr
    assert run(["git", "status", "--porcelain"], repo) == ""


def test_history_purge_conflict_aborts(tmp_path: Path) -> None:
    """Rebase conflicts during purge are aborted cleanly."""

    repo, _ = _release_repo(tmp_path)
    (repo / "pyproject.toml").write_text(
        """[project]\nname='demo'\nversion='0.2.1'\n""", encoding="utf-8"
    )
    run(["git", "commit", "-am", "chore: bump"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "history",
            "--purge",
        ],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert res.returncode == 1
    assert not (repo / ".git" / "rebase-merge").exists()
    assert not (repo / ".git" / "rebase-apply").exists()
    assert last_release_commit(str(repo)) is not None


def test_commit_date_handles_missing_tag(tmp_path: Path) -> None:
    """``_commit_date`` returns empty string for unknown tags."""

    repo, _, _ = setup_repo(tmp_path)
    with cwd(repo):
        assert _commit_date("v0.1.0") == ""


def test_commit_date_returns_timestamp(tmp_path: Path) -> None:
    """``_commit_date`` returns the commit timestamp for a tag."""

    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    expected = run(["git", "show", "-s", "--format=%cI", "v0.1.0"], repo)
    with cwd(repo):
        assert _commit_date("v0.1.0") == expected


def test_diff_stats_reports_changes(tmp_path: Path) -> None:
    """``_diff_stats`` returns insertion and deletion counts."""

    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    run(["git", "tag", "v0.2.0"], repo)
    with cwd(repo):
        assert _diff_stats("v0.1.0", "v0.2.0") == (2, 0)


def test_diff_stats_invalid_tag_raises(tmp_path: Path) -> None:
    """Unknown tags cause ``_diff_stats`` to raise ``CalledProcessError``."""

    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    with cwd(repo), pytest.raises(subprocess.CalledProcessError):
        _diff_stats("v0.1.0", "v0.3.0")


def test_history_rollback_invalid_tag_fails(tmp_path: Path) -> None:
    """``--rollback`` with a missing tag exits with an error."""

    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "history",
            "--rollback",
            "v0.2.0",
        ],
        check=False,
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert res.returncode == 1
    assert "Failed to resolve tag v0.2.0" in res.stderr


def test_history_rollback_tag_delete_failure(
    monkeypatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Return ``1`` when tag deletion fails during rollback."""

    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    run(["git", "tag", "v0.2.0"], repo)

    def fail(
        args: list[str], cwd: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        if args[:2] == ["tag", "-d"]:
            raise GitCommandError(1, ["git", *args], stderr="boom")
        return subprocess.CompletedProcess(["git", *args], 0, "", "")

    monkeypatch.setattr("bumpwright.cli.history.run_git", fail)
    monkeypatch.chdir(repo)
    with caplog.at_level(logging.ERROR):
        res = history_command(
            argparse.Namespace(output_fmt="text", stats=False, rollback="v0.2.0")
        )
    assert res == 1
    assert "Failed to delete tag v0.2.0" in caplog.text
