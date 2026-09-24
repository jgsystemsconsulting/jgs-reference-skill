# Plan: P5 install-containment-and-docs

- date: 2026-09-24
- spec: docs/superpowers/specs/2026-09-24-install-containment-and-docs.md (reviewed clean over 2 ARL rounds)
- plan_path: docs/superpowers/plans/2026-09-24-install-containment-and-docs.md
- author-leaf: Claude-pinned leaf unavailable; plan-author fallback (inline on sdd-executor-deep seat)
- context: ad-hoc (spec Evidence current; install.py 171 lines, PAYLOAD L37-40, main L129-167, book_to_skill/config.py OUTPUT_DIR/BOOK_SKILL_WORKDIR, README Install L51 + CLI L106-116, docs/skill-usage.md L46-47 three-gates stale + L59-60 /tmp, docs/other-agents.md path table already namespaced, SKILL.md Step 2 L116 tempdir form, pyproject.toml readme = README.md, tests/test_build_pack_scaffold.py containment pattern; no tests/test_install*.py today)
- research: skipped (carried from spec)

## Approach

S-sized, three tasks, dependency order:

1. Harden `install.py`: kebab + Windows-reserved namespace gate, per-agent containing roots (all `.resolve()` including Claude skills), `assert_under` strict descendant, two-pass validate-all-then-install, validation on `--list-agents` / `--dry-run`, PAYLOAD gains `pyproject.toml` and `README.md`. Force/dry/copy semantics for contained targets stay byte-equivalent.
2. Doc sync: README install path + workdir truth, docs/skill-usage.md workdir + four-gates count, SKILL.md BOOK_SKILL_WORKDIR note, docs/other-agents.md one-line kebab note only if needed.
3. New `tests/test_install_containment.py` locking Success criteria 1-6 (and payload presence), then full-suite verification.

Do not import `tools/build_pack.py` into `install.py`. Do not add `--self-check` to install. Do not expand PAYLOAD beyond the two new files. Do not redesign transform agents. Do not touch hatch build config. Transcribe containment helpers from the spec shape; do not invent a path library.

## Blocking-discovery rule

`install.py` has **no test file today**. Product edits land first; the new module is Task 3. Before any product edit, run from the repo root in Git Bash:

```bash
python -m pytest -q 2>&1 | tail -12
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
# Optional smoke (must still exit 0 on current tree with default args in dry-run):
python install.py --dry-run --list-agents 2>&1 | head -5 || true
python install.py --dry-run 2>&1 | head -5
```

Baseline expectation from the P4 era: **506 passed, 5 skipped** (or the live count if P4 already landed a few more; record the exact number you see). Five-tool self-checks exit 0. Use `python` locally when `python3` is absent; CI text stays `python3`.

If pytest is red, or any self-check fails, on the current tree: **stop and report**. Do not silently patch product code to green the baseline. A Windows-only symlink `OSError` in `tests/test_output_dir_security.py` (Developer Mode missing) is the same documented environment carve-out as P1-P4; note it and continue. Any other red is a blocker for the controller.

Re-run pytest + five self-checks after Task 1 and after Task 3. Final verification requires green against the new baseline (old count + new containment tests).

## Frozen reason / error literal style

Match build_pack and the current install exists-guard tone. Print to **stderr**, raise `SystemExit` with the same string (install already uses `raise SystemExit(f"ERROR: ...")` for exists; keep that contract so `__main__` stays `raise SystemExit(main(sys.argv))`).

Exact strings (transcribe; `{ns!r}` / path values vary):

```text
ERROR: --namespace must be kebab-case (lowercase letters, digits, hyphens), got: {ns!r}
ERROR: --namespace must not use a Windows reserved device name (con, prn, aux, nul, com1-9, lpt1-9), got: {ns!r}
ERROR: install target must resolve strictly under {root_r}, got: {tgt_r}
ERROR: {target} exists (use --force to overwrite).
```

