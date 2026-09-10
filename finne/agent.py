"""The assessing agent — the only module in this repository that calls a
model, per PREREQ-003 section 17 as amended by DECISION-027.

It is given a claim and the loss adjuster's assessed value. It is NOT
given the delegated settlement ceiling, any precedent, or any authority value, and it
has no way to reach them: this module imports nothing from
finne.authority, finne.memory, finne.policy, or finne.base, and
tests/test_import_boundaries.py enforces that over the transitive
closure rather than the direct imports alone.

The model proposes. It never authorizes, widens, signs, or submits.

Why this is safe when the seam (e) model removal was not
--------------------------------------------------------
Seam (e) removed a model from finne/explain.py after four independent
review rounds each found a new way for model-written prose to state
something FALSE beside a correct decision. That finding does not
transfer here, and the difference is the whole reason DECISION-027
could reverse part of that removal:

  - There, the model made ASSERTIONS ABOUT A DECISION. An assertion can
    be false, and validating "is this sentence true of this decision"
    defeated three separate attempts.
  - Here, the model states WHAT IT WANTS. A proposal cannot be false —
    it can only be unreasonable, and an unreasonable proposal is the
    input this product exists to constrain. If the model asks for
    40,000 against a 25,000 ceiling, the engine blocks it and the demo
    is better for it.

Untrusted output
----------------
The response is data, never instruction. Text inside it is never
executed, never used to select a code path, and never displayed as
authority. It is parsed into a Proposal, whose own __post_init__ then
rejects anything malformed — so a hostile or broken response fails
closed at the type boundary, before any other module sees it.

There is deliberately no repair, no retry with a relaxed schema, and no
fallback to a hardcoded proposal. A silent fallback would make the
demonstration appear to work while proving nothing about the agent.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import requests

from finne.models import Proposal, RiskTier, ValidationError

_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_MODEL = "anthropic/claude-opus-5"
_TIMEOUT_SECONDS = 60
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class AgentUnavailableError(Exception):
    """The model could not be reached, or refused to answer.

    Distinct from AgentResponseError: nothing was proposed because no
    usable response arrived at all. Never downgraded to a default
    proposal — see the module docstring.
    """


class AgentResponseError(Exception):
    """A response arrived but is not a usable proposal — unparseable
    JSON, a missing field, or a value the Proposal type rejects."""


@dataclass(frozen=True)
class CaseUnderAssessment:
    """What the assessing agent is told: the claim, and the loss
    adjuster's figure for it.

    Note what is absent and stays absent: there is no delegated
    settlement ceiling, no prior decision, no authority state, and no
    learned constraint. The agent cannot reason about limits it has
    never been shown, which is what makes the demonstration honest —
    the bound comes from the institution's own record of how it has
    decided before, not from the agent's restraint.
    """

    summary: str
    assessed_value: Decimal
    network: str
    asset: str
    action_class: str
    target_class: str
    function: str


_SYSTEM_PROMPT = (
    "You are a claims assessor at a general insurer. You are shown one "
    "claim and the loss adjuster's assessed value for it, and you decide "
    "what settlement to propose.\n\n"
    "Decide two things: the settlement amount to propose, and how you rate "
    "the risk profile of this claim — `low` for a straightforward claim with "
    "clear causation and supporting evidence, `medium` or `high` where "
    "causation, evidence, or the policyholder's history give you pause.\n\n"
    "Propose the settlement the claim actually merits on the evidence "
    "described. Your proposal is reviewed against the institution's own "
    "prior decisions before anything is issued to the policyholder. Do not "
    "try to guess what that review will permit, and do not hedge low to seem "
    "cautious — assess the claim."
)


def _read_env_var(name: str) -> str:
    """Real environment first, then a .env file at the repository root.

    Deliberately a local copy of the pattern in finne/base/env.py rather
    than an import of it: this module may not import finne.base at all
    (SPEC-002 section 6), because that package is where the Base signing
    key lives. Fifteen duplicated lines is the price of a boundary that
    a test can actually enforce.
    """
    value = os.environ.get(name)
    if value:
        return value
    if _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw = line.partition("=")
            if key.strip() == name:
                candidate = raw.strip().strip('"').strip("'")
                if candidate:
                    return candidate
    raise RuntimeError(
        f"{name} is not set. Set it in the environment or in a .env file at "
        "the repository root (see .env.example). The model-backed agent "
        "requires it; the default --agent=fixed path does not."
    )


def _proposal_schema(case: CaseUnderAssessment) -> dict[str, Any]:
    """A strict JSON schema for the response.

    The fact dimensions are pinned to the opportunity's own values —
    single-member enums — because they describe WHICH opportunity this
    is, not what the agent decides about it. What the agent genuinely
    decides is `amount` and `counterparty_risk_tier`, and those are the
    two fields left open.

    `amount` is a string, not a number: JSON numbers are IEEE floats,
    and this project prohibits float arithmetic anywhere in the
    authority path. A string crosses the boundary exactly, and
    Decimal() parses it exactly.
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "network", "asset", "action_class", "target_class",
            "function", "counterparty_risk_tier", "amount", "reasoning",
        ],
        "properties": {
            "network": {"type": "string", "enum": [case.network]},
            "asset": {"type": "string", "enum": [case.asset]},
            "action_class": {"type": "string", "enum": [case.action_class]},
            "target_class": {"type": "string", "enum": [case.target_class]},
            "function": {"type": "string", "enum": [case.function]},
            "counterparty_risk_tier": {
                "type": "string",
                "enum": [tier.value for tier in RiskTier],
            },
            "amount": {
                "type": "string",
                "description": (
                    "Settlement amount to propose, as a decimal string with exactly "
                    "two decimal places — format example only, carries no "
                    "suggestion about size: \"1234.56\". Not a JSON number."
                ),
            },
            "reasoning": {
                "type": "string",
                "description": "One sentence on why this settlement figure.",
            },
        },
    }


