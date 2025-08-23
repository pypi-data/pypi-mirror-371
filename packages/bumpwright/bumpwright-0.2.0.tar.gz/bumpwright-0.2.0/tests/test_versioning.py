from datetime import date
from pathlib import Path

import pytest
from tomlkit import dumps as toml_dumps
from tomlkit import parse as toml_parse
from tomlkit.exceptions import ParseError

from bumpwright import version_schemes, versioning
from bumpwright.config import Config, load_config
from bumpwright.versioning import (
    _replace_version,
    _resolve_files,
    apply_bump,
    bump_string,
    clear_version_file_cache,
    find_pyproject,
    read_project_version,
    write_project_version,
)


def test_bump_string():
    assert bump_string("1.2.3", "patch") == "1.2.4"
    assert bump_string("1.2.3", "minor") == "1.3.0"
    assert bump_string("1.2.3", "major") == "2.0.0"


def test_bump_string_uses_cached_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Repeated calls reuse cached configuration."""

    versioning._get_default_config.cache_clear()
    calls = {"count": 0}

    def fake_load_config(path: str = "bumpwright.toml"):
        calls["count"] += 1
        return load_config(path)

    monkeypatch.setattr(versioning, "load_config", fake_load_config)
    assert versioning.bump_string("1.0.0", "patch") == "1.0.1"
    assert versioning.bump_string("1.0.1", "patch") == "1.0.2"
    assert calls["count"] == 1
    versioning._get_default_config.cache_clear()


def test_bump_string_semver_prerelease_and_build() -> None:
    """SemVer release bumps drop prerelease and build metadata."""

    assert bump_string("1.2.3-alpha.1+build.1", "patch", scheme="semver") == "1.2.4"
    assert bump_string("1.2.3-alpha.1+build.1", "minor", scheme="semver") == "1.3.0"
    assert bump_string("1.2.3-alpha.1+build.1", "major", scheme="semver") == "2.0.0"
    assert bump_string("1.2.3-alpha.1", "pre", scheme="semver") == "1.2.3-alpha.2"
    assert bump_string("1.2.3+build.1", "build", scheme="semver") == "1.2.3+build.2"


@pytest.mark.parametrize("version", ["01.2.3", "1.02.3", "1.2.03"])
def test_bump_string_semver_rejects_leading_zeros(version: str) -> None:
    """SemVer parsing rejects numeric components with leading zeros."""

    with pytest.raises(ValueError):
        bump_string(version, "patch", scheme="semver")


def test_bump_string_unknown_scheme() -> None:
    """Unsupported version schemes raise clear errors."""

    with pytest.raises(ValueError, match="Unknown version scheme"):
        bump_string("1.2.3", "patch", scheme="pep440")


def test_bump_string_calver(monkeypatch: pytest.MonkeyPatch) -> None:
    """Calendar version bumps use the current date for major and minor."""

    class FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2024, 4, 1)

    monkeypatch.setattr(version_schemes, "date", FrozenDate)
    assert bump_string("2024.03.1", "minor", scheme="calver") == "2024.04.0"
    assert bump_string("2024.04.0", "patch", scheme="calver") == "2024.04.1"
    assert bump_string("2023.12.5", "major", scheme="calver") == "2024.04.0"
    assert bump_string("2024.04.0-rc.1", "pre", scheme="calver") == "2024.04.0-rc.2"
    assert (
        bump_string("2024.04.0+build.1", "build", scheme="calver")
        == "2024.04.0+build.2"
    )


def test_calver_patch_rollover_month(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch bumps roll over to a new month with patch reset."""

    class FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2024, 5, 1)

    monkeypatch.setattr(version_schemes, "date", FrozenDate)
    assert bump_string("2024.04.2", "patch", scheme="calver") == "2024.05.0"


