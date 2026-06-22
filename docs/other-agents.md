<!-- Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see ../LICENSE). SPDX-License-Identifier: MIT -->

# Installing with other agents

`jgs-reference-skill` follows the open [agentskills.io](https://agentskills.io)
`SKILL.md` format. Some agents read that format **natively** (the folder is copied
unchanged); others need a **format transform** into their own prompt/rule convention.
`install.py --agent <name>` handles both.

| Agent | `--agent` | Target | Format |
|-------|-----------|--------|--------|
| Claude Code | `claude` (default) | `~/.claude/skills/<ns>/jgs-reference-skill/` (honours `$CLAUDE_CONFIG_DIR`) | native |
| OpenClaw | `openclaw` | `~/.openclaw/skills/<ns>/jgs-reference-skill/` | native |
| GitHub Copilot CLI | `copilot` | `~/.copilot/skills/<ns>/jgs-reference-skill/` | native |
| OpenAI Codex CLI | `codex` | `~/.codex/prompts/jgs-reference-skill.md` | transform (prompt) |
| Gemini CLI | `gemini` | `~/.gemini/commands/<ns>/jgs-reference-skill.toml` | transform (TOML command) |
| Cursor | `cursor` | `./.cursor/rules/jgs-reference-skill.mdc` | transform (project-local rule) |

`<ns>` is the vendor namespace (`jgs` by default; `--flat` drops it). `--agent all`
installs to every **user-global** agent — Cursor is project-local, so run it separately
inside the project you want it in.

## Important limitation for transform agents

Native installs copy the **whole skill**, including its Python tools
(`tools/*.py`, `scripts/extract.py`) — so the full vet → extract → outline → verify
pipeline works.

The transform formats (Codex / Gemini / Cursor) carry only the **prose spec**
(`SKILL.md`) as a single prompt/command file. They **cannot** carry the executable
tools. On those agents the skill guides the workflow, but to actually run
`vet_source.py` / `outline.py` / `check_overlap.py` / `validate_pack.py` you must have
this repo cloned locally and invoke the tools from a shell. The generated prompt notes
this and links back to the repo.

For the full automated experience, use a native agent (Claude Code, Copilot CLI, or
OpenClaw).

## Examples

```bash
python install.py --agent codex --dry-run     # preview the Codex prompt target
python install.py --agent gemini              # write the Gemini TOML command
python install.py --agent cursor              # add a project-local Cursor rule
```
