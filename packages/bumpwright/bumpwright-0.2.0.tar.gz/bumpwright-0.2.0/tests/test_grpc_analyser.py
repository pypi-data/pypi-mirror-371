"""Tests for the gRPC analyser."""

import os

from bumpwright import gitutils
from bumpwright.analysers.grpc import (
    GrpcAnalyser,
    Service,
    _build_services_at_ref,
    diff_services,
    extract_services_from_proto,
    list_proto_files_at_ref,
)
from bumpwright.config import Config


def _build(src: str) -> dict[str, Service]:
    """Parse proto source into a service mapping."""
    return extract_services_from_proto(src)


def test_removed_service_is_major() -> None:
    """Removing a service triggers a major impact."""
    old = _build(
        """
        service Foo {
            rpc Ping (Req) returns (Res);
        }
        """
    )
    new: dict[str, Service] = {}
    impacts = diff_services(old, new)
    assert any(i.severity == "major" for i in impacts)


def test_added_service_is_minor() -> None:
    """Adding a service triggers a minor impact."""
    old: dict[str, Service] = {}
    new = _build(
        """
        service Foo {
            rpc Ping (Req) returns (Res);
        }
        """
    )
    impacts = diff_services(old, new)
    assert any(i.severity == "minor" for i in impacts)


def test_removed_method_is_major() -> None:
    """Removing a method from a service is a major impact."""
    old = _build(
        """
        service Foo {
            rpc Ping (Req) returns (Res);
            rpc Pong (Req) returns (Res);
        }
        """
    )
    new = _build(
        """
        service Foo {
            rpc Ping (Req) returns (Res);
        }
        """
    )
    impacts = diff_services(old, new)
    assert any(i.severity == "major" and i.symbol == "Foo.Pong" for i in impacts)


def test_added_method_is_minor() -> None:
    """Adding a method to a service is a minor impact."""
    old = _build(
        """
        service Foo {
            rpc Ping (Req) returns (Res);
        }
        """
    )
    new = _build(
        """
        service Foo {
            rpc Ping (Req) returns (Res);
            rpc Pong (Req) returns (Res);
        }
        """
    )
    impacts = diff_services(old, new)
    assert any(i.severity == "minor" and i.symbol == "Foo.Pong" for i in impacts)


def test_proto_file_listing_and_analyser(tmp_path) -> None:
    """Verify git-backed proto discovery and analyser logic."""

    repo = tmp_path / "repo"
    api = repo / "apis"
    api.mkdir(parents=True)
    (api / "svc.proto").write_text(
        "service Greeter { rpc Hello (Req) returns (Res); }\n"
    )
    (api / "ignore.proto").write_text(
        "service Ignored { rpc Ping (Req) returns (Res); }\n"
    )
    other = repo / "other.proto"
    other.write_text("service Other { rpc Ping (Req) returns (Res); }\n")
    (repo / "README.txt").write_text("readme\n")
    gitutils._run(["git", "init"], str(repo))
    gitutils._run(["git", "config", "user.email", "test@example.com"], str(repo))
    gitutils._run(["git", "config", "user.name", "Test"], str(repo))
    gitutils._run(["git", "add", "."], str(repo))
    gitutils._run(["git", "commit", "-m", "init"], str(repo))

    cfg = Config()
    cfg.ignore.paths = []
    cfg.project.public_roots = ["apis"]
    analyser = GrpcAnalyser(cfg)
    old = os.getcwd()
    os.chdir(repo)
    try:
        paths = list_proto_files_at_ref("HEAD", ["apis"], ["apis/ignore.proto"])
        assert paths == {"apis/svc.proto"}
        built = _build_services_at_ref("HEAD", ["apis"], ["apis/ignore.proto"])
        assert "Greeter" in built
        collected = analyser.collect("HEAD")
    finally:
        os.chdir(old)

    assert "Greeter" in collected
    impacts = analyser.compare(
        {"Svc": Service("Svc", {"A"})},
        {"Svc": Service("Svc", {"A", "B"})},
    )
    assert any(i.symbol == "Svc.B" for i in impacts)
