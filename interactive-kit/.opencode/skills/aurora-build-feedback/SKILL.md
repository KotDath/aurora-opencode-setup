---
name: aurora-build-feedback
description: Run proportionate Aurora SDK tests, target builds, package validation and optional deployment as an evidence-producing feedback loop. Use during implementation or verification, not for product discovery.
---

# Aurora build feedback

Read `aurora.local.json`. Resolve a leading `~/` in a configured path against
the current user's home before invoking a tool; never pass the literal tilde as
an argv path and never evaluate arbitrary shell expressions or environment
variables from JSON. Never print, commit or place signing material and
credentials in prompts. Missing SDK, target, keys or device blocks only the
corresponding check.

Use the project's documented commands first. Before relying on unfamiliar `sfdk` or `apptool` syntax, inspect the installed executable's help. Keep host, target-build, package, signing, validation and runtime evidence distinct.

For each required check:

1. Record the exact command and working directory.
2. Run the narrowest relevant test first.
3. For a target build, identify the installed SDK and selected target, then build in a dedicated `build/<target>/` directory using the repository's supported wrapper.
4. On failure, identify the first causal diagnostic rather than the final cascading message. Make the smallest in-contract repair and repeat the failed check.
5. When requested and configured, sign the produced RPM and run the target validator against that exact artifact.
6. Deploy or launch only with an explicitly configured device. Do not treat installation as proof of the manual scenario.

Aurora SDK revisions expose different front ends. Do not assume `sfdk engine status` exists merely because `sfdk` exists. Inspect `sfdk --help`/`sfdk help` and the configured SDK root. Aurora SDK 5.2.1 commonly includes `sdk/<version>/tools/apptool`; when present, a CMake application can be built with the project as `WORKSPACE_DIR`, for example `apptool build --x64 --nosign --novalidate --dstdir build/x86_64`. Do not pass a spec path unless that installed wrapper's help or project documentation requires it. The resulting RPM is normally under `build/x86_64/RPMS/`; use the actual discovered path.

For device operations, locate the actual `sfdk` executable from project-local
configuration or the SDK installation and inspect `sfdk device exec --help` and
`sfdk deploy --help`. For `device exec`, prefer the documented explicit
`sfdk device exec <name-or-idx> -- <command>...` argv and test both a numeric
index and a real registered name, including spaces. For commands such as
`deploy` that consume only the configured device, use command-scoped
`-c device=...`; never mutate persistent `sfdk config` merely to run a step. A
registered device and a successful SSH command do not prove deploy readiness:
record emulator status and the actual deploy exit code.

When an owner-only value must be provisioned locally, provide a no-echo
interactive input mode so the person need not put it in a prompt, shell history
or process argv. Transport the value to the target through stdin rather than a
remote command string, never echo it, and reject empty/invalid input before
invoking the SDK tool. A separate explicit argv option may remain for
non-sensitive public automation values, but the two input modes must be
mutually exclusive and tested.

After a successful Aurora application deploy, verify the installed application
through its application-model paths (for example the desktop entry and resolved
`/opt/app/<app-id>/current/` target) as well as the deploy exit code. Do not
assume `rpm -q <app-id>` is authoritative: SDK deployment may publish symlinks
into `/opt/app` without registering the application in the conventional RPM
database visible to the device user.

Validate the exact final RPM and record the process exit code. A validator's
block count or lack of diagnostics is not a verdict without the exit code.
Signing is a separate check. Run `apptool sign` from the build directory that
actually contains `RPMS/`; without user keys, the 5.2.1 wrapper may use its
developer testing certificate. Compute the artifact hash afterwards and verify
the Aurora external signature with `rpmsign-external dump` and
`rpmsign-external verify` in the SDK build environment. A zero-output signing
command is not proof. Standard `rpm -Kv` does not understand the appended
Aurora external signature and may report payload digests as `BAD` after a valid
external signature, so do not use it as the signature verdict. Rerun package
validation if signing changes the package bytes.

Report command, exit status, relevant diagnostic and artifact path/hash. Zero discovered tests, skipped tests and unavailable tools are not passing evidence. Host-side tests do not prove target linkage; target compilation does not prove UI behavior; mocks do not prove a live integration.

When source, build configuration or package content changes, mark affected prior results stale and rerun them before handoff.

When translation catalogs change, verify the generated `.qm` rather than only
the source `.ts`. Use the installed Qt Linguist tooling (for example a
round-trip with `lconvert`) or package extraction to confirm representative
active strings, then require fresh observation in the selected device locale.
