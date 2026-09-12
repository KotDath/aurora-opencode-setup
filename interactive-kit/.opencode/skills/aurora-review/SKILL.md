---
name: aurora-review
description: Independently review an Aurora batch contract or implementation against evidence and produce one verdict plus manual acceptance scenarios. Use after drafting a contract and after implementation.
---

# Aurora review

Review the approved artifact, actual files and actual command results. Do not accept an implementer's summary as evidence and do not edit during review.

For a draft contract, verify traceability to the brief and human decisions, source-backed platform/integration facts, one observable outcome, relevant success and adverse states, narrow edit boundaries, executable checks and a manual observation. Reject unsupported target APIs and unresolved decisions that would change the implementation.

For code:

1. Inspect the complete relevant diff plus unchanged call sites and configuration boundaries.
2. Audit every row of the batch's behavior-to-evidence matrix. Trace the primary path and the most consequential error, hierarchical navigation, cancellation, retry of the exact failed operation and late-completion path.
3. Compare external requests, parsing and state transitions with their cited contracts.
4. Rerun proportionate checks independently and identify the exact artifact tested.
5. Check that permissions and dependencies are no broader than the implemented behavior requires.
6. State every runtime boundary that remains unobserved.

Treat visible wording, enabled states, navigation and error recovery as
behavior, not decoration. If the batch changes QML or translations, inspect the
exact user-visible contexts and compare them with the approved language/product
decisions. Reject stale template branding and unintended mixed-language active
screens. A source `.ts` check does not prove the packaged `.qm`; require a
rebuild and runtime observation when translation content changes.

Generated build and package paths are commonly ignored by Git. Inspect the
exact artifact path supplied in the handoff with `file`, `stat` and a hash; do
not infer that an RPM or `.qm` is absent from a glob/search command that honors
ignore rules. If the claimed exact path is genuinely absent, report that fact
instead of substituting another artifact.

Request changes when deterministic critical behavior is only source-inspected
despite being practical to host-test. In particular, do not infer parser shape,
request encoding, navigation history, retry target, cancellation semantics or
late-reply safety from compilation alone.

Classify test provenance explicitly: direct production module, mock around
production module, or separately reimplemented model/mirror. Passing a mirror
does not establish that production behavior matches it. For security-sensitive
code, reject predictable entropy/credential fallbacks. For helper and
provisioning scripts, compare argv with the installed CLI help, the runtime path
consumed by the application and representative actual values; fake-tool tests
alone cannot validate assumptions shared by both the script and fake.
For owner-entered values, verify a local no-echo path, mutual exclusion with any
automation flag, validation before tool invocation, stdin-only target transport
and absence of the value from stdout, stderr and child argv.

Return exactly one verdict: `passed` or `changes_requested`. Put blocking findings first; each finding names the file or behavior, evidence and expected correction. Consolidate related issues into one repair request.

Finish with a short numbered manual checklist tied to acceptance criteria. Only the person can report `passed`, `failed`, `blocked` or `not run` for those observations. A screenshot, build, package validation or agent statement cannot substitute for unperformed device behavior.
