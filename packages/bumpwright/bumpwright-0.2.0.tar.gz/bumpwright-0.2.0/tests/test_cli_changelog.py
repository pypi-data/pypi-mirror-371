import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from cli_helpers import run, run_installed, setup_repo


def test_bump_uses_config_path(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    (repo / "bumpwright.toml").write_text(
        "[project]\npublic_roots=['pkg']\n[changelog]\npath='CHANGELOG.md'\n",
        encoding="utf-8",
    )
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "__init__.py").write_text(
        "def foo() -> int:\n    return 1\n\n\ndef bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    sha = run(["git", "rev-parse", "--short", "HEAD"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    output = res.stderr
    content = (repo / "CHANGELOG.md").read_text()
    today = date.today().isoformat()
    assert f"## [v0.2.0] - {today}" in content
    assert f"- {sha} feat: change" in content
    assert "## [v0.2.0]" not in output


def test_bump_writes_changelog(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    sha = run(["git", "rev-parse", "--short", "HEAD"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "CHANGELOG.md",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    output = res.stderr
    content = (repo / "CHANGELOG.md").read_text()
    today = date.today().isoformat()
    assert f"## [v0.2.0] - {today}" in content
    assert f"- {sha} feat: change" in content
    assert "## [v0.2.0]" not in output


def test_bump_writes_changelog_stdout(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    sha = run(["git", "rev-parse", "--short", "HEAD"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "-",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    output = res.stderr
    today = date.today().isoformat()
    assert f"## [v0.2.0] - {today}" in output
    assert f"- {sha} feat: change" in output
    assert not (repo / "CHANGELOG.md").exists()


def test_changelog_links_repo_url_cli(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    sha = run(["git", "rev-parse", "--short", "HEAD"], repo)
    res = run_installed(
        [
            "bumpwright",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "CHANGELOG.md",
            "--format",
            "md",
            "--repo-url",
            "https://example.com/repo",
        ],
        repo,
    )
    content = (repo / "CHANGELOG.md").read_text()
    expected = f"- [{sha}](https://example.com/repo/commit/{sha}) feat: change"
    assert expected in content
    assert "TypeError" not in res.stderr


def test_changelog_links_repo_url_config(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    (repo / "bumpwright.toml").write_text(
        "[project]\npublic_roots=['pkg']\n[changelog]\nrepo_url='https://example.com/repo'\n",
        encoding="utf-8",
    )
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    sha = run(["git", "rev-parse", "--short", "HEAD"], repo)
    res = run_installed(
        [
            "bumpwright",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "-",
            "--format",
            "md",
        ],
        repo,
    )
    output = res.stderr
    expected = f"- [{sha}](https://example.com/repo/commit/{sha}) feat: change"
    assert expected in output
    assert "TypeError" not in output


def test_changelog_custom_template_cli(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    (repo / "tpl.j2").write_text("VERSION={{ version }}\n", encoding="utf-8")
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "CHANGELOG.md",
            "--changelog-template",
            "tpl.j2",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert (repo / "CHANGELOG.md").read_text() == "VERSION=0.2.0\n"


def test_changelog_custom_template_config(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    tpl = repo / "tpl.j2"
    tpl.write_text("Built {{ version }}\n", encoding="utf-8")
    (repo / "bumpwright.toml").write_text(
        "[project]\npublic_roots=['pkg']\n[changelog]\npath='CHANGELOG.md'\ntemplate='tpl.j2'\n",
        encoding="utf-8",
    )
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert (repo / "CHANGELOG.md").read_text() == "Built 0.2.0\n"


def test_changelog_exclude_cli(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "commit", "--allow-empty", "-m", "chore: drop"], repo)
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: keep"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "CHANGELOG.md",
            "--changelog-exclude",
            "^chore",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    content = (repo / "CHANGELOG.md").read_text()
    assert "feat: keep" in content
    assert "chore: drop" not in content


def test_changelog_exclude_config(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    (repo / "bumpwright.toml").write_text(
        "[project]\npublic_roots=['pkg']\n[changelog]\npath='CHANGELOG.md'\nexclude=['^chore']\n",
        encoding="utf-8",
    )
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "commit", "--allow-empty", "-m", "chore: drop"], repo)
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: keep"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    content = (repo / "CHANGELOG.md").read_text()
    assert "feat: keep" in content
    assert "chore: drop" not in content


def test_changelog_diff_and_contributors(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    run(["git", "tag", "v0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(
        [
            "git",
            "commit",
            "-am",
            "feat: change",
            "--author",
            "Alice <alice@users.noreply.github.com>",
        ],
        repo,
    )
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "CHANGELOG.md",
            "--repo-url",
            "https://github.com/me/project",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    content = (repo / "CHANGELOG.md").read_text()
    compare_line = "[Diff since v0.1.0](https://github.com/me/project/compare/v0.1.0...v0.2.0)"
    assert compare_line in content
    assert "### Contributors" in content
    assert "- [Alice](https://github.com/alice)" in content
    assert "### Breaking changes" not in content


def test_changelog_breaking_changes(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    run(["git", "commit", "--allow-empty", "-m", "chore(release): 0.1.0"], repo)
    run(["git", "tag", "v0.1.0"], repo)
    (pkg / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat!: break"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--changelog",
            "CHANGELOG.md",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    content = (repo / "CHANGELOG.md").read_text()
    assert "### Breaking changes" in content
    assert "feat!: break" in content
