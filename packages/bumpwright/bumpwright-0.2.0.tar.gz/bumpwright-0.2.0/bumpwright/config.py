"""Load and represent ``bumpwright`` configuration files."""

from __future__ import annotations

import copy
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .types import BumpLevel


@dataclass
class Rules:
    """Rules controlling version bump decisions.

    Attributes:
        return_type_change: Version bump level triggered when a public API
            return type changes.
        param_annotation_change: Version bump level for parameter annotation
            changes.
        implementation_change: Bump level when implementation of a public
            symbol changes without altering its signature. ``None`` disables
            this detection.
    """

    return_type_change: BumpLevel = "minor"
    param_annotation_change: BumpLevel = "patch"
    implementation_change: BumpLevel | None = "patch"

    def __post_init__(self) -> None:
        """Validate rule configuration.

        Raises:
            ValueError: If ``return_type_change`` is not ``"major"`` or
                ``"minor"``. ``param_annotation_change`` must be ``"major"``,
                ``"minor"``, or ``"patch"``.
        """

        if self.return_type_change not in {"major", "minor"}:
            raise ValueError("return_type_change must be 'major' or 'minor'")
        if self.param_annotation_change not in {"major", "minor", "patch"}:
            raise ValueError(
                "param_annotation_change must be 'major', 'minor', or 'patch'"
            )
        if self.implementation_change not in {"major", "minor", "patch", None}:
            raise ValueError(
                "implementation_change must be 'major', 'minor', 'patch', or None"
            )


@dataclass
class Project:
    """Project metadata and public API configuration.

    Attributes:
        package: Importable package containing the project's code. When empty the
            repository layout is used.
        public_roots: Paths whose contents constitute the public API.
        private_prefixes: Symbol name prefixes treated as private.
        extra_public_files: Additional glob patterns that trigger a patch bump
            when changed.
    """

    package: str = ""
    public_roots: list[str] = field(default_factory=lambda: ["."])
    private_prefixes: list[str] = field(default_factory=lambda: ["_"])
    extra_public_files: list[str] = field(
        default_factory=lambda: ["README.*", "docs/**/*.rst"]
    )


@dataclass
class Ignore:
    """Paths to ignore during scanning."""

    paths: list[str] = field(
        default_factory=lambda: ["tests/**", "examples/**", "scripts/**"]
    )


@dataclass
class Analysers:
    """Analyser plugin configuration.

    Attributes:
        enabled: Names of enabled analyser plugins.
    """

    enabled: set[str] = field(default_factory=set)


@dataclass
class Migrations:
    """Settings for the migrations analyser."""

    paths: list[str] = field(default_factory=lambda: ["migrations"])


@dataclass
class OpenAPI:
    """Settings for the OpenAPI analyser.

    Attributes:
        paths: File paths to OpenAPI specification documents.
    """

    paths: list[str] = field(
        default_factory=lambda: [
            "openapi.yaml",
            "openapi.yml",
            "openapi.json",
        ]
    )


@dataclass
class Changelog:
    """Changelog file configuration.

    Attributes:
        path: Default changelog file path. Empty string disables changelog generation.
        template: Jinja2 template file for changelog entries. Empty string selects
            the built-in template.
        exclude: Regular expression patterns for commit subjects to omit from
            changelog entries.
        repo_url: Base repository URL used for commit and compare links.
    """

    path: str = ""
    template: str = ""
    exclude: list[str] = field(default_factory=list)
    repo_url: str = ""


@dataclass
class VersionFiles:
    """Locations containing project version strings.

    Attributes:
        paths: Glob patterns to search for version declarations.
        ignore: Glob patterns to skip during version replacement.
        scheme: Versioning scheme identifier. Defaults to ``"semver"``.
    """

    paths: list[str] = field(
        default_factory=lambda: [
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "**/__init__.py",
            "**/version.py",
            "**/_version.py",
        ]
    )
    ignore: list[str] = field(
        default_factory=lambda: [
            "build/**",
            "dist/**",
            "*.egg-info/**",
            ".eggs/**",
            ".venv/**",
            "venv/**",
            ".env/**",
            "**/__pycache__/**",
        ]
    )

    scheme: str = "semver"


