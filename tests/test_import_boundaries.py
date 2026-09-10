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
# PREREQ-003 section 17 as amended by DECISION-027: the model-call
# permission moved from finne/explain.py — which never exercised it and
# remains deterministic — to finne/agent.py, the proposing agent.
_MODEL_SDK_ALLOWED = "finne/agent.py"
_MODEL_SDK_MODULES = {"anthropic", "openai"}


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


def _dotted_package_of(path: Path) -> str:
    """The package a file lives in, e.g. `finne.base` for
    finne/base/adapter.py — needed to resolve its relative imports."""
    return path.relative_to(REPO_ROOT).parent.as_posix().replace("/", ".")


def _resolve_relative(package: str, module: str | None, level: int) -> str:
    """`from ..x import y` inside finne.base -> `finne.x`. Mirrors
    Python's own resolution: level 1 is the current package, each
    further dot strips one more."""
    parts = package.split(".") if package else []
    if level - 1 > 0:
        parts = parts[: -(level - 1)] or []
    base = ".".join(parts)
    if module:
        return f"{base}.{module}" if base else module
    return base


def _imported_finne_submodules(path: Path) -> set[str]:
    """Every `finne.*` module this file imports, by dotted name.

    Resolves BOTH absolute (`from finne.base import adapter`) and
    relative (`from . import adapter`, `from .adapter import x`) forms.
    Relative imports were a real blind spot found by independent review:
    for `from .adapter import x`, `node.module` is `"adapter"`, which
    does not start with `"finne"`, so the boundary was silently
    unchecked."""
    tree = ast.parse(path.read_text(), filename=str(path))
    package = _dotted_package_of(path)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "finne" or alias.name.startswith("finne."):
                    modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_relative(package, node.module, node.level)
            if not (base == "finne" or base.startswith("finne.")):
                continue
            modules.add(base)
            # `from finne.base import adapter`: the imported NAME may
            # itself be a submodule, which is the form that actually
            # crosses the boundary.
            for alias in node.names:
                modules.add(f"{base}.{alias.name}")
    return modules


def _module_files(dotted: str) -> list[str]:
    """Resolve a dotted module name to EVERY file it could denote — the
    package `finne/base/__init__.py` and the module `finne/base.py`.

    Resolving only the module was a real blind spot (every finne package
    has an `__init__.py`, so `import finne.base` resolved to nothing and
    was never followed). Resolving only the first match is a smaller one
    in the other direction: Python prefers the package, so picking
    `x.py` when both exist would follow the file Python does NOT import.
    Following both is strictly safer than choosing — for a boundary
    check, an extra edge can only over-report, never miss."""
    stem = dotted.replace(".", "/")
    return [
        candidate
        for candidate in (f"{stem}/__init__.py", f"{stem}.py")
        if (REPO_ROOT / candidate).exists()
    ]


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


def test_only_explain_imports_a_model_sdk():
    """PREREQ-003 section 13: `finne/explain.py` is the only module
    permitted to call a model. Nothing else may import an AI SDK."""
    violations = []
    for path in _application_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel == _MODEL_SDK_ALLOWED:
            continue
        hit = _imported_top_level_modules(path) & _MODEL_SDK_MODULES
        if hit:
            violations.append((rel, sorted(hit)))
    assert not violations, f"an AI SDK is imported outside {_MODEL_SDK_ALLOWED}: {violations}"


def _reachable_finne_files(entry: str) -> set[str]:
    """Transitive closure of finne/* files reachable from `entry`."""
    reachable: set[str] = set()
    frontier = [entry]
    while frontier:
        rel = frontier.pop()
        if rel in reachable:
            continue
        reachable.add(rel)
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        for module in _imported_finne_submodules(path):
            frontier.extend(_module_files(module))
    return reachable


def test_agent_has_no_import_path_to_finne_base():
    """SPEC-002 section 6: a model may never sign, submit, or construct
    a transaction. `finne/agent.py` is the only module that calls a
    model, so it is the one that must not be able to reach the signing
    key. Transitive, for the same reason as the explain check below."""
    breaches = sorted(
        rel for rel in _reachable_finne_files("finne/agent.py")
        if rel.startswith("finne/base/")
    )
    assert not breaches, f"finne/agent.py can reach finne/base/ via: {breaches}"


def test_agent_cannot_reach_authority_memory_or_policy():
    """SPEC-002 invariant 11: the agent is never given the owner
    ceiling, any precedent, or any authority value. The `Opportunity`
    type carries no such field, but a type alone would not stop the
    module importing `finne.policy` and reading the ceiling directly —
    so the reachability is forbidden outright.

    This is the invariant that makes the demonstration honest: the
    bound comes from Finné Memory, not from the agent's restraint."""
    forbidden = ("finne/authority/", "finne/memory/", "finne/policy.py")
    reachable = _reachable_finne_files("finne/agent.py")
    breaches = sorted(
        rel for rel in reachable if any(rel.startswith(f) for f in forbidden)
    )
    assert not breaches, (
        f"finne/agent.py can reach authority/memory/policy via: {breaches} — "
        "the agent must not be able to see what it is permitted to do"
    )


