# bumpwright

![Coverage](https://lewis-morris.github.io/bumpwright/_static/badges/coverage.svg)
![Version](https://lewis-morris.github.io/bumpwright/_static/badges/version.svg)
![Python Versions](https://lewis-morris.github.io/bumpwright/_static/badges/python.svg)
![License](https://lewis-morris.github.io/bumpwright/_static/badges/license.svg)

Bumpwright is an automated semantic versioning tool. It analyzes code changes instead of relying on commit messages to suggest the right next version.

It compares your latest code against the last release with a single command. The tool tells you whether to bump the version by a patch, minor, or major, making accurate releases effortless for maintainers of libraries and services with stable interfaces.

**Docs:** https://lewis-morris.github.io/bumpwright/
**Guides:** https://lewis-morris.github.io/bumpwright/guides/

## Overview

### What & Why

Traditional release tools rely on commit messages, which can be inconsistent. Bumpwright inspects your project’s public API directly to decide the next version. This catches breaking changes even if commit messages miss them and can update version strings and generate changelog entries automatically, streamlining releases.

### How It Works

Bumpwright compares two Git references—usually the last release tag and the current commit—and detects changes in the public interface. Removed functions or changed signatures trigger a major bump; new features result in a minor bump; and bug fixes or small tweaks lead to a patch bump. Static analysis and optional analysers (for CLI commands, web routes, migrations, and more) drive these decisions. You can apply the suggestion, update files, and render changelog notes.

### Key Benefits

- **Simplicity** – run a single command to see how your API changed.
- **Accuracy** – catches breaking changes that commit messages may miss.
- **Flexibility** – configurable analysers and settings to fit your workflow.
- **Automation** – update version files and generate changelog entries.

### Trade-offs / Constraints

- **Baseline required** – needs a baseline reference (e.g., prior release tag); run `bumpwright init` to mark it.
- **Static analysis limits** – cannot account for runtime-specific changes or internal logic.
- **Python 3.11+** – focuses on Python projects and requires Python 3.11 or newer.

Get started with the [Quickstart guide](https://lewis-morris.github.io/bumpwright/quickstart.html).

---

## Install

```bash
pip install bumpwright  # Python 3.11+
```

Bumpwright now uses Python's built-in `tomllib`, removing the need for the
external `tomli` dependency.

Full details: [Installation](https://lewis-morris.github.io/bumpwright/quickstart.html#installation)

---

## TL;DR (90 seconds)

```bash
# 1) Create a baseline release commit once
bumpwright init

# 2) Ask Bumpwright what the next version should be
bumpwright decide

# 3) Apply it, update files, commit and tag
bumpwright bump --commit --tag
```

What the decision means and examples: [Quickstart](https://lewis-morris.github.io/bumpwright/quickstart.html) • Command flags: [Usage → bump](https://lewis-morris.github.io/bumpwright/usage/bump.html)

| Command | Purpose |
|---------|---------|
| [`bumpwright init`](https://lewis-morris.github.io/bumpwright/usage/init.html) | Create a baseline release commit. |
| [`bumpwright bump`](https://lewis-morris.github.io/bumpwright/usage/bump.html) | Determine and apply the next version. |
| [`bumpwright history`](https://lewis-morris.github.io/bumpwright/usage/history.html) | View past releases in text, Markdown, or JSON and roll back a tag. |

---

## Configuration (minimal)

Bumpwright reads `bumpwright.toml` (you can change with `--config`). Defaults are sensible; start small and opt-in extras as needed.

```toml
# bumpwright.toml
[project]
public_roots = ["."]
# modifying modules here triggers at least a patch bump
private_prefixes = ["_"]  # names starting with "_" are ignored as private

[analysers]
cli = true         # set true to enable
grpc = false
web_routes = false
migrations = false
openapi = false
graphql = false

[changelog]
# path = "CHANGELOG.md"   # optional default target for --changelog
repo_url = "https://github.com/me/project"  # link commits and compares

[version]
scheme = "semver"   # "semver" | "calver"
# paths / ignore have robust defaults
```

All options and defaults: [Configuration](https://lewis-morris.github.io/bumpwright/configuration.html) • Versioning schemes: [Versioning](https://lewis-morris.github.io/bumpwright/versioning.html)

---

## Output & Changelog

- Choose output with `--format text|md|json` for human/CI consumption.
- Generate release notes with a Jinja2 template via `--changelog` (and `--repo-url` or `[changelog].repo_url` for compare/commit links).

Template context includes: `version`, `date`, `release_datetime_iso`, `commits[sha,subject,link]`, `previous_tag`, `compare_url`, `contributors[name,link]`, `breaking_changes`, `repo_url`.

Learn more & ready-to-copy templates:  
- [Changelog → Template variables](https://lewis-morris.github.io/bumpwright/changelog/template.html)  
- [Changelog → Examples](https://lewis-morris.github.io/bumpwright/changelog/examples.html)

---

## Analysers (opt-in)

Enable what you need in `[analysers]` or per-run with `--enable-analyser/--disable-analyser`.

- **Python API (default)** – respects `__all__`; otherwise public = names not starting with `_`.  
- **CLI** – detects changes to argparse/Click commands.  
- **gRPC** – service and method diffs.
- **Web routes** – Flask/FastAPI route changes.  
- **Migrations** – Alembic schema impacts.  
- **OpenAPI** – spec diffs.  
- **GraphQL** – schema diffs.

Overview & per-analyser docs: [Analysers](https://lewis-morris.github.io/bumpwright/analysers/)

---

## GitHub Actions (CI)

Common workflows are prebuilt:

- **Auto-bump on push** (commit + tag + append changelog)  
- **PR check** (report decision only)  
- **Manual release** (on dispatch)

Copy/paste from: [CI/CD (GitHub Actions)](https://lewis-morris.github.io/bumpwright/recipes/github-actions.html)

---

## Contributing & Roadmap

Issues and PRs welcome. See [Contributing](https://lewis-morris.github.io/bumpwright/contributing.html) and planned work in the [Roadmap](https://lewis-morris.github.io/bumpwright/roadmap.html).

**License:** [MIT](./LICENSE)
