---
name: aurora-contract
description: Turn researched product decisions into small human-readable Aurora product, status and vertical batch contracts. Use before implementation and whenever behavior or acceptance criteria change.
---

# Aurora contract

The contract is a shared Markdown artifact, not a hidden workflow state.

Use `templates/product.md`, `templates/ai-status.md` and `templates/batch.md`. Create `docs/product.md`, `docs/ai-status.md` and one file under `docs/batches/` when missing. Preserve earlier human decisions and source-linked fact IDs; never silently rewrite an accepted decision.

For each batch:

1. Preserve the person's full scope in the product contract, name one primary demo outcome, and keep the remaining observable outcomes in an ordered backlog. Define the active batch around that primary outcome; bootstrap and configuration alone are not product outcomes.
2. List inputs and source fact IDs. Mark proposals and unresolved probes separately from verified facts.
3. Describe user actions, visible states and transitions, including the material adverse path.
4. State explicit boundaries and allowed `edit_paths`.
5. Add a behavior-to-evidence matrix that maps every critical success/adverse behavior to a deterministic automated check, a manual observation, or an explicit unverified boundary. Parsers, request construction, state transitions, navigation, retry, cancellation and late completion must be host-tested when practical.
6. Specify a short numbered manual checklist. A build is not a runtime observation.
7. Ask the person to approve the draft before source edits begin.

Record each durable decision with a status and evidence chain. Use
`verified-constraint` for sourced technical facts, `product-choice` for a human
preference among supportable alternatives, `probe` for an unresolved technical
claim and `rejected` for an excluded or unsupported option. Human approval
accepts a product tradeoff; it never changes a `probe` into a verified fact.
Do not approve a batch whose observable outcome depends on an unresolved
blocking probe.

Use these statuses consistently: `draft`, `approved`, `implementing`, `review`, `awaiting-human`, `accepted`, `blocked`. Status describes the current human-readable record; it is not an authorization mechanism.

The product contract owns durable behavior and decisions. A batch owns one increment. The status file is a compact recovery index: active batch, last verified artifact, stale evidence, blocker and next human decision. Keep raw research notes and long logs out of the product contract.

If research contradicts a requested behavior, show the exact conflict and smallest probe or decision needed. If review changes product behavior, return the batch to `draft`; a code defect can stay in the current approved batch.

For a one-hour request, keep the active contract compact enough to approve in a
single reading. Record optional polish and later features in the backlog rather
than expanding the active batch.