def test_calver_patch_rollover_year(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch bumps roll over to a new year and clear metadata."""

    class FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2025, 1, 1)

    monkeypatch.setattr(version_schemes, "date", FrozenDate)
    assert (
        bump_string("2024.12.2-rc.1+build.3", "patch", scheme="calver") == "2025.01.0"
    )


@pytest.mark.parametrize("level", ["", "foo", "majority"])
def test_bump_string_invalid_level(level: str) -> None:
    """Ensure ``bump_string`` rejects unsupported bump levels."""

    with pytest.raises(ValueError):
        bump_string("1.2.3", level)  # type: ignore[arg-type]


def test_bump_segment_default() -> None:
    """Missing segments default to an ``.1`` suffix."""

    assert version_schemes._bump_segment(None, "rc") == "rc.1"


def test_bump_segment_no_numeric() -> None:
    """Segments without digits append ``.1``."""

    assert version_schemes._bump_segment("alpha", "rc") == "alpha.1"


def test_calver_invalid_version_raises() -> None:
    """Invalid calendar versions raise ``ValueError``."""

    scheme = version_schemes.CalverScheme()
    with pytest.raises(ValueError):
        scheme.bump("2024.13.0", "patch")


@pytest.fixture
def missing_file(tmp_path: Path) -> Path:
    """Return a path to a non-existent ``pyproject.toml`` file."""

    return tmp_path / "pyproject.toml"


@pytest.fixture
def pyproject_missing_version(tmp_path: Path) -> Path:
    """Create a ``pyproject.toml`` lacking the version field."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {}}))
    return py


@pytest.fixture
def pyproject_malformed(tmp_path: Path) -> Path:
    """Create a malformed ``pyproject.toml`` to trigger parse errors."""

    py = tmp_path / "pyproject.toml"
    py.write_text("::invalid::", encoding="utf-8")
    return py


@pytest.mark.parametrize(
    ("path_fixture", "exc"),
    [
        ("missing_file", FileNotFoundError),
        ("pyproject_missing_version", KeyError),
        ("pyproject_malformed", ParseError),
    ],
)
def test_read_project_version_errors(
    path_fixture: str, exc: type[Exception], request: pytest.FixtureRequest
) -> None:
    """Validate ``read_project_version`` error handling for bad inputs."""

    path = request.getfixturevalue(path_fixture)
    with pytest.raises(exc):
        read_project_version(path)


def test_apply_bump(tmp_path: Path):
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    out = apply_bump("minor", py, cfg=cfg)
    assert out.old == "0.1.0" and out.new == "0.2.0"
    assert read_project_version(py) == "0.2.0"
    assert py in out.files
    assert out.skipped == []


def test_apply_bump_dry_run(tmp_path: Path) -> None:
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "1.2.3"}}))
    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    out = apply_bump("patch", py, dry_run=True, cfg=cfg)
    assert out.old == "1.2.3" and out.new == "1.2.4"
    assert read_project_version(py) == "1.2.3"
    assert out.files == []
    assert out.skipped == []


def test_apply_bump_updates_extra_files(tmp_path: Path) -> None:
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    setup = tmp_path / "setup.py"
    setup.write_text("version='0.1.0'", encoding="utf-8")
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    init = pkg / "__init__.py"
    init.write_text("__version__ = '0.1.0'", encoding="utf-8")
    ver = pkg / "version.py"
    ver.write_text("VERSION = '0.1.0'", encoding="utf-8")
    _ver = pkg / "_version.py"
    _ver.write_text("version = '0.1.0'", encoding="utf-8")

    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    out = apply_bump("patch", py, cfg=cfg)
    assert out.new == "0.1.1"
    assert "version='0.1.0'" in setup.read_text(encoding="utf-8")
    assert "__version__ = '0.1.1'" in init.read_text(encoding="utf-8")
    assert "VERSION = '0.1.0'" in ver.read_text(encoding="utf-8")
    assert "version = '0.1.0'" in _ver.read_text(encoding="utf-8")
    # Only files declaring ``__version__`` are updated.
    assert out.files == [py, init]
    assert out.skipped == []


def test_apply_bump_ignore_patterns(tmp_path: Path) -> None:
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "1.0.0"}}))
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    init = pkg / "__init__.py"
    init.write_text("__version__ = '1.0.0'", encoding="utf-8")

    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    out = apply_bump("minor", py, ignore=[str(init)], cfg=cfg)
    assert "__version__ = '1.0.0'" in init.read_text(encoding="utf-8")
    assert init not in out.files
    assert out.skipped == []