Namespace errors also `print(..., file=sys.stderr)` before `raise SystemExit(...)` **or** raise `SystemExit` with the message only (SystemExit string goes to stderr via the interpreter). Prefer the build_pack twin: print to stderr, then `raise SystemExit(1)` (int code) so tests can assert `e.code == 1` without parsing the message from the exception alone. If you raise `SystemExit(1)` after printing, capture stderr in tests via `capsys` or a thin runner. Either int-code-after-print or string-SystemExit is acceptable; **pick int-code-after-print** so the runner below stays simple and matches build_pack's `return 1`.

## Task 1: install.py containment + PAYLOAD

**Files:** `install.py` only.

### 1a. Imports and module constants

Add `re` to the import block. Keep every other import.

Immediately after the `NS = "jgs"` / `ROOT = ...` block (before PAYLOAD is fine; after HOME also fine), add:

```python
_NS_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}
```

### 1b. PAYLOAD

Replace the PAYLOAD list and refresh the comment so it no longer implies pyproject is excluded:

```python
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
```

Order inside the list is not load-bearing; keeping the old nine first and appending the two new names is fine. Both files exist at repo root today.

### 1c. Helpers: validate_namespace, containing_root, assert_under

Place after `claude_home()` and before (or after) `AGENTS`. Do not import build_pack.

```python
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
```

Notes locked by the spec:

- Claude root is `(claude_home() / "skills").resolve()` (full path resolve, not resolve-home-then-join without resolve on skills).
- Strict descendant only: equality with the root fails (a target of exactly `.../skills` must not install).
- `containing_root` may use if/elif or a dict of zero-arg callables; keep it stdlib and side-effect free beyond Path.resolve.

Do **not** change the `AGENTS[...]["target"]` lambdas' intended layouts for valid inputs. Optional: add a `"root"` callable per agent instead of `containing_root(name)`; either shape is fine if the six roots match the table above.

### 1d. Rewrite `main` control flow (two-pass)

Keep argparse flags identical. Replace the body after `args = ap.parse_args(...)` with this shape:

```python
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--agent",
        default="claude",
        help="claude|openclaw|copilot|codex|gemini|cursor|all (default: claude)",
    )
    ap.add_argument(
        "--namespace", default=NS, help=f"vendor namespace dir (default: {NS})"
    )
    ap.add_argument(
        "--flat", action="store_true", help="install without the namespace dir"
    )
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
        print(
            f"\nDone. Reload your agent (Claude Code: restart session) "
            f"and run /{SKILL}."
        )
    return 0
```

Load-bearing behaviours:

1. **`--flat`**: skip `validate_namespace`; `ns = ""`; target is still assert_under'd (contained by construction for valid agent roots).
2. **`--list-agents`**: validation runs first when not flat; listing still prints paths and returns 0; **no** install pass.
3. **`--dry-run`**: still runs pass 1 containment, then `install_*` dry branch (print only, no FS effect). Bad namespace never reaches dry print.
4. **`--agent all`**: one bad target fails the whole run in pass 1 before any agent is installed (no partial multi-agent install).
5. **`install_native` / `install_transform`**: leave bodies unchanged (exists+!force+!dry SystemExit string; dry return; else rmtree-if-exists + mkdir/copy or write_text). Contained `--force` overwrite stays exactly as today.

Prose note: the existing Cursor help string in current install.py uses an em dash before "run". Prefer leaving that one pre-existing character untouched (drive-by churn). All new code and new docs in this package must stay em-dash free. If the implementer is already touching that print, ASCII hyphen is fine.

### 1e. Check after Task 1