def test_opportunity_carries_no_authority_field():
    """SPEC-002 invariant 11, at the type level: whatever else changes,
    the agent's input must not grow a ceiling, a precedent, or an
    authority value."""
    import dataclasses

    from finne.agent import Opportunity

    fields = {f.name for f in dataclasses.fields(Opportunity)}
    forbidden = {
        "max_amount", "ceiling", "owner_policy", "policy", "precedent",
        "precedents", "authority", "authorized_amount", "learned_max_amount",
        "cold_start_autonomous_amount", "candidates",
    }
    leaked = fields & forbidden
    assert not leaked, f"Opportunity exposes authority information to the agent: {leaked}"


def test_explain_has_no_import_path_to_finne_base():
    """PREREQ-003 section 10: `finne/explain.py` has no import path to
    `finne/base/` — it retains no model-call permission but is still
    presentation adjacent to a decision, and the boundary is kept.
    Checks the transitive closure, not just the direct imports, since
    an indirect path would breach the boundary just as effectively.

    Static by construction, so it sees imports inside function bodies
    and behind `if` branches (any `ast.Import` node counts, wherever it
    sits) and terminates via the visited set. What static analysis
    CANNOT see is a name assembled at runtime — which is why
    `test_application_code_uses_no_dynamic_imports` below forbids that
    escape hatch outright rather than leaving the closure quietly
    incomplete."""
    breaches = sorted(
        rel for rel in _reachable_finne_files("finne/explain.py")
        if rel.startswith("finne/base/")
    )
    assert not breaches, f"finne/explain.py can reach finne/base/ via: {breaches}"


def test_application_code_uses_no_dynamic_imports():
    """Every boundary test in this file is static: it reads import
    statements out of the AST. `importlib.import_module("finne.base." +
    name)` imports a module without producing an import statement, and
    would pass every check above while breaching the boundary.

    Rather than attempt to analyse dynamic imports — which cannot be
    done soundly — application code is forbidden from using them. The
    prohibition covers the ways of REACHING the machinery, not just
    calling it: independent review evaded a call-only check with
    `f = __import__; f("finne.base")` and with
    `getattr(builtins, "__import__")`. So any mention of the name, any
    reflective lookup of a string containing "import", and the
    arbitrary-execution builtins that could rebuild it all count.

    This is DEFENCE IN DEPTH, not a proof. A determined evasion —
    aliasing `getattr`, assembling "__import__" from fragments — stays
    invisible to any static check, and claiming otherwise would be the
    same overclaim these reviews keep catching elsewhere. What it does
    reliably catch is the accidental violation: someone reaching for
    `importlib` because it seemed convenient. Human and independent
    review remain the final enforcement layer for the deliberate case.

    Nothing in finne/ or scripts/ needs any of them. (Until round 4 of
    the seam (e) review, `finne/explain.py` carried a lazy
    `import anthropic` inside a function body — statically visible, and
    seen by the AST walk above. That import is gone with the model call
    itself; the boundary rule stays, so a future reinstatement is caught
    rather than assumed.)
    """
    forbidden_names = {"__import__", "eval", "exec", "compile"}
    forbidden_attrs = {"__import__", "import_module", "__loader__", "find_spec"}
    violations = []
    for path in _application_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                names = [module] if module else [a.name for a in getattr(node, "names", [])]
                if any((n or "").split(".")[0] in {"importlib", "builtins"} for n in names):
                    violations.append((rel, node.lineno, "importlib/builtins import"))
            elif isinstance(node, ast.Name) and node.id in forbidden_names:
                # Covers `f = __import__` as well as `__import__(...)`:
                # the name is flagged wherever it appears, in any context.
                violations.append((rel, node.lineno, node.id))
            elif isinstance(node, ast.Attribute) and node.attr in forbidden_attrs:
                violations.append((rel, node.lineno, f".{node.attr}"))
            elif isinstance(node, ast.Call):
                func = node.func
                is_getattr = isinstance(func, ast.Name) and func.id in {"getattr", "vars"}
                if is_getattr:
                    for arg in node.args[1:]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            if "import" in arg.value or "loader" in arg.value:
                                violations.append((rel, node.lineno, f"getattr {arg.value!r}"))
    assert not violations, (
        "dynamic imports evade every static boundary check in this file: "
        f"{violations}"
    )
