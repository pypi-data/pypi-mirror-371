from __future__ import annotations

import pytest

from bumpwright import analysers
from bumpwright.analysers import (
    Analyser,
    available,
    get_analyser_info,
    load_enabled,
    register,
)
from bumpwright.compare import Impact
from bumpwright.config import Config


def test_register_records_metadata() -> None:
    """Ensure register stores class and description."""
    backup = analysers.REGISTRY.copy()
    try:
        analysers.REGISTRY.clear()

        @register("dummy", "Example analyser")
        class DummyAnalyser(Analyser):
            def __init__(self, cfg: Config) -> None:  # pragma: no cover - simple init
                self.cfg = cfg

            def collect(self, ref: str) -> object:  # pragma: no cover - trivial
                return {}

            def compare(self, old: object, new: object) -> list[Impact]:  # pragma: no cover - trivial
                return []

        assert "dummy" in available()
        info = get_analyser_info("dummy")
        assert info and info.description == "Example analyser"
        assert info.cls is DummyAnalyser
    finally:
        analysers.REGISTRY.clear()
        analysers.REGISTRY.update(backup)


def test_load_enabled_errors_for_unknown() -> None:
    """Unknown analysers should raise a clear error."""
    backup = analysers.REGISTRY.copy()
    try:
        analysers.REGISTRY.clear()
        cfg = Config()
        cfg.analysers.enabled.add("missing")
        with pytest.raises(ValueError):
            load_enabled(cfg)
    finally:
        analysers.REGISTRY.clear()
        analysers.REGISTRY.update(backup)