```bash
python -c "
import install
from pathlib import Path
import tempfile, os
assert 'pyproject.toml' in install.PAYLOAD and 'README.md' in install.PAYLOAD
# valid default ns
install.validate_namespace('jgs')
# reserved
try:
    install.validate_namespace('con'); raise SystemExit('expected fail')
except SystemExit as e:
    assert e.code == 1
# kebab
try:
    install.validate_namespace('Bad Slug'); raise SystemExit('expected fail')
except SystemExit as e:
    assert e.code == 1
# contain happy
root = Path(tempfile.mkdtemp())
(root / 'skills').mkdir()
tgt = root / 'skills' / 'jgs' / 'jgs-reference-skill'
install.assert_under(root / 'skills', tgt)
# contain escape
try:
    install.assert_under(root / 'skills', root / 'outside'); raise SystemExit('expected fail')
except SystemExit as e:
    assert e.code == 1
print('TASK1-SMOKE-OK')
"
python install.py --dry-run 2>&1 | head -8
python install.py --namespace 'Bad Slug' --dry-run; echo exit:$?
python install.py --namespace con --list-agents; echo exit:$?
python -m pytest -q 2>&1 | tail -12
```

Expect: smoke OK; default dry-run still prints a claude native would-copy line; bad namespace dry-run and list-agents exit nonzero; existing pytest suite still green (no new module yet).

## Task 2: Doc sync

**Files:** `README.md`, `docs/skill-usage.md`, `SKILL.md`, and only if needed `docs/other-agents.md`.

Written prose standard: no em dashes, staff-engineer voice, avoid-ai-writing bar. Prefer surgical line edits over rewrites.

### 2a. README.md

**(1) CLI Usage workdir (current L106 and L109 bare `/tmp/book_skill_work/...`).**

Replace the extract/outline/verify block so it matches `book_to_skill/config.py`. Preferred shape:

```bash
# 3. Extract + outline, then generate the pack (agent follows SKILL.md)
# Extract writes to tempfile.gettempdir()/book_skill_work by default
# (Windows: under %TEMP%), or $BOOK_SKILL_WORKDIR when set.
python3 scripts/extract.py path/to/source.pdf --mode technical
WORKDIR="${BOOK_SKILL_WORKDIR:-$(python -c "import tempfile, pathlib; print(pathlib.Path(tempfile.gettempdir()) / 'book_skill_work')")}"
python3 tools/outline.py --source "$WORKDIR/full_text.txt" --out outline.json

# 4. Verify before publishing: all four must pass
python3 tools/check_overlap.py --source "$WORKDIR/full_text.txt" --pack packs/nasa-se-handbook
python3 tools/validate_pack.py packs/nasa-se-handbook
python3 tools/pack_eval.py --pack packs/nasa-se-handbook
python3 tools/scan_generated_skill.py packs/nasa-se-handbook
```

A shorter form is also fine if it (a) names `BOOK_SKILL_WORKDIR`, (b) names the `tempfile.gettempdir()/book_skill_work` default and Windows `%TEMP%`, and (c) uses a placeholder such as `<workdir>/full_text.txt` with workdir defined one line above. **Do not** leave bare `/tmp/book_skill_work` as the only example.

**(2) Install path paragraph (current L115-116).**

Change:

```text
As an agent skill, install it where your host discovers skills (e.g.
`~/.claude/skills/jgs-reference-skill/`) and drive it conversationally (see
```

to the namespaced default:

```text
As an agent skill, install it where your host discovers skills (default
`~/.claude/skills/jgs/jgs-reference-skill/`; `--flat` drops the `jgs/` segment)
and drive it conversationally (see
```

Leave the Install section's already-correct L51 namespaced line intact unless a one-word alignment is required. Do not change the agent-paste block beyond path truth if it already defers to `install.py --list-agents`.

### 2b. docs/skill-usage.md

**(1) Four gates count (current L46-47 "three gates").** Spec non-goal says fix unconditionally while editing this file:

```text
6. **Verify** four gates: `check_overlap.py` (no verbatim), `validate_pack.py`
   (structure + tier), `pack_eval.py` (index routes are grounded),
   `scan_generated_skill.py` (prompt-injection / unsafe-authority scan).
```

