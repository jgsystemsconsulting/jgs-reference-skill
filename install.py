#!/usr/bin/env python3
# Copyright (c) 2026 JG Systems Consulting Ltd. — MIT License (see LICENSE).
# SPDX-License-Identifier: MIT
"""
install.py — install jgs-reference-skill into a coding agent (RR-S-02/03/15).

This repo IS a single skill (SKILL.md at root + its tools). Native agents get the
whole skill folder copied unchanged; transform agents get SKILL.md rendered into
their own prompt/command format.

  python install.py                      # Claude Code (default), namespaced
  python install.py --agent all          # every user-global agent
  python install.py --agent gemini --dry-run
  python install.py --list-agents
  python install.py --flat               # drop the vendor namespace

Honours $CLAUDE_CONFIG_DIR for Claude Code. Exit 0 on success, 1 on error.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SKILL = "jgs-reference-skill"
NS = "jgs"
ROOT = Path(__file__).resolve().parent

_NS_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}

# Runtime payload a native install needs (everything SKILL.md drives), including
# pyproject.toml + README.md so `pip install -e ".[all]"` works from the installed
# tree. Repo meta beyond that (CI, landing page, the installers themselves) stays out.
PAYLOAD = [
    "SKILL.md",
    "scripts",
    "tools",
    "book_to_skill",
    "docs",
    "templates",
    "LICENSE",
    "NOTICE",
    "ATTRIBUTION.md",
    "pyproject.toml",
    "README.md",
]

HOME = Path.home()


def claude_home() -> Path:
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(cfg) if cfg else HOME / ".claude"


def validate_namespace(ns: str) -> None:
    """Reject non-kebab or Windows-reserved --namespace values before any FS work."""
    if not _NS_RE.fullmatch(ns):
        msg = (
            f"ERROR: --namespace must be kebab-case "
            f"(lowercase letters, digits, hyphens), got: {ns!r}"
        )
        print(msg, file=sys.stderr)
        raise SystemExit(1)
    if any(s.lower() in _WINDOWS_RESERVED for s in [ns, *ns.split("-")]):
        msg = (
            f"ERROR: --namespace must not use a Windows reserved device name "
            f"(con, prn, aux, nul, com1-9, lpt1-9), got: {ns!r}"
        )
        print(msg, file=sys.stderr)
        raise SystemExit(1)


def containing_root(agent: str) -> Path:
    """Resolved directory every install target for this agent must sit strictly under."""
    if agent == "claude":
        return (claude_home() / "skills").resolve()
    if agent == "openclaw":
        return (HOME / ".openclaw" / "skills").resolve()
    if agent == "copilot":
        return (HOME / ".copilot" / "skills").resolve()
    if agent == "gemini":
        return (HOME / ".gemini" / "commands").resolve()
    if agent == "codex":
        return (HOME / ".codex" / "prompts").resolve()
    if agent == "cursor":
        return (Path.cwd() / ".cursor" / "rules").resolve()
    raise SystemExit(f"ERROR: unknown agent for containment: {agent!r}")


def assert_under(root: Path, target: Path) -> None:
    """Require resolved target to be a strict descendant of resolved root."""
    root_r, tgt_r = root.resolve(), target.resolve()
    if root_r == tgt_r or root_r not in tgt_r.parents:
        msg = (
            f"ERROR: install target must resolve strictly under {root_r}, "
            f"got: {tgt_r}"
        )
        print(msg, file=sys.stderr)
        raise SystemExit(1)


# kind: native (copy folder) | transform (render SKILL.md to one file)
# target() returns the install path given the namespace.
AGENTS = {
    "claude":  dict(kind="native",    in_all=True,
                    target=lambda ns: claude_home() / "skills" / ns / SKILL),
    "openclaw": dict(kind="native",   in_all=True,
                    target=lambda ns: HOME / ".openclaw" / "skills" / ns / SKILL),
    "copilot": dict(kind="native",    in_all=True,
                    target=lambda ns: HOME / ".copilot" / "skills" / ns / SKILL),
    "codex":   dict(kind="transform", in_all=True, fmt="md",
                    target=lambda ns: HOME / ".codex" / "prompts" / f"{SKILL}.md"),
    "gemini":  dict(kind="transform", in_all=True, fmt="toml",
                    target=lambda ns: HOME / ".gemini" / "commands" / ns / f"{SKILL}.toml"),
    # Cursor rules are PROJECT-local, so they're excluded from --agent all.
    "cursor":  dict(kind="transform", in_all=False, fmt="mdc",
                    target=lambda ns: Path.cwd() / ".cursor" / "rules" / f"{SKILL}.mdc"),
}


def _skill_parts() -> tuple[str, str]:
    """Return (description, body) parsed from SKILL.md frontmatter."""
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    desc, body = "", text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            front = text[3:end]
            body = text[end + 4:].lstrip("\n")
            for line in front.splitlines():
                if line.strip().startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip('"')
    return desc, body


def render_transform(fmt: str) -> str:
    desc, body = _skill_parts()
    note = (f"<!-- {SKILL}: the Python tools this skill drives "
            f"(tools/*.py, scripts/extract.py) are NOT carried in this single prompt — "
            f"clone https://github.com/jgsystemsconsulting/{SKILL} for them. -->\n\n")
    if fmt == "toml":
        esc = body.replace('"""', '\\"\\"\\"')
        return f'description = "{desc}"\nprompt = """\n{note}{esc}\n"""\n'
    if fmt == "mdc":
        return f"---\ndescription: {desc}\nalwaysApply: false\n---\n\n{note}{body}"
    return f"# {SKILL}\n\n{note}{body}"  # md (codex)


