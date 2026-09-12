# Interactive Aurora application development

This repository is an interactive workspace for a native Aurora OS application. The person approves product contracts and manually accepts observable behavior. Agents perform research, implementation and verification, but never convert an unperformed check into a pass.

## Target baseline

- Target Aurora OS 5.2.1, SDK 5.2.1.200 and Qt 5.6.3 unless the person explicitly chooses another installed target.
- Build native C++ and QML with CMake. Use public Aurora APIs and QML/Silica components supported by the chosen target.
- Treat official documentation, installed SDK availability, target compilation, package validation and runtime behavior as separate evidence.
- Do not assume an API exists because it exists in a newer desktop Qt release. Verify unfamiliar types, members, QML imports, packages and permissions before depending on them.
- Keep credentials, session tokens, private keys and signing material out of source, documentation, prompts and logs. `aurora.local.json` contains local paths only and stays outside application Git. Resolve a leading `~/` against the current user's home before invoking a tool; do not evaluate arbitrary shell expressions or environment-variable syntax from JSON.

## Natural-language workflow

The default `orchestrator` starts this workflow when the person asks to create or change an Aurora application. No workflow command is required.

1. Read the brief and existing product/batch documents. Capture the full requested scope as ordered observable outcomes. Select one primary demo outcome; keep every other outcome in the product backlog without researching or implementing it yet.
2. For a new application, collect only the application identifier and display names needed by `aurora-bootstrap`, create the scaffold immediately, initialize Git, and preflight Git identity plus the installed SDK/build-tool paths. Do not derive identifiers or names from a third-party service or trademark; ask for the person's values. Inspect only the project and explicit configured/known SDK paths, never broad home-directory inventories. Bootstrap is a prerequisite, never a product batch.
3. Derive the smallest research matrix that can unblock the primary demo outcome. Run only applicable lanes concurrently: `aurora-researcher` for platform work, `ui-researcher` for graphical behavior and `integration-researcher` for external contracts. Do not research backlog features.
4. Persist one compact current research packet under `docs/research/` and give it verbatim with the brief to `architect` and any pre-contract reviewer. A replacement agent reads that packet instead of rediscovering sources. Its first batch must deliver the primary observable outcome, not configuration or another technical layer.
5. Ask one compact informed interview after the synthesis returns. Ask only questions whose answers change the active outcome, architecture, risk or acceptance.
6. Write or update `docs/product.md`, `docs/ai-status.md` and one vertical contract in `docs/batches/<id>.md` from the templates. Ask the person to approve it before application code changes.
7. Give `implementer` only the approved active contract, relevant source paths and unresolved findings. Keep one writer and one active batch.
8. Give `reviewer` a narrow review packet: the contract, changed paths, the behavioral verification matrix and exact command/artifact evidence. The reviewer must identify which tests execute production code and which are only models/mirrors. Repair one consolidated set of concrete findings in the same batch; send only design-changing findings back through `architect`.
9. Present automated results, limitations and the contract's short manual checklist. Before handoff, verify that owner-only provisioning is executable for the real target tool and configuration path; when a configured emulator is reachable, load `aurora-device-observation`, install the exact final artifact and collect explicitly labelled agent observations. The person reports `passed`, `failed`, `blocked` or `not run` for each scenario.
10. Record the observation and open the next outcome from the product backlog only after the primary result is accepted or its residual limitation is explicitly accepted.

For a one-hour request, use this decision budget as a priority order rather than a promise: bootstrap and preflight by minute 5; targeted research by minute 15; approved contract by minute 20; compiling primary path plus deterministic tests by minute 42; target build, one review and one consolidated repair by minute 55; reserve the end for installation and human observation. When time is tight, defer polish and backlog behavior explicitly. Never defer the primary success path, its most consequential adverse path, or the evidence needed to distinguish a real result from a mock.

If a new session begins, recover from `docs/ai-status.md`, the active batch, `git status` and `git diff`. Do not repeat settled research without a changed contract or new uncertainty.

## Git checkpoints

- Bootstrap ensures the project is inside a Git repository with initial branch `main`; it does not stage or commit automatically.
- `orchestrator` owns commits. `implementer` and `reviewer` never commit or push.
- Before staging, inspect the working tree and select explicit paths. Never stage `aurora.local.json`, credentials, signing material, generated packages/build directories or `.opencode/node_modules`.
- Inspect the staged diff before every commit. Never use a commit to relabel failed, blocked or unperformed checks as passed.
- Normal checkpoints are: verified scaffold; approved product/batch contract; and an accepted vertical batch after automated checks and fresh review. Keep unfinished repair work uncommitted so the reviewer sees the complete diff.
- Use concise messages such as `chore: initialize Aurora application`, `docs(b1): approve contract` and `feat(b1): show signed-out application shell`. Never push unless the person separately requests it.
- If `user.name` or `user.email` is absent, mark only the commit checkpoint blocked and continue research, implementation, verification and manual handoff. Ask the person to configure identity alongside the next useful result; do not end a turn solely for identity and never invent values.

## Contract rules

- Separate observed facts, sourced constraints, user decisions and proposals.
- A contract names the user outcome, states, behavior, boundaries, automated checks, manual checks and known limitations.
- The product contract retains the full scope, one primary demo outcome and an ordered backlog. Research and implementation consume the primary outcome first, then pull the next outcome from that backlog.
- Every batch includes a behavior-to-evidence matrix. Deterministic parsers, request construction, navigation/state transitions, retry, cancellation and late completion require host coverage when they are part of the outcome; a reviewer may not pass them by source inspection alone. A test of a separately reimplemented model or language mirror is model evidence, not production-code coverage.
- Security-sensitive randomness and credential handling fail closed. Never substitute timestamps, process identifiers or another predictable fallback for cryptographic entropy.
- Provisioning, deployment and other helper scripts are product code for review purposes. Check their argv against the installed tool's help and exercise representative real values such as names containing spaces; a fake tool proves only the shape it was taught.
- Research reports are inputs. The batch contract is the handoff to implementation. The diff is the implementation artifact. Test/build output and reviewer findings are the verification artifacts.
- A positive human opinion never overrides failed required automated checks.
- A new source or package build makes earlier results stale for affected scenarios. State this plainly; no hidden state machine enforces it.
- User-visible text is behavior. When an active locale catalog exists, active batch screens must not silently fall back to unfinished source strings or stale template branding; translation changes require a rebuilt package and fresh observation in that locale.
- Do not add product behavior merely because it appears in a reference application.

## Roles and writes

- `orchestrator` owns shared product, batch and status documents. It does not edit application source.
- Researchers return reports to the orchestrator and do not edit the project.
- `architect` synthesizes verified research into a read-only architecture proposal and vertical batch boundaries.
- `implementer` is the only application-code writer. It stays within the approved batch boundaries.
- `reviewer` never edits. It reruns appropriate checks independently and reports concrete findings first.

Use the project-local Aurora skills for bootstrap, contracts, build feedback, review and optional emulator observation. `/aurora-init` is only a convenience for creating a missing scaffold from the pinned template.