**(2) Running-the-tools-directly block (current L59-60 `/tmp/...`).** Same workdir truth as README. Example:

```bash
python tools/vet_source.py --title "NASA SE Handbook" --publisher "NASA" --license "Public Domain (US Government work)"
# full_text.txt lives under BOOK_SKILL_WORKDIR if set, else tempfile.gettempdir()/book_skill_work
# (Windows: %TEMP%\book_skill_work)
python tools/outline.py --source <workdir>/full_text.txt --out outline.json
python tools/check_overlap.py --source <workdir>/full_text.txt --pack packs/<slug>
python tools/validate_pack.py packs/<slug>
python tools/pack_eval.py --pack packs/<slug>
python tools/scan_generated_skill.py packs/<slug>
```

Install section already namespaced; keep it.

### 2c. SKILL.md Step 2

Current L116 already uses `<tempdir>/book_skill_work/{full_text.txt,metadata.json}`. Extend that sentence (or the next) so agents do not invent `/tmp/...` on Windows:

```text
Output lands in
`<tempdir>/book_skill_work/{full_text.txt,metadata.json}`
(`BOOK_SKILL_WORKDIR` if set, else `tempfile.gettempdir()/book_skill_work`;
on Windows the default is under `%TEMP%`). Read `metadata.json`
```

Do not rework Step 9 or gate counts (P4 owns those; Step 9 already says four gates). Prerequisites `pip install -e ".[all]"` stays; Goal 3 makes it true for installed trees.

### 2d. docs/other-agents.md

Path table already documents `~/.claude/skills/<ns>/jgs-reference-skill/` with `<ns>` default `jgs`. Touch **only** if you add one sentence under the table:

```text
`--namespace` must be a single kebab-case token (lowercase letters, digits, hyphens);
no `..`, no absolute path, no Windows reserved device names.
```

Do not redesign the transform-agent limitation section.

### 2e. Check after Task 2

```bash
# No bare /tmp/book_skill_work left as the sole workdir example in operator docs:
rg -n '/tmp/book_skill_work' README.md docs/skill-usage.md SKILL.md || true
rg -n 'BOOK_SKILL_WORKDIR|gettempdir|%TEMP%' README.md docs/skill-usage.md SKILL.md
# Namespaced install example present; bare non-namespaced primary example gone:
rg -n 'skills/jgs/jgs-reference-skill' README.md
rg -n 'skills/jgs-reference-skill/' README.md || true
# skill-usage four gates:
rg -n 'four gates' docs/skill-usage.md
```

Expect: BOOK_SKILL_WORKDIR + gettempdir (or %TEMP%) hits in README, skill-usage, SKILL.md; README primary install example includes `jgs/`; skill-usage says four gates. A residual mention of `/tmp` only as "on many Unix hosts" is acceptable if the Windows default is also named; bare `/tmp/book_skill_work` as the only copy-paste path is not.

## Task 3: Regression tests + final verification

**Files:** create `tests/test_install_containment.py` only (no product edits unless a Task 1 bug surfaces).

### 3a. Module skeleton and runner

`install.py` lives at repo root (not under `tools/`). Drive it by importing `install` and calling `install.main(argv)`, with `install.HOME` and `CLAUDE_CONFIG_DIR` pointed under `tmp_path` so tests never touch the real user profile. Spec Goal 5 prefers this over a pure subprocess suite; a thin subprocess helper is allowed as a supplement for "python install.py" smoke but is not required if `main()` coverage is complete.

