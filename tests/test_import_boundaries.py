"""Enforces PREREQ-003's module boundaries via static AST inspection of
the actual application source, not just documentation or code review.

Written after independent review found scripts/deploy_contract.py
importing eth_account and web3 directly and signing/broadcasting
transactions itself — a real violation of PREREQ-003 section 6 ("only
finne/base/adapter.py holds key material or reaches the network") that
existed in application code with nothing automated to catch it. Scans
finne/ and scripts/ only, not tests/: test code legitimately references
web3/eth_account types (e.g. web3.exceptions.ContractLogicError) for
assertions and mocking, which is not the concern this boundary protects
against — only application code holding real key material is.

Covers: module constraints, invariant 9.
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_SIBYL_MEMORY_ALLOWED = {"finne/memory/client.py"}
_KEY_MATERIAL_ALLOWED_PREFIX = "finne/base/"
_KEY_MATERIAL_MODULES = {"eth_account", "web3"}


def _imported_top_level_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def _application_python_files() -> list[Path]:
    files: list[Path] = []
    for directory in ("finne", "scripts"):
        files.extend((REPO_ROOT / directory).rglob("*.py"))
    return files


def test_only_memory_client_imports_sibyl_memory_client():
    violations = []
    for path in _application_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in _SIBYL_MEMORY_ALLOWED:
            continue
        if "sibyl_memory_client" in _imported_top_level_modules(path):
            violations.append(rel)
    assert not violations, f"sibyl_memory_client imported outside finne/memory/client.py: {violations}"


def test_only_finne_base_imports_key_material_libraries():
    violations = []
    for path in _application_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith(_KEY_MATERIAL_ALLOWED_PREFIX):
            continue
        modules = _imported_top_level_modules(path)
        hit = modules & _KEY_MATERIAL_MODULES
        if hit:
            violations.append((rel, sorted(hit)))
    assert not violations, f"eth_account/web3 imported outside finne/base/: {violations}"
