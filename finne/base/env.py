"""Loads FINNE_BASE_PRIVATE_KEY and BASE_RPC_URL, from the real process
environment first, falling back to a .env file at the repository root
(see .env.example) for local development.

No dependency on python-dotenv is added — DECISION-023 fixes this
project's dependency list, and parsing two KEY=VALUE lines does not
need a library. This is the only .env reader in the repository —
finne/base/adapter.py is the only importer, including its own
deploy_contract() (the one-time deployment logic that used to live in
scripts/deploy_contract.py directly, moved here after independent
review found that script importing eth_account/web3 and signing
transactions itself, outside finne/base/) — keeping every reader of
raw key material under finne/base/, per PREREQ-003 section 6.

Persistence note, corrected after independent review: the key is never
written to Sibyl Memory, logged, or committed — but it IS necessarily
persisted locally in .env (gitignored, mode 0600, never committed) for
this to work at all without an interactive prompt every run. "Never
persisted anywhere" would overclaim; the accurate boundary is "never
persisted in Finné Memory's own records or in version control."
"""

from __future__ import annotations

import os
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


def _read_dotenv_file() -> dict[str, str]:
    if not _ENV_FILE.exists():
        return {}
    values: dict[str, str] = {}
    for line in _ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def get_env_var(name: str) -> str:
    """Real environment variables take precedence over .env, which is
    only a local-development fallback. Raises RuntimeError with an
    actionable message if the variable is set nowhere — never returns
    an empty string or None for a caller to silently misuse."""
    value = os.environ.get(name)
    if value:
        return value
    value = _read_dotenv_file().get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Set it in the environment or in a .env "
            "file at the repository root (see .env.example)."
        )
    return value
