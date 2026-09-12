---
name: aurora-bootstrap
description: Initialize an empty Aurora OS project from the pinned official ApplicationTemplate CMake branch. Use only for new project scaffolding or when the user invokes /aurora-init; do not use to add features to an existing application.
---

# Aurora project bootstrap

Use `scripts/bootstrap.py`; do not reproduce its transformations by hand.

The script retrieves the official repository `https://hub.mos.ru/auroraos/demos/ApplicationTemplate.git`, branch `cmake-version`, at the pinned commit declared in the script. It verifies the commit and adapts it in a temporary directory before publishing. Publishing always overwrites matching template files and merges template directories while preserving destination-only files such as `.opencode`, `docs`, `templates`, `AGENTS.md` and `opencode.json`. It rejects symbolic-link targets and file/directory type conflicts. If publication fails, it restores replaced files and removes partially created paths.

After successful publication the script ensures that the destination belongs to a Git repository. It creates a repository with initial branch `main` when neither the destination nor a parent directory is already a repository. It never stages or commits files automatically.

Required inputs are a lowercase reverse-DNS application ID and plain English/Russian display names. The command rejects shell-sensitive display-name characters before invocation. Never derive these values from credentials, account data, a third-party service name or its trademark; collect the person's intended identifier and branding without proposing an affiliation.

Run from the intended project root:

```bash
python3 .opencode/skills/aurora-bootstrap/scripts/bootstrap.py \
  --app-id "ru.example.demo" \
  --display-name "Demo" \
  --display-name-ru "Демо" \
  --destination .
```

Use `--offline` only when the pinned commit already exists in the verified cache. A failed fetch without a verified cache is a blocker.

Run the bootstrap only for a new scaffold or an explicitly requested reset. Re-running it replaces every destination file whose relative path is also present in the generated ApplicationTemplate, including `README.md`, `.gitignore`, CMake, QML and C++ template files. It does not delete destination-only files.

The result is deliberately a base project. Add Qt modules, RPM dependencies and desktop permissions only after the brief requires them and `aurora-researcher` verifies their exact target-version contract. Treat `.aurora-template-origin.json` as provenance; do not edit it to make a later verification appear successful.

After creation, inspect the returned JSON fields `git_repository`, `created_paths` and `overwritten_paths`, then inspect `git status`. Report the pinned commit, retrieval mode and overwritten paths. Before the first commit, confirm that ignored local configuration, credentials, signing material, generated build directories and `.opencode/node_modules` are not staged. The bootstrap does not commit automatically.