```python
# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Containment + payload regression for install.py (P5).

Covers spec 2026-09-24-install-containment-and-docs Success criteria 1-6
(namespace gate, decoy no-rmtree, dry-run/list-agents validation, default
install payload, --flat, contained --force, metadata build from installed tree).
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import install  # noqa: E402

SKILL = "jgs-reference-skill"


def _run(argv, monkeypatch, home: Path, claude_cfg: Path | None = None):
    """Call install.main with a fake HOME / optional CLAUDE_CONFIG_DIR.

    Converts SystemExit(int|str|None) into an int rc so assertions stay simple.
    """
    monkeypatch.setattr(install, "HOME", home)
    env_cfg = str(claude_cfg) if claude_cfg is not None else str(home / ".claude")
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", env_cfg)
    # Avoid cursor tests depending on the real cwd rules dir unless a test sets it.
    try:
        return install.main(["install.py", *argv])
    except SystemExit as e:
        if e.code is None:
            return 0
        if isinstance(e.code, int):
            return e.code
        return 1


def _skills(cfg: Path) -> Path:
    return cfg / "skills"
```

### 3b. Reject cases (SC1, SC2): nonzero, no writes, decoy intact

```python
def test_namespace_absolute_rejected(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    absent = Path(tempfile.gettempdir()) / f"jgs-evil-{os.getpid()}-{uuid4().hex[:8]}"
    assert not absent.exists()
    before = set(tmp_path.rglob("*"))
    rc = _run(["--namespace", str(absent), "--force"], monkeypatch, home, cfg)
    assert rc == 1
    assert not absent.exists()
    assert set(tmp_path.rglob("*")) == before


def test_namespace_dotdot_rejected(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    before = set(tmp_path.rglob("*"))
    rc = _run(["--namespace", "../../x", "--force"], monkeypatch, home, cfg)
    assert rc == 1
    assert set(tmp_path.rglob("*")) == before


@pytest.mark.parametrize("ns", ["Bad Slug", "bad_slug", "Bad", "", "jgs.ns", "JGS"])
def test_namespace_bad_kebab_rejected(tmp_path, monkeypatch, ns):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    before = set(tmp_path.rglob("*"))
    # argparse with namespace "" still passes the flag value as empty string
    argv = ["--force"]
    if ns == "":
        argv = ["--namespace", "", "--force"]
    else:
        argv = ["--namespace", ns, "--force"]
    rc = _run(argv, monkeypatch, home, cfg)
    assert rc == 1
    assert set(tmp_path.rglob("*")) == before


@pytest.mark.parametrize("ns", ["con", "CON", "prn", "aux", "nul", "com1", "lpt9"])
def test_namespace_windows_reserved_rejected(tmp_path, monkeypatch, ns):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    before = set(tmp_path.rglob("*"))
    rc = _run(["--namespace", ns, "--force"], monkeypatch, home, cfg)
    assert rc == 1
    assert set(tmp_path.rglob("*")) == before


def test_decoy_outside_root_not_rmtree(tmp_path, monkeypatch):
    """Old join semantics: --namespace <abs> + --force could rmtree the decoy.

    After the gate, the decoy must still exist with its sentinel intact.
    """
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    decoy = tmp_path / "outside-decoy" / SKILL
    decoy.mkdir(parents=True)
    sentinel = decoy / "SENTINEL"
    sentinel.write_text("do-not-delete", encoding="utf-8")
    # Absolute namespace that, under pre-fix join, would become the target parent.
    rc = _run(
        ["--namespace", str(decoy.parent), "--force"],
        monkeypatch,
        home,
        cfg,
    )
    assert rc == 1
    assert decoy.is_dir()
    assert sentinel.read_text(encoding="utf-8") == "do-not-delete"


def test_bad_namespace_dry_run_no_writes(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    before = set(tmp_path.rglob("*"))
    rc = _run(["--namespace", "Bad Slug", "--dry-run"], monkeypatch, home, cfg)
    assert rc == 1
    assert set(tmp_path.rglob("*")) == before


def test_bad_namespace_list_agents_no_writes(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    before = set(tmp_path.rglob("*"))
    rc = _run(
        ["--namespace", "con", "--list-agents"],
        monkeypatch,
        home,
        cfg,
    )
    assert rc == 1
    assert set(tmp_path.rglob("*")) == before
```

