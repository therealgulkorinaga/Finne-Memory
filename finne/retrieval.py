"""Candidate precedent generation (R1) — the first point where
finne.authority and finne.memory are connected.

Retrieval is a candidate generator only. Every candidate returned here
is later re-read exactly by the memory layer (already done, since
MemoryStore.search_cases returns validated CaseVersionRecord objects),
authority-folded, and deterministically filtered by
finne.authority.comparability — rank order and search relevance carry
no weight in the final result.

Safety property: because finne.authority.derivation takes the MAXIMUM
authorized amount over ELIGIBLE candidates, a retrieval miss (this
module failing to surface a real precedent) can only lower the derived
learned constraint, never raise it. Retrieval quality is therefore not
a correctness risk for the authority engine — it is a completeness
concern for the demo narrative, not a safety concern. No model
participates in retrieval.
"""

from __future__ import annotations

from finne.authority.comparability import compare
from finne.memory.client import MemoryStore
from finne.models import EvaluatedCandidate, Proposal

# Deliberately coarse: only the dimensions every fixture in the active
# corpus shares (ACTIVE_DEMO_DESIGN.md section 5). Including target_class
# or function here would narrow the FTS5 search query itself and risk
# under-retrieving cases that are legitimately supposed to come back as
# material-difference examples (e.g. CASE-004, CASE-005) — the precise
# exact-match filtering is comparability.compare()'s job, not the
# search query's. A wide net here is safe per the module-level docstring;
# comparability is what actually gates eligibility.
_QUERY_DIMENSIONS = ("network", "asset", "action_class")


def _build_query(proposal: Proposal) -> str:
    return " ".join(getattr(proposal, dim) for dim in _QUERY_DIMENSIONS)


def find_candidates(
    proposal: Proposal, memory: MemoryStore, *, limit: int = 50
) -> list[EvaluatedCandidate]:
    """Retrieve and assemble candidates for the authority engine.

    A candidate is excluded here — not merely marked ineligible — only
    when it cannot be assembled into a well-formed EvaluatedCandidate at
    all: no confirmed authority state exists yet (fold_authority_state
    returned None), or no outcome has been recorded yet. Both are
    "not ready to be judged as precedent," distinct from being eligible
    for derivation (comparable + active + success), which
    finne.authority.derivation decides, not this module. A withdrawn,
    superseded, questioned, or draft case still gets assembled and
    returned here — it is retrievable and displayable, per PREREQ-002 —
    even though the engine will not let it authorize anything.
    """
    query = _build_query(proposal)
    stored_cases = memory.search_cases(query, limit=limit)

    candidates: list[EvaluatedCandidate] = []
    for case in stored_cases:
        authority_state = memory.fold_authority_state(case.decision_version_id)
        if authority_state is None:
            # No confirmed authority event exists for this case yet —
            # e.g. the case version was written but never confirmed, or
            # the journal history failed validation. Not yet a candidate.
            continue

        outcome_record = memory.read_outcome(case.decision_version_id)
        if outcome_record is None:
            # No recorded outcome — cannot be judged success or failure,
            # so it cannot be assembled into a well-formed candidate.
            continue

        candidates.append(
            EvaluatedCandidate(
                decision_version_id=case.decision_version_id,
                authorized_amount=case.authorized_amount,
                authority_state=authority_state,
                outcome=outcome_record.outcome,
                comparability=compare(proposal, case.facts),
            )
        )
    return candidates
