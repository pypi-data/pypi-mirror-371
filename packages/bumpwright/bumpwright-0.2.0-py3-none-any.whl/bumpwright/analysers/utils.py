"""Shared helpers for analyser modules."""

from __future__ import annotations

import ast
import logging
from collections.abc import Iterable, Iterator
from functools import lru_cache

from ..gitutils import list_py_files_at_ref, read_file_at_ref, read_files_at_ref

logger = logging.getLogger(__name__)


def _is_const_str(node: ast.AST) -> bool:
    """Return whether ``node`` is an ``ast.Constant`` string.

    Args:
        node: AST node to inspect.

    Returns:
        ``True`` if ``node`` represents a constant string literal.
    """

    return isinstance(node, ast.Constant) and isinstance(node.value, str)


@lru_cache(maxsize=None)
def parse_python_source(ref: str, path: str, cwd: str | None = None) -> ast.AST | None:
    """Return the parsed AST for ``path`` at ``ref``.

    Results are cached per ``(ref, path, cwd)`` to avoid repeated git
    lookups and ``ast.parse`` calls when analysers inspect the same files
    multiple times. Invalid or unreadable files are skipped.

    Args:
        ref: Git reference of the file to parse.
        path: File path relative to the repository root.
        cwd: Repository path. Defaults to the current working directory.

    Returns:
        Parsed module AST or ``None`` if the file does not exist or is
        invalid at ``ref``.

    Example:
        >>> tree = parse_python_source('HEAD', 'bumpwright/__init__.py')
        >>> isinstance(tree, ast.AST)
        True
    """

    code = read_file_at_ref(ref, path, cwd=cwd)
    if code is None:
        return None
    try:
        return ast.parse(code)
    except (SyntaxError, UnicodeDecodeError):
        logger.warning("Failed to parse %s at %s", path, ref)
        return None


def iter_py_files_at_ref(
    ref: str,
    roots: Iterable[str],
    ignore_globs: Iterable[str] | None = None,
    cwd: str | None = None,
) -> Iterator[tuple[str, str]]:
    """Yield Python file paths and contents for a git reference.

    Args:
        ref: Git reference to inspect.
        roots: Root directories to search for Python modules.
        ignore_globs: Optional glob patterns to exclude.
        cwd: Repository path in which to run git commands.

    Yields:
        Tuples of ``(path, source)`` for each discovered Python file. Paths
        are sorted to ensure deterministic iteration order.

    Example:
        >>> next(iter_py_files_at_ref('HEAD', ['bumpwright']))[0].endswith('.py')
        True
    """

    paths = sorted(list_py_files_at_ref(ref, roots, ignore_globs=ignore_globs, cwd=cwd))
    contents = read_files_at_ref(ref, paths, cwd=cwd)
    for path in paths:
        code = contents.get(path)
        if code is not None:
            yield path, code


def clear_caches() -> None:
    """Clear caches used by analyser utilities."""

    parse_python_source.cache_clear()
    list_py_files_at_ref.cache_clear()
    read_file_at_ref.cache_clear()
