"""Terminal presentation for the two-session demo.

Presentation ONLY (PREREQ-003 section 17): this module computes no
authority, reads no memory, and decides nothing. Every value it renders
is passed in, already final. It exists because the recall moment —
a fresh process constraining 25,000 to 10,000 because of something it
remembered — has to be legible on a video, and a wall of print()
output is not.

Two side-by-side terminals make the process separation self-evident in
a way a browser tab does not, which is why this is a `rich` terminal
application and not a web app (PREREQ-003 section 16).

Degrades deliberately: FINNE_PLAIN_OUTPUT=1 renders unstyled text, so
the session scripts remain readable when piped, captured by tests, or
run somewhere rich cannot draw.

Two rules make this module unable to damage a session:

- Every caller-supplied string is rendered as LITERAL text with rich
  markup disabled and control characters stripped. Unescaped, a fact
  value or an explanation containing `[/x]` raises MarkupError and a
  containing `\x1b[2J` clears the screen — neither may be reachable
  from data.
- Every write degrades before it fails (`_emit`): rich, then plain
  `print`, then — for everything except the two frames that exist to be
  seen — silence. By the time most of these calls run, an authorization
  is already persisted to Sibyl Memory and may already be settled on
  Base, so a closed pipe must not abort the remaining work.
- The two exceptions are `decision_panel` and `memory_failure`, which
  fail closed. A session that persists and submits an authorization no
  one ever saw satisfies none of the acceptance criteria this demo
  exists to meet; better to stop.
"""

from __future__ import annotations

import os
import unicodedata

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from finne.models import AuthorizationDecision, AuthorizationResult, EvaluatedCandidate, Proposal

_PLAIN_ENV_VAR = "FINNE_PLAIN_OUTPUT"
_ESCAPED_CATEGORIES = frozenset({"Mn", "Me"})

_RESULT_STYLES = {
    AuthorizationResult.ALLOW: "bold green",
    AuthorizationResult.CONSTRAIN: "bold yellow",
    AuthorizationResult.BLOCK: "bold red",
    AuthorizationResult.ESCALATE: "bold magenta",
}


def _plain() -> bool:
    return os.environ.get(_PLAIN_ENV_VAR) == "1"


def console() -> Console:
    # no_color and a fixed width keep captured output stable and
    # diffable when tests or a pipe consume it.
    return Console(no_color=_plain(), width=100 if _plain() else None)


def _clean(text: str) -> str:
    """Renders text safely WITHOUT losing which value it is.

    Every character that cannot be drawn safely is REPLACED by a visible
    `<U+XXXX>` escape rather than deleted, and the escape's own opening
    delimiter is escaped too. That makes the transformation injective:
    two different values can never render as the same string.

    Injectivity is the point, and it took three attempts to get.
    Deleting control characters made "A\x00B" and "AB" display
    identically. NFC-normalising made a decomposed and a precomposed
    decision-version id display identically. Escaping without escaping
    the delimiter made a literal "e<U+0301>" collide with a real
    combining acute. In a system whose entire claim is auditable
    citation, display may refuse to draw a character; it may not decide
    two different values are the same one.

    What gets escaped:
      C*     ANSI escapes, carriage returns, DEL, zero-width joiners,
             bidirectional overrides — anything that can move, hide, or
             reverse text already on screen. Newline is the exception:
             it is content here, and multi-line explanations need it.
      Mn/Me  Combining marks. They cannot drive the cursor, but they
             stack over a neighbouring glyph and can strike one
             through — U+0338 over a digit.
      <      The delimiter itself, so an escape can never be forged or
             collided with by ordinary input.
    """
    out = []
    for char in text:
        if char == "\n":
            out.append(char)
        elif char == "<" or unicodedata.category(char).startswith("C") or (
            unicodedata.category(char) in _ESCAPED_CATEGORIES
        ):
            out.append(f"<U+{ord(char):04X}>")
        else:
            out.append(char)
    return "".join(out)


def _text(value: str, style: str | None = None) -> Text:
    """Literal text: rich markup is never parsed, so `[/x]` in a fact
    value renders as itself instead of raising MarkupError."""
    return Text(_clean(value), style=style or "")


class PresentationError(Exception):
    """Raised when something that MUST be seen could not be written
    anywhere. Only the decision frame and the memory-failure frame are
    required; everything else degrades quietly."""


def _emit(out: Console, renderable, fallback: str, *, required: bool = False) -> None:
    """Writes, falling back to the plainest possible output.

    Best-effort by default: a note or a table that cannot be drawn must
    never abort a session that has already authorized (or refused) an
    action. `required=True` inverts that for the two frames whose whole
    purpose is to be seen — if BOTH paths fail there, the run fails
    rather than continuing to persist and submit an authorization no one
    ever saw. Independent review caught that: a silently-swallowed
    decision panel would let a session exit 0 having satisfied none of
    the visible-decision acceptance criteria.
    """
    try:
        out.print(renderable)
        return
    except Exception as rich_failure:
        try:
            print(_clean(fallback), flush=True)
            return
        except Exception as plain_failure:
            if required:
                raise PresentationError(
                    "the decision could not be displayed by any means "
                    f"(rich: {rich_failure!r}; plain: {plain_failure!r})"
                ) from plain_failure


def session_header(session_label: str, subtitle: str) -> None:
    out = console()
    plain = f"=== {session_label} — {subtitle} ==="
    if _plain():
        _emit(out, _text(plain), plain)
        return
    _emit(out, Panel(_text(subtitle, "bold"), title=_clean(session_label), border_style="cyan"), plain)


