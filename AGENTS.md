# Aurora OpenCode kit maintenance

This repository maintains only the copyable `interactive-kit`. Application
development instructions live in `interactive-kit/AGENTS.md` and are copied
into an application repository with the rest of the overlay.

When changing the kit:

- keep it product-independent and interactive;
- preserve the seven declared roles and one application-code writer;
- keep permissions in each agent frontmatter and MCP/model configuration in
  `interactive-kit/opencode.json`;
- do not add OpenSpec, a workflow state machine, profiles or automatic push;
- add deterministic coverage to `tests/test_interactive_kit.py` for enforceable
  behavior;
- keep product-specific observations out of this reusable repository;
- run `python3 tests/test_interactive_kit.py -v` before committing.

Do not edit or commit credentials, tokens, signing material, generated packages,
build directories or `.opencode/node_modules`. The tracked
`interactive-kit/aurora.local.json` is a deliberate non-secret configuration for
the demonstration environment; application copies remain ignored.
