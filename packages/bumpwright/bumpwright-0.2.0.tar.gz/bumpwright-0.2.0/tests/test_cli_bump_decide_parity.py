import json
import os
import subprocess
import sys
from pathlib import Path

from cli_helpers import run, setup_repo


def test_decide_flag_detects_no_api_changes(tmp_path: Path) -> None:
    """``decide`` should detect no bump when the API is unchanged."""
    repo, pkg, _ = setup_repo(tmp_path)

    # Modify implementation without changing the public API.
    init_file = pkg / "__init__.py"
    init_file.write_text(
        "def foo() -> int:\n    # no-op change\n    return 1\n", encoding="utf-8"
    )
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "chore: comment"], repo)

    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}

    res_decide = subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "decide"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert "bumpwright suggests: patch" in res_decide.stderr

    res_decide_json = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "decide",
            "--format",
            "json",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    data = json.loads(res_decide_json.stderr)
    assert data["level"] == "patch"
    assert data["confidence"] == 1.0
    assert data["reasons"] == ["Modified public symbol"]

    res_bump = subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "bump"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert "bumpwright bumped version" in res_bump.stderr
