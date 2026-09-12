---
description: Create a new Aurora application from the pinned official CMake template.
agent: orchestrator
---

Initialize a new Aurora application in the current directory.

Interpret the arguments as:

- `$1`: reverse-DNS application ID, for example `ru.example.demo`;
- `$2`: English display name;
- `$3`: Russian display name.

If any argument is missing, ask only for the missing value. Display names containing `"`, `$`, backticks, backslashes, percent signs or line breaks are not accepted because this command is translated through a shell; ask for a plain display name instead. Refuse to initialize when application source files from another project are already present. The script always overwrites matching ApplicationTemplate paths, so this refusal is the guard against resetting another application. Project-local setup files that are absent from the template are preserved. Load the `aurora-bootstrap` skill and run its deterministic script with all values quoted as separate arguments:

```bash
python3 .opencode/skills/aurora-bootstrap/scripts/bootstrap.py --app-id "$1" --display-name "$2" --display-name-ru "$3" --destination .
```

The source must be the pinned commit from the official `ApplicationTemplate` repository's `cmake-version` branch. Create only the base application. Do not infer network libraries, desktop permissions or other application-specific dependencies. The script initializes Git when needed but does not make a commit. Report the source commit, Git repository state, and created and overwritten paths.
