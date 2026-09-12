---
name: aurora-device-observation
description: Observe a built Aurora application on an explicitly configured emulator with audb, while keeping automated evidence distinct from human acceptance.
---

# Aurora device observation

Use this skill only after the exact final RPM has passed the required build,
signing and validation checks. Read `aurora.local.json`; `device` must identify
an explicit emulator and `audb` must be the `audb` command. Check
`command -v audb` and `audb --version`, then invoke `audb` from `PATH`. A missing
command or device blocks only device observation. `audb` is emulator-only and
is not evidence for a physical device.

Never print or pass credentials, authorization codes or tokens through prompts,
logs, command lines, screenshots or Git. Owner-only configuration must be
provisioned by a reviewed helper that accepts secrets through a non-logging
channel. The person performs credential entry and authorization.

Before observation:

1. Record the RPM path and SHA-256, then deploy that exact artifact using the
   SDK's documented explicit device selection.
2. Confirm installation through Aurora application-model paths under
   `/opt/app/<app-id>/current/`; do not rely on `rpm -q` alone.
3. Check `audb setup-status`, `audb status` and capabilities. `audb install`
   modifies the SDK QEMU launcher and requires an explicit person-approved
   setup step plus emulator restart; never run it silently as ordinary testing.
4. Take an initial `audb screenshot --output /tmp/<name>.png` before input, then
   repeat after each relevant action. Keep screenshots and logs outside Git
   unless the contract names a reviewed evidence directory.

For a first launch that can show an Aurora permission dialog, start the launch
without waiting for it to finish and observe the emulator immediately from a
second live command/session. The runtime-manager start call may wait for the
dialog or report `ApplicationAlreadyLaunching`; that message is not proof of a
failed application when the permission UI is still pending. Use `audb tap` with
the shortest practical duration, then independently query the running
application list and PID.

Use `audb screenshot` for screen observation. It tries QMP first and, on a
supported Linux/X11 or XWayland host, captures the exact resolved emulator
window if QMP has no surface. Do not launch a separate screenshot utility or
capture the whole desktop. If `audb screenshot` fails, record its error and
mark screen observation blocked rather than treating another backend as proof
of the application's behavior.

Execute the contract's manual scenarios one at a time. For every action record:

- artifact hash, emulator identity and application PID;
- input coordinates or semantic action;
- before/after observation and whether another application opened;
- relevant Runtime Manager/application log excerpt;
- `observed`, `failed`, `blocked` or `not run`.

Automation may establish an **agent observation**, including launch, visible
labels, fail-closed behavior and navigation state. It may not mark a manual
criterion `passed`. Show the person the current screen and numbered scenario;
only their explicit report can produce `passed` or `failed`. A source/package
change makes affected observations stale and requires redeploy plus repetition.

When a translation catalog changed, observe the rebuilt package in that exact
locale. Check every active scenario screen for stale template wording,
unfinished-source fallbacks and unintended mixed-language copy; parsing the
source `.ts` alone does not prove which `.qm` the device loaded.
