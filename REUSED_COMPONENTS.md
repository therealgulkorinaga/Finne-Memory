# Reused Components

Record every reused code component, dependency, asset, dataset, template, license, source, and modification. An entry of `None` is required when a change introduces no reused component.

## 2026-09-02: Transferable Governance Update

- Arko-supplied governance text: The mandatory lifecycle, absolute stop conditions, and commit checklist were supplied directly by Arko and are preserved in `prompts/2026-09-02-transferable-ai-build-governance.md`.
- Lifecycle provenance: The lifecycle beginning `DECIDE → WRITE AND APPROVE SPEC` and ending `KNOWN-GOOD CHECKPOINT` was incorporated from Arko's saved instruction.
- Stop-condition provenance: The ten absolute stop conditions were incorporated from Arko's saved instruction.
- Commit-checklist provenance: The fifteen required commit-gate fields were incorporated from Arko's saved instruction.
- Inaccessible source: No unseen text was extracted or copied from `ETHOnline_2026_Solo_AI_Build_Rules(1).pdf`; Codex did not read or verify that PDF in this Work session.
- External code: None.
- Dependencies: None.
- Datasets: None.
- Templates: None.
- Assets: None.
- Licensing impact: None identified for this documentation-only change.

## 2026-09-03: Domain Pivot And Architecture Planning

- Arko-supplied text: The revised product thesis, authority model, invariants, two-session demonstration, deterministic/model split, architecture direction, and velocity model were supplied directly by Arko and are preserved verbatim in `prompts/2026-09-03-revised-direction-base-agent-authority.md`. That text is incorporated into `DECISION-022`, `PRD.md`, `docs/product/ACTIVE_DEMO_DESIGN.md`, and `docs/architecture/PREREQ-003_ARCHITECTURE.md`.
- External factual sources quoted or summarised: official event rules from `hack.sibyllabs.org` and `docs.sibyllabs.org`, and package metadata from the PyPI JSON API. These are cited with verification dates in `HACKATHON_RULES.md` and `PREREQ-003` section 0. No text was copied beyond short factual requirements and API names.
- Retained internal work: the `PREREQ-002` object model, authority states, transitions, citation rules, and invariants are carried forward from this repository's own approved planning contract. Their supplier-domain instantiation is retained as historical.
- External code: None. No code of any kind was written or copied in this change.
- Dependencies introduced: **None.** No package was installed.
- Dependencies *specified for future implementation* under `DECISION-023`, recorded here so their provenance and licensing are known before `SPEC-001` is approved:

| Package | Purpose | Licence | Notes |
| --- | --- | --- | --- |
| `sibyl-memory-client` `0.8.0` | Mandatory memory substrate | MIT | Verified from PyPI 2026-09-03; not installed |
| `web3` | Base adapter | MIT | Standard Python Ethereum client |
| `py-solc-x` | One-time contract compile | MIT | Avoids adding Foundry or Hardhat |
| `rich` | Terminal interface | MIT | Presentation only |
| `pytest` | Tests | MIT | Dev only |
| `hypothesis` | Property test for the owner-ceiling invariant | MPL-2.0 | Dev only; not distributed |
| ~~`anthropic`~~ | ~~Optional explanation~~ | MIT | **SUPERSEDED 2026-09-05**: declared during seam (e), removed the same day after independent review round 4. Never shipped as a dependency; the `explain` extra is gone from `pyproject.toml` and no module imports a model SDK. Retained here because this table is a historical record of what was declared |

- Licensing impact of this change: None from reuse, because no code or dependency was added. **Separately, Arko resolved `ORG-Q2` on 2026-09-03 by selecting MIT**, and `LICENSE` was added at repository root under `DECISION-024`. The text is the standard unmodified OSI MIT template with copyright `2026 Arko Ganguli`. Every dependency specified above is MIT-compatible; `hypothesis` is MPL-2.0 but is dev-only and not distributed.
- Datasets: The active demo corpus in `docs/product/ACTIVE_DEMO_DESIGN.md` is entirely synthetic and authored for this project. No external dataset was used.
- Templates and assets: None.

## 2026-09-10: Vendored Quay Design Tokens For The Demonstration Viewer

- Reused component: Quay design-system tokens — colour, typography, motion, and elevation custom properties.
- Source: Claude Design project "Viewer for control run comparison" (`51086be5-d2b8-412c-ac5a-9eaf4a11b298`), file `_ds/quay-design-system-1b60adac-6edc-473e-b609-5779c5d0ce46/colors_and_type.css`. Authored by Arko in Claude Design; imported 2026-09-10 via the `claude_design` MCP.
- Where it now lives: `web/quay-tokens.css`, with a provenance header naming the source file and import date.
- Modification: **Reduced, not copied wholesale.** Only the tokens `web/index.html` actually consumes were carried over. The upstream file's light-mode block, spacing/radii scales, deprecated `--copper-*` aliases, and its entire `.quay` component layer were omitted, so the vendored file stays auditable at a glance rather than shipping several hundred lines of unused CSS.
- Licensing impact: None. The tokens are the project owner's own design work, produced in the owner's Claude Design account, and are used in the owner's repository under the same MIT licence (`DECISION-024`).
- External code: The artboard `Finne Memory Demo.dc.html` was also read and implemented from, but **no code was copied from it.** It is a `.dc.html` canvas document whose runtime (`support.js`, ~70KB of generated React-based `dc-runtime`) and design-system bundle (`_ds_bundle.js`, whose manifest declares `"components":[]`) were both read and deliberately NOT reproduced. `web/index.html` is an independent vanilla-JS implementation of the design.
- Dependencies introduced: **None.** The artboard loaded `ethers@5.7.2` from jsdelivr purely to compute `keccak256("DV-001-V1")` and two 4-byte function selectors. All three are fixed constants, so they are embedded in `web/index.html` with the command that reproduces them — removing a ~250KB CDN dependency and the "keccak library failed to load" failure path with it. The page has no build step and no runtime dependency beyond the Google Fonts stylesheet the tokens import, which degrades to system fallbacks.
- Datasets: None. Every decision value on the page is fixed output from this project's own recorded demonstration run; the onchain values are read live from this project's own deployed contract.
- Templates and assets: None.