def _build_request(case: CaseUnderAssessment, model: str) -> dict[str, Any]:
    user_message = (
        f"Claim: {case.summary}\n"
        f"Channel: {case.network}\n"
        f"Settlement currency: {case.asset}\n"
        f"Assessment type: {case.action_class}\n"
        f"Peril: {case.target_class}\n"
        f"Decision under consideration: {case.function}\n"
        f"Loss adjuster's assessed value: {case.assessed_value} {case.asset}\n\n"
        "Propose your settlement."
    )
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "claim_settlement_proposal",
                "strict": True,
                "schema": _proposal_schema(case),
            },
        },
        # NOT optional. OpenRouter serves the same model through several
        # providers and its own documentation states that enforcement
        # varies — some guarantee schema-conforming output, others
        # "treat it as a strong hint". Without this flag a run can be
        # routed to a provider that returns prose, which on a recorded
        # demonstration is a failure with no recovery.
        "provider": {"require_parameters": True},
    }


def _extract_content(body: dict[str, Any]) -> str:
    try:
        choices = body["choices"]
        if not choices:
            raise AgentResponseError("model returned no choices")
        content = choices[0]["message"]["content"]
    except (KeyError, TypeError, IndexError) as exc:
        raise AgentResponseError(
            f"unexpected response envelope from the model provider: {exc}"
        ) from exc
    if not isinstance(content, str) or not content.strip():
        raise AgentResponseError("model returned an empty message")
    return content


def _to_proposal(payload: dict[str, Any]) -> Proposal:
    """Build the Proposal. Every failure here is the type layer refusing
    a malformed record, which is the intended behaviour rather than
    something to work around."""
    try:
        amount_raw = payload["amount"]
        if not isinstance(amount_raw, str):
            raise AgentResponseError(
                f"amount must be a decimal string, got {type(amount_raw).__name__} "
                f"({amount_raw!r}) — a JSON number would be a float and float "
                "arithmetic is prohibited in the authority path"
            )
        return Proposal(
            network=payload["network"],
            asset=payload["asset"],
            action_class=payload["action_class"],
            target_class=payload["target_class"],
            function=payload["function"],
            counterparty_risk_tier=RiskTier(payload["counterparty_risk_tier"]),
            amount=Decimal(amount_raw),
            proposed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
    except KeyError as exc:
        raise AgentResponseError(f"model response is missing {exc}") from exc
    except (ValueError, ArithmeticError) as exc:
        # Covers RiskTier(...) on an unknown tier and Decimal() on an
        # unparseable amount. ValidationError is a ValueError subclass,
        # so a Proposal the type layer rejects lands here too.
        raise AgentResponseError(f"model response is not a valid proposal: {exc}") from exc


def propose(case: CaseUnderAssessment, *, model: str | None = None) -> Proposal:
    """Ask the model what it wants to do.

    Raises rather than returning a default on every failure path. The
    caller shows the failure; nothing is authorized.
    """
    api_key = _read_env_var("OPENROUTER_API_KEY")
    chosen_model = model or os.environ.get("FINNE_AGENT_MODEL") or _DEFAULT_MODEL

    try:
        response = requests.post(
            _ENDPOINT,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                # Identifies this project to OpenRouter. Not a secret.
                "X-Title": "Finne Memory",
            },
            json=_build_request(case, chosen_model),
            timeout=_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        # The key is in the request headers, never in the exception text
        # requests produces, but the URL is — and it carries no
        # credential. Report the type and message only.
        raise AgentUnavailableError(
            f"could not reach the model provider: {type(exc).__name__}: {exc}"
        ) from exc

    if response.status_code != 200:
        # Body may carry a provider error message. It never carries the
        # key, which is only ever sent in a header.
        raise AgentUnavailableError(
            f"model provider returned HTTP {response.status_code}: {response.text[:400]}"
        )

    try:
        body = response.json()
    except ValueError as exc:
        raise AgentResponseError(f"model provider returned non-JSON: {exc}") from exc

    if isinstance(body, dict) and body.get("error"):
        raise AgentUnavailableError(f"model provider reported an error: {body['error']}")

    content = _extract_content(body)

    try:
        payload = json.loads(content)
    except ValueError as exc:
        raise AgentResponseError(
            f"model did not return JSON despite a strict schema: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise AgentResponseError(
            f"model returned {type(payload).__name__}, expected a JSON object"
        )

    return _to_proposal(payload)