### 3c. Happy paths (SC3-SC6)

```python
def test_default_dry_run_prints_contained_writes_nothing(tmp_path, monkeypatch, capsys):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    rc = _run(["--dry-run"], monkeypatch, home, cfg)
    assert rc == 0
    out = capsys.readouterr().out
    # Contained target under the fake CLAUDE_CONFIG_DIR skills root.
    assert "jgs" in out and SKILL in out
    assert not (_skills(cfg) / "jgs" / SKILL).exists()


def test_default_install_creates_namespaced_tree_with_payload(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    rc = _run([], monkeypatch, home, cfg)
    assert rc == 0
    dest = _skills(cfg) / "jgs" / SKILL
    assert (dest / "SKILL.md").is_file()
    assert (dest / "pyproject.toml").is_file()
    assert (dest / "README.md").is_file()
    assert (dest / "book_to_skill").is_dir()
    # Sanity: PAYLOAD items that exist at repo root were copied.
    for item in install.PAYLOAD:
        src = REPO_ROOT / item
        if src.exists():
            assert (dest / item).exists(), item


def test_flat_install_no_namespace_segment(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    rc = _run(["--flat"], monkeypatch, home, cfg)
    assert rc == 0
    dest = _skills(cfg) / SKILL
    assert (dest / "SKILL.md").is_file()
    assert not (_skills(cfg) / "jgs" / SKILL).exists()
    # Still under skills root
    assert _skills(cfg).resolve() in dest.resolve().parents


def test_force_overwrites_contained_target(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    dest = _skills(cfg) / "jgs" / SKILL
    dest.mkdir(parents=True)
    stale = dest / "STALE.txt"
    stale.write_text("old", encoding="utf-8")
    rc = _run(["--force"], monkeypatch, home, cfg)
    assert rc == 0
    assert (dest / "SKILL.md").is_file()
    assert not stale.exists()


def test_exists_without_force_errors(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    dest = _skills(cfg) / "jgs" / SKILL
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("x", encoding="utf-8")
    rc = _run([], monkeypatch, home, cfg)
    assert rc != 0
    # Untouched
    assert (dest / "SKILL.md").read_text(encoding="utf-8") == "x"


def test_dry_run_never_deletes(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    dest = _skills(cfg) / "jgs" / SKILL
    dest.mkdir(parents=True)
    keep = dest / "KEEP.txt"
    keep.write_text("keep", encoding="utf-8")
    rc = _run(["--force", "--dry-run"], monkeypatch, home, cfg)
    assert rc == 0
    assert keep.read_text(encoding="utf-8") == "keep"


def test_metadata_build_from_installed_tree(tmp_path, monkeypatch):
    """SC3/SC6: hatchling can see project metadata from the installed copy."""
    home = tmp_path / "home"
    home.mkdir()
    cfg = home / ".claude"
    cfg.mkdir()
    assert _run([], monkeypatch, home, cfg) == 0
    dest = _skills(cfg) / "jgs" / SKILL
    assert (dest / "pyproject.toml").is_file()
    assert (dest / "README.md").is_file()
    # Local metadata build without network or dependency download.
    import subprocess

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-e",
            str(dest),
            "--dry-run",
            "--no-deps",
            "-q",
        ],
        cwd=str(dest),
        capture_output=True,
        text=True,
    )
    # pip dry-run exit 0 means metadata resolved. If the environment's pip
    # lacks dry-run on ancient pip, fall back to a hatchling metadata read.
    if proc.returncode != 0:
        # Fallback for pips without --dry-run: pyproject must parse as TOML.
        import tomllib
        data = tomllib.loads((dest / "pyproject.toml").read_text(encoding="utf-8"))
        assert data["project"]["name"] == "jgs-reference-skill"
        assert data["project"]["readme"] == "README.md"
        assert (dest / "book_to_skill").is_dir()
    else:
        assert proc.returncode == 0
```

Optional extras (nice, not required if the above are green):