def install_native(target: Path, dry: bool, force: bool) -> None:
    if target.exists() and not force and not dry:
        raise SystemExit(f"ERROR: {target} exists (use --force to overwrite).")
    if dry:
        print(f"  would copy {len(PAYLOAD)} item(s) → {target}")
        return
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for item in PAYLOAD:
        src = ROOT / item
        if not src.exists():
            continue
        dst = target / item
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(src, dst)
    print(f"  installed → {target}")


def install_transform(target: Path, fmt: str, dry: bool, force: bool) -> None:
    if target.exists() and not force and not dry:
        raise SystemExit(f"ERROR: {target} exists (use --force to overwrite).")
    if dry:
        print(f"  would write {fmt} prompt → {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_transform(fmt), encoding="utf-8")
    print(f"  wrote {fmt} → {target}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default="claude",
                    help="claude|openclaw|copilot|codex|gemini|cursor|all (default: claude)")
    ap.add_argument("--namespace", default=NS, help=f"vendor namespace dir (default: {NS})")
    ap.add_argument("--flat", action="store_true", help="install without the namespace dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--list-agents", action="store_true")
    args = ap.parse_args(argv[1:])

    # Token gate runs for every mode except --flat (namespace unused under --flat).
    if not args.flat:
        validate_namespace(args.namespace)

    ns = "" if args.flat else args.namespace  # pathlib drops the empty segment

    if args.list_agents:
        for name, a in AGENTS.items():
            print(f"{name:9} {a['kind']:9} {a['target'](ns)}")
        return 0

    if args.agent == "all":
        chosen = [n for n, a in AGENTS.items() if a["in_all"]]
        print(
            "Installing to user-global agents "
            "(Cursor is project-local - run --agent cursor separately):"
        )
    else:
        if args.agent not in AGENTS:
            ap.error(f"unknown agent '{args.agent}' (see --list-agents)")
        chosen = [args.agent]

    # Pass 1: resolve + contain every chosen target. No mkdir/rmtree/write yet.
    planned: list[tuple[str, dict, Path]] = []
    for name in chosen:
        a = AGENTS[name]
        target = a["target"](ns)
        assert_under(containing_root(name), target)
        planned.append((name, a, target))

    # Pass 2: install only after every containment check passed.
    for name, a, target in planned:
        print(f"[{name}] {a['kind']}")
        if a["kind"] == "native":
            install_native(target, args.dry_run, args.force)
        else:
            install_transform(target, a["fmt"], args.dry_run, args.force)

    if not args.dry_run:
        print(f"\nDone. Reload your agent (Claude Code: restart session) and run /{SKILL}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
