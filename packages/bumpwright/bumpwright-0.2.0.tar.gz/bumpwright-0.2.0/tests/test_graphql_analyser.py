from __future__ import annotations

import os

from bumpwright import gitutils
from bumpwright.analysers.graphql_schema import (
    GraphQLAnalyser,
    TypeDef,
    _build_schema_at_ref,
    _list_graphql_files_at_ref,
    diff_types,
    extract_types_from_schema,
)
from bumpwright.config import Config


def _build(sdl: str) -> dict[str, TypeDef]:
    """Parse SDL into type definitions."""

    return extract_types_from_schema(sdl)


def test_removed_type_is_major() -> None:
    """Removing a type should trigger a major impact."""

    old = _build("type User { id: ID! }")
    new: dict[str, TypeDef] = {}
    impacts = diff_types(old, new)
    assert any(i.severity == "major" and i.symbol == "User" for i in impacts)


def test_added_type_is_minor() -> None:
    """Adding a type should trigger a minor impact."""

    old: dict[str, TypeDef] = {}
    new = _build("type User { id: ID! }")
    impacts = diff_types(old, new)
    assert any(i.severity == "minor" and i.symbol == "User" for i in impacts)


def test_added_field_is_minor() -> None:
    """Adding a field is a minor change."""

    old = _build("type User { id: ID! }")
    new = _build("type User { id: ID!, name: String }")
    impacts = diff_types(old, new)
    assert any(i.severity == "minor" and i.symbol == "User.name" for i in impacts)


def test_removed_field_is_major() -> None:
    """Removing a field is a major change."""

    old = _build("type User { id: ID!, name: String }")
    new = _build("type User { id: ID! }")
    impacts = diff_types(old, new)
    assert any(i.severity == "major" and i.symbol == "User.name" for i in impacts)


def test_extract_special_definitions() -> None:
    """Enums, unions, and scalars have no fields."""

    sdl = (
        "enum Role { USER ADMIN }\n"
        "union SearchResult = User | Post\n"
        "scalar DateTime\n"
    )
    types = extract_types_from_schema(sdl)
    assert types["Role"].fields == frozenset()
    assert types["SearchResult"].fields == frozenset()
    assert types["DateTime"].fields == frozenset()


def test_graphql_file_listing_and_analyser(tmp_path) -> None:
    """_list_graphql_files_at_ref and GraphQLAnalyser cover git integration."""

    repo = tmp_path / "repo"
    schema = repo / "schema"
    schema.mkdir(parents=True)
    (schema / "include.graphql").write_text("type Query { hello: String }\n")
    (schema / "ignore.graphql").write_text("type Foo { id: ID }\n")
    other = repo / "other.graphql"
    other.write_text("type Other { id: ID }\n")
    (repo / "README.txt").write_text("readme\n")
    gitutils._run(["git", "init"], str(repo))
    gitutils._run(["git", "config", "user.email", "test@example.com"], str(repo))
    gitutils._run(["git", "config", "user.name", "Test"], str(repo))
    gitutils._run(["git", "add", "."], str(repo))
    gitutils._run(["git", "commit", "-m", "init"], str(repo))

    files = _list_graphql_files_at_ref(
        "HEAD", ["schema"], ["schema/ignore.graphql"], str(repo)
    )
    assert files == {"schema/include.graphql"}

    built = _build_schema_at_ref(
        "HEAD", ["schema"], ["schema/ignore.graphql"], str(repo)
    )
    assert "Query" in built

    cfg = Config()
    cfg.ignore.paths = []
    cfg.project.public_roots = ["schema"]
    analyser = GraphQLAnalyser(cfg)

    old = os.getcwd()
    os.chdir(repo)
    try:
        collected = analyser.collect("HEAD")
    finally:
        os.chdir(old)
    assert "Query" in collected

    impacts = analyser.compare(
        {"User": TypeDef("User", frozenset({"id"}))},
        {"User": TypeDef("User", frozenset({"id", "name"}))},
    )
    assert any(i.symbol == "User.name" for i in impacts)