- `--namespace jgs` explicit equals default.
- `--agent openclaw` with monkeypatched HOME only (no CLAUDE_CONFIG_DIR reliance).
- Unit tests calling `install.validate_namespace` / `install.assert_under` directly.

Do not require network. Do not install packages into the developer env beyond `--dry-run --no-deps`. Do not touch the real `~/.claude`.

### 3d. Final verification

```bash
python -m pytest -q tests/test_install_containment.py 2>&1 | tail -20
python -m pytest -q 2>&1 | tail -12
for t in vet_source check_overlap outline validate_pack pack_eval; do
  python tools/$t.py --self-check || echo "SELF-CHECK-FAIL $t"
done
# install.py smoke (real dry-run against the developer machine is fine; it must not write):
python install.py --dry-run 2>&1 | head -8
python install.py --namespace 'Bad Slug' --dry-run; echo rc:$?
python install.py --namespace con --list-agents; echo rc:$?
python install.py --flat --dry-run 2>&1 | head -8
```

Expect:

- New module all green.
- Full suite: previous baseline + new tests (target **506 + N** passed, 5 skipped, or the live prior count + N). No new failures outside the known Windows symlink carve-out.
- Five self-checks PASS.
- Bad-namespace smoke exits nonzero; default and flat dry-run exit 0 and print contained targets.

## Acceptance checklist (mirrors spec Success criteria)

| SC | Proof |
|----|--------|
| 1 | Absolute / `../../x` / `Bad Slug` / `con` / empty without `--flat` exit nonzero; decoy-outside-root sentinel intact; nothing created under fake skills root on pure reject |
| 2 | `--dry-run` and `--list-agents` with bad namespace exit nonzero and perform no writes (tests `test_bad_namespace_dry_run_no_writes`, `test_bad_namespace_list_agents_no_writes`) |
| 3 | Default install into temp `CLAUDE_CONFIG_DIR` creates `<cfg>/skills/jgs/jgs-reference-skill/` with `SKILL.md`, `pyproject.toml`, `README.md`; metadata build check (`pip install -e --dry-run --no-deps` or pyproject presence fallback) succeeds |
| 4 | `--flat` lands at `<cfg>/skills/jgs-reference-skill/` (no `jgs/` segment), still under skills root |
| 5 | Contained `--force` overwrites; dry-run never deletes (`test_force_overwrites_contained_target`, `test_dry_run_never_deletes`) |
| 6 | Installed tree has `pyproject.toml` so documented `pip install -e ".[all]"` is viable (file presence + metadata check) |
| 7 | README + docs/skill-usage.md document `BOOK_SKILL_WORKDIR` and `gettempdir()` default (Windows `%TEMP%`); bare `/tmp/book_skill_work` is not the only example |
| 8 | README primary install example is `~/.claude/skills/jgs/jgs-reference-skill/` (namespaced); matches install.py and docs/other-agents.md |
| 9 | SKILL.md names `BOOK_SKILL_WORKDIR` override consistently with config.py |
| 10 | New containment tests green with existing pytest suite; no new runtime dependencies; install.py stays pure stdlib |

## Out of scope (do not touch)

- Transform-agent install formats (a-20)
- build_pack / pack scaffold (P2)
- CI workflow (P1)
- Step 9 gate set beyond the skill-usage "three gates" count fix (P4)
- RELEASE-INFO / release-standard (P6, P9)
- New env vars
- Changing default agent, default namespace `jgs`, licence PAYLOAD entries, or transform render text
- `install.py --self-check`
- Non-stdlib dependencies
- CONTRIBUTING.md beyond an optional one-line workdir mention (not required)
- CHANGELOG (P6/P9)

## Implementer return contract

When done: commit the product + test + doc changes on the working branch, then return status, commit hashes, one-line test summary (pytest passed/skipped + self-check PASS), and any concerns (especially the Windows symlink carve-out if it fired).
