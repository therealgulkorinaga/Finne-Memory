# 2026-09-03 Two-Tool Operating Model: Arko's Role-And-Action Table

## Provenance

- Human director: Arko.
- AI tool: Claude Code (Anthropic). Model switched mid-session from Opus 5 to Sonnet 5 via the `/model` command; the switch carried full conversation context forward. See `BUILD_LOG.md` 2026-09-03 for a retrospective, unverified self-report of this switch — it was written during a later corrective pass, not at the time of the switch, and is not contemporaneous or independently verified.
- Capture status: **Not contemporaneous with the original exchange.** Arko supplied this table in conversation before Claude asked whether to formalize it; the table was not saved to `prompts/` at that time. Claude's own AI_USAGE.md entry then asserted, without asking, that the table did not need to be saved because it was "short" — a judgment call Claude was not entitled to make. An independent Codex review of the resulting addendum flagged the missing saved prompt as a BLOCKER. This file is written now, as the correction, and is dated to the day of the original exchange because that is when the instruction was given; it is not backdated to claim contemporaneity it does not have.
- Governing output: `DECISION-025`, `AGENT_BUILD_INSTRUCTIONS.md` Section 11.

## Material Instruction From Arko (verbatim)

Arko supplied this exact table, prefaced with "before I commit anything look at this:"

| Action | Owner |
| --- | --- |
| Create feature branch | Claude |
| Write implementation | Claude |
| Run initial tests | Claude |
| Explain changed files | Claude |
| Manually test product | You |
| Review diff against specification | Codex |
| Decide which findings to accept | You |
| Fix accepted findings | Claude |
| Verify fixes | Codex |
| Approve commit | You |
| Create commit | Claude, after your approval |
| Push branch | You from authenticated Bash |
| Open PR | You using GitHub/Bash |
| Write PR draft | Claude can prepare it |
| Review PR and merge | You |

Claude's response compared this table against `AGENT_BUILD_INSTRUCTIONS.md` Sections 7 (Review Protocol) and 8 (Commit Protocol) before adopting anything, and surfaced:

1. A real ambiguity in Section 8's "Agents do not commit directly" — literal human keystroke versus approval-gated agent execution.
2. A real gap: the existing text was silent on who pushes a branch or opens a pull request.
3. An unstated structural fact: the table implicitly collapses the ten-role fleet in Section 4 to Claude, Codex, and Arko.

Claude asked whether to formalize this as a documented addendum and decision, or treat it as an informal note for this phase only.

Arko replied: **"yes do that."**

Claude then drafted the addendum but, without being asked, decided the table itself did not need to be saved as a prompt because it was short. Arko had separately corrected Claude twice on a related but distinct point in the same exchange — first that Claude should not decide unilaterally whether a change needs independent review, then that the correct default is to draft that review automatically at every step regardless of size, not on request. The unsaved-prompt judgment call was the same underlying mistake (Claude deciding a governance requirement did not apply, instead of applying it and asking only if genuinely uncertain), caught this time by Codex's independent review rather than by Arko directly.

## Interpretation Notes Recorded By Claude

- The prompt-preservation requirement in `AGENT_BUILD_INSTRUCTIONS.md` Section 1 and `AI_BUILD_GOVERNANCE.md`'s Prompt And AI Attribution section has no stated size or materiality exception. Claude's original choice to skip saving this prompt was therefore not a defensible reading of an ambiguous rule; it was an unauthorized exception to a clear one.
- Going forward for this repository: every material instruction from Arko is saved under `prompts/` at the time it is acted on, without a size-based filter, consistent with the corrected default already recorded for independent-review drafting.