def test_apply_bump_mixed_ignore_patterns(tmp_path: Path) -> None:
    """Ignore files using absolute and relative patterns."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "1.0.0"}}))
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    keep = pkg / "keep.py"
    keep.write_text("__version__ = '1.0.0'", encoding="utf-8")
    ignore_rel = pkg / "ignore_rel.py"
    ignore_rel.write_text("__version__ = '1.0.0'", encoding="utf-8")
    ignore_abs = tmp_path / "ignore_abs.py"
    ignore_abs.write_text("__version__ = '1.0.0'", encoding="utf-8")

    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    out = apply_bump(
        "patch",
        py,
        paths=["pkg/*.py", str(ignore_abs)],
        ignore=[str(ignore_abs), "pkg/ignore_rel.py"],
        cfg=cfg,
    )

    assert "__version__ = '1.0.1'" in keep.read_text(encoding="utf-8")
    assert "__version__ = '1.0.0'" in ignore_rel.read_text(encoding="utf-8")
    assert "__version__ = '1.0.0'" in ignore_abs.read_text(encoding="utf-8")
    assert py in out.files and keep in out.files
    assert ignore_rel not in out.files and ignore_abs not in out.files
    assert out.skipped == []


@pytest.mark.parametrize(
    "ignore_dir,file_name",
    [
        ("build/pkg", "__init__.py"),
        ("dist/pkg", "__init__.py"),
        ("project.egg-info", "__init__.py"),
        (".eggs/pkg", "__init__.py"),
        (".venv/pkg", "__init__.py"),
        ("venv/pkg", "__init__.py"),
        (".env/pkg", "__init__.py"),
        ("pkg/__pycache__", "version.py"),
    ],
)
def test_default_version_ignore_patterns(
    tmp_path: Path, ignore_dir: str, file_name: str
) -> None:
    """Version files in ignored directories are skipped by default."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "1.0.0"}}))
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    init = pkg / "__init__.py"
    init.write_text("__version__ = '1.0.0'", encoding="utf-8")

    ignore_path = tmp_path / ignore_dir
    ignore_path.mkdir(parents=True)
    ignored_file = ignore_path / file_name
    ignored_file.write_text("__version__ = '1.0.0'", encoding="utf-8")

    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    out = apply_bump(
        "minor",
        py,
        paths=cfg.version.paths,
        ignore=cfg.version.ignore,
        cfg=cfg,
    )

    assert "__version__ = '1.1.0'" in init.read_text(encoding="utf-8")
    assert "__version__ = '1.0.0'" in ignored_file.read_text(encoding="utf-8")
    assert ignored_file not in out.files
    assert out.skipped == []


def test_apply_bump_ignores_files_without_version(tmp_path: Path) -> None:
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    extra = tmp_path / "extra.py"
    extra.write_text("print('no version here')", encoding="utf-8")

    out = apply_bump(
        "patch",
        py,
        paths=[str(extra)],
        ignore=[],
        config_path=tmp_path / "bumpwright.toml",
    )

    assert extra not in out.files
    assert extra not in out.skipped
    assert extra.read_text(encoding="utf-8") == "print('no version here')"


def test_replace_version_returns_false_when_unmodified(tmp_path: Path) -> None:
    target = tmp_path / "module.py"
    target.write_text("print('hello')", encoding="utf-8")

    assert not _replace_version(target, "0.1.0", "0.2.0")
    assert target.read_text(encoding="utf-8") == "print('hello')"


def test_replace_version_multiple_matches(tmp_path: Path) -> None:
    """Only the expected version occurrence is updated."""

    target = tmp_path / "module.py"
    target.write_text(
        "__version__ = '0.1.0'\n__version__ = '0.2.0'\n", encoding="utf-8"
    )

    assert _replace_version(target, "0.1.0", "0.1.1")
    assert target.read_text(encoding="utf-8") == (
        "__version__ = '0.1.1'\n__version__ = '0.2.0'\n"
    )


def test_replace_version_uses_module_patterns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure module-level regex patterns drive version replacement."""

    target = tmp_path / "module.py"
    target.write_text("__version__ = '0.1.0'", encoding="utf-8")
    monkeypatch.setattr(versioning, "_VERSION_RE_PATTERNS", [])

    assert not _replace_version(target, "0.1.0", "0.2.0")
    assert target.read_text(encoding="utf-8") == "__version__ = '0.1.0'"


def test_apply_bump_respects_scheme(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Use configured version scheme when bumping."""

    class FrozenDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2024, 4, 1)

    (tmp_path / "bumpwright.toml").write_text("[version]\nscheme='calver'\n")
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "2024.03.1"}}))
    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    monkeypatch.setattr(version_schemes, "date", FrozenDate)
    monkeypatch.chdir(tmp_path)
    out = apply_bump("minor", py, cfg=cfg)
    assert out.new == "2024.04.0"
    assert out.skipped == []


