import argparse
import os
from pathlib import Path

from cli_helpers import run, setup_repo

from bumpwright.cli.decide import _collect_impacts
from bumpwright.compare import decide_bump
from bumpwright.config import load_config


def test_private_helper_triggers_patch(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    init = pkg / "__init__.py"
    init.write_text(
        "def foo() -> int:\n    return _helper()\n\n"
        "def _helper() -> int:\n    return 1\n",
        encoding="utf-8",
    )
    run(["git", "commit", "-am", "feat: add helper"], repo)

    init.write_text(
        "def foo() -> int:\n    return _helper()\n\n"
        "def _helper() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "commit", "-am", "chore: tweak helper"], repo)

    cfg = load_config(repo / "bumpwright.toml")
    args = argparse.Namespace(
        enable_analyser=None, disable_analyser=None, no_impl_change_patch=False
    )
    prev_cwd = Path.cwd()
    try:
        os.chdir(repo)
        impacts = _collect_impacts("HEAD^", "HEAD", cfg, args)
    finally:
        os.chdir(prev_cwd)
    decision = decide_bump(impacts)
    assert decision.level == "patch"
    assert decision.reasons == ["Modified public module"]
