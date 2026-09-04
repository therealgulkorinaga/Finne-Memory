# 2026-09-03 TASK-001 Definition And Seam (a) Implementation Kickoff

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic), model Sonnet 5.
- Capture status: Contemporaneous, saved before implementation began.
- Governing outputs: `TASK-001` (in `TASKS.md`), and the first application code in this repository — `finne/models.py`, `finne/policy.py`, `finne/authority/comparability.py`, `finne/authority/derivation.py`, `finne/authority/engine.py`, `config/owner_policy.toml`, `tests/test_authority_invariants.py`, `tests/test_comparability.py`, `tests/test_authority_states.py`, `pyproject.toml`.

## Material Instruction From Arko (verbatim)

Across a short exchange, immediately following approval of the build sequencing recommendation (core `SPEC-001` implementation before any web-hosting work):

> got let get moving, define task-001 and start on seam (a)

This followed Claude's recommendation to sequence work as: (1) implement `SPEC-001` as approved — terminal interface, subprocess-isolated sessions; (2) record the demo video off the real run; (3) only then, if time remains, add a Streamlit web wrapper reusing the same subprocess design. Arko approved that sequencing and directed starting immediately with `TASK-001` and seam (a) — "models, policy, and the pure authority engine with its invariant tests," per the build order `SPEC-001` section 14 already named.

## Interpretation Notes Recorded By Claude

- `TASK-001` is drafted as the umbrella authorization for the full `SPEC-001` implementation, per the `Required Task Format` in `TASKS.md`. Individual seams (a)–(e) are implemented as separate bounded sub-changes — each its own branch, Codex review pass(es) under the two-pass cap, and commit — consistent with how every other bounded change in this repository has been handled, and with `SPEC-001` section 14's own suggested split points.
- Python 3.11, specified in `DECISION-023`, is not installed on this machine. Available interpreters are 3.13.1 and 3.14.3; neither 3.11 nor 3.12 is present. `sibyl-memory-client` requires only `>=3.10`. Claude selected Python 3.13.1 as the more conservative of the two available options — a routine, reversible implementation substitution, not a product or architecture decision, and is recording it here and in the commit explanation rather than treating it as silent.
- The authority engine's `derive_effective_authority` signature takes `owner_policy` and `hard_policy` as two separate parameters, per `SPEC-001` section 7, but no document defines `HardPolicy`'s exact field set — `PRD.md`'s five-input intersection formula names it conceptually without specifying its schema, and `PREREQ-003` explicitly defers "physical serialization" to implementation. Claude is implementing `HardPolicy` as a currently-active supplementary constraint, defaulting to a no-op (no additional restriction beyond `owner_policy`) for the V1 demo, since no document describes a scenario requiring an active temporary override. This keeps the five-way intersection architecturally real without inventing undescribed product behavior. Recorded here as a design decision made during implementation, per `PRD.md`'s own framing that "the exact implementation may differ" from the conceptual formula.