def proposal_panel(proposal: Proposal, owner_ceiling, source: str | None = None) -> None:
    """`source` names where the proposal came from.

    Without it, a run with a live model looks identical on screen to one
    using a fixed value — the agent does real work (it decides the
    amount and the risk rating) and gets no credit for it. Naming the
    source also makes the honest thing visible: on the default path
    nothing is called, and the screen says so rather than implying an
    agent that isn't there.
    """
    out = console()
    lines = []
    if source:
        lines.append(f"Assessed by: {source}")
    lines.append(
        f"Proposed: {proposal.amount} {proposal.asset} "
        f"({proposal.action_class} / {proposal.target_class} / {proposal.function})"
    )
    lines.append(f"Delegated authority: {owner_ceiling} {proposal.asset}")
    lines.append(f"Channel: {proposal.network}   Claim risk: {proposal.counterparty_risk_tier.value}   (the agent's own assessment)")
    body = "\n".join(lines)
    if _plain():
        _emit(out, _text(body), body)
        return
    _emit(out, Panel(_text(body), title="Proposal", border_style="white"), body)


def candidates_table(candidates: list[EvaluatedCandidate]) -> None:
    """Shows what memory returned AND why each candidate was or was not
    eligible. Similarity is never conflated with authority (PREREQ-003
    section 7): comparability, authority state, and outcome are three
    separate columns, all displayed, exactly as the engine saw them."""
    out = console()
    if not candidates:
        empty = "Retrieved 0 prior decisions from Sibyl Memory."
        _emit(out, _text(empty), empty)
        return

    lines = [f"Retrieved {len(candidates)} prior decision(s) from Sibyl Memory:"]
    for candidate in candidates:
        verdict = "ELIGIBLE" if candidate.is_eligible() else "excluded"
        lines.append(
            f"  {candidate.decision_version_id}: authorized={candidate.authorized_amount} "
            f"state={candidate.authority_state.value} outcome={candidate.outcome.value} "
            f"comparable={candidate.comparability.is_comparable} [{verdict}]"
        )
    fallback = "\n".join(lines)

    if _plain():
        _emit(out, _text(fallback), fallback)
        return

    table = Table(title=f"Retrieved {len(candidates)} prior decision(s) from Sibyl Memory")
    table.add_column("Prior decision")
    table.add_column("Settled", justify="right")
    table.add_column("Status")
    table.add_column("Outcome")
    table.add_column("Comparable")
    table.add_column("Eligible")
    for candidate in candidates:
        eligible = candidate.is_eligible()
        table.add_row(
            _text(candidate.decision_version_id),
            _text(str(candidate.authorized_amount)),
            _text(candidate.authority_state.value),
            _text(candidate.outcome.value),
            _text("yes" if candidate.comparability.is_comparable else "no"),
            _text("YES", "bold green") if eligible else _text("no", "dim"),
        )
    _emit(out, table, fallback)


def decision_panel(decision: AuthorizationDecision, proposal: Proposal, explanation: str) -> None:
    """The recall moment. Renders the proposed-to-authorized change and
    the precedent that caused it as the most prominent thing on
    screen — this is the single frame the demo video exists to show."""
    out = console()
    citation = ", ".join(decision.cited_precedents) or "no precedent"
    # The canonical, machine-checkable statement of the change. Emitted
    # verbatim in plain mode and embedded verbatim in the rich panel, so
    # the assertions in tests/test_fresh_session.py and
    # tests/test_base_adapter.py check the SAME string a viewer sees,
    # rather than a parallel format that could drift away from the demo.
    change_line = (
        f"{proposal.amount} proposed -> {decision.authorized_amount} authorized (citing {citation})"
    )
    result_line = f"RESULT: {decision.result.value.upper()}"
    fallback = f"{result_line}\n{change_line}\n{explanation}"

    if _plain():
        _emit(out, _text(result_line), result_line, required=True)
        _emit(out, _text(change_line), change_line, required=True)
        _emit(out, _text(explanation), explanation, required=True)
        return

    style = _RESULT_STYLES[decision.result]
    body = Text()
    body.append_text(_text(f"{change_line}\n\n", style))
    body.append_text(_text(f"Bound by: {decision.binding_constraint}\n"))
    body.append_text(_text(f"Citing precedent: {citation}\n\n"))
    body.append_text(_text(explanation, "dim"))
    _emit(
        out,
        Panel(body, title=f"Decision: {decision.result.value.upper()}", border_style=style.split()[-1]),
        fallback,
        required=True,
    )


def memory_failure(detail: str) -> None:
    """NEG-01 / PREREQ-003 section 19: memory unavailable, uninitialised,
    or unauthenticated resolves to `escalate`, "stated on screen as a
    memory failure, never as an allow".

    Deliberately distinct from `candidates_table([])`, which says
    "Retrieved 0 prior decisions". An empty record is a fact about history;
    a failed read is the absence of any fact at all. Conflating them is
    the one way an outage could be mistaken for a clean cold start.
    """
    out = console()
    lines = [
        f"MEMORY FAILURE: {detail}",
        "RESULT: ESCALATE",
        "Sibyl Memory could not be read. This is a failure, not an empty corpus: "
        "no authority can be derived from history that was never read. Nothing is "
        "authorized, nothing was submitted, and nothing was persisted.",
    ]
    body = "\n".join(lines)
    if _plain():
        _emit(out, _text(body), body, required=True)
        return
    _emit(
        out,
        Panel(_text(body, "bold red"), title="Memory failure", border_style="red"),
        body,
        required=True,
    )


def note(message: str) -> None:
    out = console()
    _emit(out, _text(message) if _plain() else _text(message, "dim"), message)


def warn(message: str) -> None:
    out = console()
    _emit(out, _text(message) if _plain() else _text(message, "bold red"), message)