@dataclass
class Config:
    """Top-level configuration for bumpwright.

    Attributes:
        project: Project settings.
        rules: Rules controlling version bumps.
        ignore: Paths to exclude when scanning.
        analysers: Optional analyser plugin settings.
        changelog: Changelog file path and template defaults.
        version: Locations containing version strings.
    """

    project: Project = field(default_factory=Project)
    rules: Rules = field(default_factory=Rules)
    ignore: Ignore = field(default_factory=Ignore)
    analysers: Analysers = field(default_factory=Analysers)
    migrations: Migrations = field(default_factory=Migrations)
    openapi: OpenAPI = field(default_factory=OpenAPI)
    changelog: Changelog = field(default_factory=Changelog)
    version: VersionFiles = field(default_factory=VersionFiles)


def _merge_defaults(data: dict | None, defaults: dict) -> dict:
    """Merge user configuration with dataclass defaults.

    Args:
        data: Raw configuration mapping or ``None`` for no user overrides.
        defaults: Default configuration mapping generated from dataclasses.

    Returns:
        Combined configuration with defaults applied.
    """

    out = copy.deepcopy(defaults)  # Avoid mutating the defaults mapping
    for section, content in (data or {}).items():
        out.setdefault(section, {}).update(content or {})
    return out


def _validate_keys(data: dict, defaults: dict) -> None:
    """Ensure configuration keys are recognised.

    Args:
        data: Configuration mapping merged with defaults.
        defaults: Default configuration mapping generated from dataclasses.

    Raises:
        ValueError: If unknown sections or keys are present.
    """
    unexpected_sections = set(data) - set(defaults)
    if unexpected_sections:
        unknown = ", ".join(sorted(unexpected_sections))
        raise ValueError(f"Unknown configuration sections: {unknown}")

    for section, default_content in defaults.items():
        if section == "analysers" or not isinstance(default_content, dict):
            continue
        unexpected = set(data.get(section, {})) - set(default_content)
        if unexpected:
            unknown = ", ".join(sorted(unexpected))
            raise ValueError(f"Unknown keys in '{section}' section: {unknown}")


def load_config(path: str | Path = "bumpwright.toml") -> Config:
    """Load configuration from a TOML file.

    Args:
        path: Path to the configuration file.

    Returns:
        Parsed configuration object.

    Example:
        >>> cfg = load_config()
        >>> isinstance(cfg.project.public_roots, list)
        True
    """
    p = Path(path)
    raw: dict
    if not p.exists():
        raw = {}
    else:
        raw = tomllib.loads(p.read_text(encoding="utf-8"))
    defaults = asdict(Config())
    user_ignore = raw.get("version", {}).get("ignore")
    if user_ignore:
        raw.setdefault("version", {})["ignore"] = [
            *defaults["version"]["ignore"],
            *user_ignore,
        ]
    d = _merge_defaults(raw, defaults)
    _validate_keys(d, defaults)
    proj = Project(**d["project"])
    rules = Rules(**d["rules"])
    ign = Ignore(**d["ignore"])
    enabled = {name for name, enabled in d["analysers"].items() if enabled}
    analysers = Analysers(enabled=enabled)
    migrations = Migrations(**d.get("migrations", {}))
    openapi = OpenAPI(**d.get("openapi", {}))
    changelog = Changelog(**d.get("changelog", {}))
    version = VersionFiles(**d.get("version", {}))
    return Config(
        project=proj,
        rules=rules,
        ignore=ign,
        analysers=analysers,
        migrations=migrations,
        openapi=openapi,
        changelog=changelog,
        version=version,
    )
