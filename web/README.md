# Demonstration viewer

A single static page that shows the Finné Memory consistency check: **25,000.00 GBP proposed → 10,000.00 GBP authorized**, citing precedent `DV-001-V1`.

The corpus is synthetic and the run is recorded; see `DECISION-028`.

## Run it

No build step, no dependencies, no wallet.

```bash
python3 -m http.server 8000 --directory web
# open http://127.0.0.1:8000
```

Opening `web/index.html` directly from the filesystem also works, but serving it over HTTP is closer to how it behaves when deployed — a `file://` origin sends `Origin: null`, which some RPC providers treat differently.

## What it is, and what it is not

It renders a **recorded run**. The page says so in its own header, and the distinction matters:

- **It computes no authority.** The deterministic engine lives in `finne/authority/` and is deliberately not reimplemented here. Every decision value on the page is fixed output from a real run.
- **It is not a simulator.** Letting a visitor change inputs and watch authority recalculate would mean shipping a JavaScript reimplementation of the engine — a reimplementation is what a judge would then be looking at, not the real thing.
- **It connects no wallet.** The system signs with its own key, server-side. A browser wallet cannot write to the contract at all: `AuthorizationReceipt.sol` has an immutable `authorizedSigner` set to the deployer, and `test_live_contract_rejects_an_unauthorized_signer` asserts that any other sender reverts.

The one live thing on the page is the **onchain verification panel**, which reads the deployed contract directly from a public Base Sepolia RPC:

```
recorded(keccak256("DV-001-V1"))   -> true
getReceipt(keccak256("DV-001-V1")) -> authorizedAmount 10000000000  (10,000.00 GBP)
                                      factsHash, submittedBy, recordedAt
```

If that read fails, the panel says so and shows nothing. It never falls back to cached figures — a panel that silently displays stale values while claiming to be live is worse than one that admits it is down.

## Reproducing the embedded constants

The page embeds one hash and two function selectors rather than pulling in a crypto library to derive them at runtime:

```bash
python -c "from web3 import Web3; \
  print(Web3.keccak(text='DV-001-V1').hex()); \
  print(Web3.keccak(text='recorded(bytes32)')[:4].hex()); \
  print(Web3.keccak(text='getReceipt(bytes32)')[:4].hex())"
```

`getReceipt` returns four 32-byte words in fixed ABI order — `authorizedAmount`, `factsHash`, `submittedBy`, `recordedAt` — and the page decodes them positionally.

## Provenance

Implemented from the Claude Design artboard `Finne Memory Demo.dc.html` (project `51086be5-d2b8-412c-ac5a-9eaf4a11b298`). Design tokens are vendored into `quay-tokens.css`; see `REUSED_COMPONENTS.md`. The decision to add a web surface at all — the architecture had deliberately chosen a terminal interface — is recorded as `DECISION-026`.

**The terminal demonstration remains the primary artifact.** `HACKATHON_RULES.md` requires fresh-session recall to be shown in the submission video as one continuous unedited segment, which is the real two-terminal run, not this page.