def test_apply_bump_invalid_scheme(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Invalid version schemes raise clear errors."""

    (tmp_path / "bumpwright.toml").write_text("[version]\nscheme='unknown'\n")
    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    cfg: Config = load_config(tmp_path / "bumpwright.toml")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="Unknown version scheme"):
        apply_bump("patch", py, cfg=cfg)


def test_resolve_files_nested_dirs_sorted(tmp_path: Path) -> None:
    """Resolve nested patterns and ensure results are deterministically ordered."""

    pkg = tmp_path / "pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)

    # Create files in non-sorted order to verify output sorting.
    paths = [
        pkg / "b.txt",
        pkg / "a.txt",
        sub / "d.txt",
        sub / "c.txt",
    ]
    for path in paths:
        path.write_text("", encoding="utf-8")

    out = _resolve_files(["pkg/**/*.txt"], [], tmp_path)
    expected = [
        pkg / "a.txt",
        pkg / "b.txt",
        sub / "c.txt",
        sub / "d.txt",
    ]
    assert out == expected


def test_resolve_files_absolute_paths_and_ignore_patterns(tmp_path: Path) -> None:
    """Handle absolute patterns and exclusion rules in file resolution."""

    base = tmp_path
    abs_file = base / "abs.py"
    abs_file.write_text("", encoding="utf-8")

    ignore_abs = base / "ignore_abs.py"
    ignore_abs.write_text("", encoding="utf-8")

    pkg = base / "pkg"
    pkg.mkdir()
    keep_rel = pkg / "keep.py"
    keep_rel.write_text("", encoding="utf-8")
    ignore_rel = pkg / "ignore_rel.py"
    ignore_rel.write_text("", encoding="utf-8")

    patterns = [str(abs_file), str(ignore_abs), "pkg/*.py"]
    ignore = [str(ignore_abs), "pkg/ignore_rel.py"]
    out = _resolve_files(patterns, ignore, base)
    expected = [abs_file, keep_rel]
    assert out == expected


def test_resolve_files_overlapping_patterns_deduped(tmp_path: Path) -> None:
    """Overlapping glob patterns yield unique, sorted results."""

    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("", encoding="utf-8")
    b.write_text("", encoding="utf-8")

    patterns = ["*.txt", "a.*", "b.*"]
    out = _resolve_files(patterns, [], tmp_path)

    assert out == [a, b]


def test_resolve_files_uses_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Ensure repeated resolution reuses cached results."""

    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    (tmp_path / "b.txt").write_text("2", encoding="utf-8")
    clear_version_file_cache()
    calls = {"count": 0}
    from bumpwright.versioning import glob as glob_orig  # noqa: PLC0415

    def fake_glob(pattern: str, recursive: bool = True) -> list[str]:
        calls["count"] += 1
        return glob_orig(pattern, recursive=recursive)

    monkeypatch.setattr("bumpwright.versioning.glob", fake_glob)
    _resolve_files(["*.txt"], [], tmp_path)
    _resolve_files(["*.txt"], [], tmp_path)
    assert calls["count"] == 1


def test_clear_version_file_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Manual cache clearing forces subsequent filesystem scans."""

    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    clear_version_file_cache()
    calls = {"count": 0}
    from bumpwright.versioning import glob as glob_orig  # noqa: PLC0415

    def fake_glob(pattern: str, recursive: bool = True) -> list[str]:
        calls["count"] += 1
        return glob_orig(pattern, recursive=recursive)

    monkeypatch.setattr("bumpwright.versioning.glob", fake_glob)
    _resolve_files(["*.txt"], [], tmp_path)
    clear_version_file_cache()
    _resolve_files(["*.txt"], [], tmp_path)
    assert calls["count"] == 2  # noqa: PLR2004


def test_resolve_files_cache_evicted_on_new_args(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The cache retains only the most recent resolution."""

    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    (tmp_path / "b.txt").write_text("2", encoding="utf-8")
    clear_version_file_cache()
    calls = {"count": 0}
    from bumpwright.versioning import glob as glob_orig  # noqa: PLC0415

    def fake_glob(pattern: str, recursive: bool = True) -> list[str]:
        calls["count"] += 1
        return glob_orig(pattern, recursive=recursive)

    monkeypatch.setattr("bumpwright.versioning.glob", fake_glob)
    _resolve_files(["a.txt"], [], tmp_path)
    _resolve_files(["b.txt"], [], tmp_path)
    _resolve_files(["a.txt"], [], tmp_path)
    assert calls["count"] == 3  # noqa: PLR2004


def test_apply_bump_reuses_resolve_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Repeated bumps with identical patterns reuse cached file resolution."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    cfg_file = tmp_path / "extra.cfg"
    cfg_file.write_text("version = '0.1.0'", encoding="utf-8")

    calls = {"count": 0}
    from bumpwright.versioning import glob as glob_orig  # noqa: PLC0415

    def fake_glob(pattern: str, recursive: bool = True) -> list[str]:
        calls["count"] += 1
        return glob_orig(pattern, recursive=recursive)

    monkeypatch.setattr("bumpwright.versioning.glob", fake_glob)
    apply_bump("patch", py, paths=["*.cfg"], config_path=tmp_path / "bumpwright.toml")
    apply_bump("patch", py, paths=["*.cfg"], config_path=tmp_path / "bumpwright.toml")
    assert calls["count"] == 1


@pytest.mark.parametrize("arg", ["paths", "ignore"])
def test_apply_bump_clears_cache_on_arg_change(
    arg: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Changing ``paths`` or ``ignore`` triggers new file resolution."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    a_cfg = tmp_path / "a.cfg"
    a_cfg.write_text("version = '0.1.0'", encoding="utf-8")
    b_cfg = tmp_path / "b.cfg"
    b_cfg.write_text("version = '0.1.0'", encoding="utf-8")

    cfg = load_config(tmp_path / "bumpwright.toml")
    calls = {"count": 0}
    from bumpwright.versioning import glob as glob_orig  # noqa: PLC0415

    def fake_glob(pattern: str, recursive: bool = True) -> list[str]:
        calls["count"] += 1
        return glob_orig(pattern, recursive=recursive)

    monkeypatch.setattr("bumpwright.versioning.glob", fake_glob)

    if arg == "paths":
        apply_bump("patch", py, paths=["a.cfg"], cfg=cfg)
        apply_bump("patch", py, paths=["b.cfg"], cfg=cfg)
        apply_bump("patch", py, paths=["a.cfg"], cfg=cfg)
    else:
        apply_bump("patch", py, paths=["*.cfg"], ignore=["b.cfg"], cfg=cfg)
        apply_bump("patch", py, paths=["*.cfg"], ignore=["a.cfg"], cfg=cfg)
        apply_bump("patch", py, paths=["*.cfg"], ignore=["b.cfg"], cfg=cfg)

    assert calls["count"] == 3  # noqa: PLR2004


def test_find_pyproject(tmp_path: Path) -> None:
    """Locate the nearest ``pyproject.toml`` when present."""

    root = tmp_path / "proj"
    root.mkdir()
    py = root / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    sub = root / "pkg"
    sub.mkdir()
    assert find_pyproject(sub) == py


def test_find_pyproject_missing(tmp_path: Path) -> None:
    """Return ``None`` when no ``pyproject.toml`` is found."""

    assert find_pyproject(tmp_path / "missing") is None


def test_write_project_version(tmp_path: Path) -> None:
    """Update the project version in ``pyproject.toml``."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({"project": {"version": "0.1.0"}}))
    write_project_version("0.2.0", py)
    data = toml_parse(py.read_text())
    assert data["project"]["version"] == "0.2.0"


def test_write_project_version_missing_project(tmp_path: Path) -> None:
    """Raise ``KeyError`` when the ``[project]`` table is absent."""

    py = tmp_path / "pyproject.toml"
    py.write_text(toml_dumps({}))
    with pytest.raises(KeyError):
        write_project_version("0.1.0", py)


def test_write_project_version_missing_file(tmp_path: Path) -> None:
    """Raise ``FileNotFoundError`` when ``pyproject.toml`` cannot be located."""

    missing = tmp_path / "missing" / "pyproject.toml"
    with pytest.raises(FileNotFoundError):
        write_project_version("0.1.0", missing)


def test_resolve_files_skips_non_files(tmp_path: Path) -> None:
    """Directories matched by patterns are ignored."""

    (tmp_path / "dir").mkdir()
    out = versioning._resolve_files(["dir"], [], tmp_path)
    assert out == []


def test_resolve_files_handles_outside_base(tmp_path: Path) -> None:
    """Files outside the base directory are retained with full paths."""

    outside = tmp_path.parent / "ext.txt"
    outside.write_text("x", encoding="utf-8")
    out = versioning._resolve_files([str(outside)], [], tmp_path)
    assert Path(str(outside)) in out
