# Spec: P5 install-containment-and-docs

- date: 2026-09-24
- project: jgs-reference-skill
- package: P5 (docs/superpowers/packages/2026-09-24-jgs-reference-skill-packages.md)
- author-leaf: fallback (inline); Claude-pinned leaf unavailable; constraints locked at the package proposal stop
- context: ad-hoc (P5 package section; findings I3 and I4; current files read in full: install.py 171 lines, book_to_skill/config.py OUTPUT_DIR/BOOK_SKILL_WORKDIR, README.md Install and CLI Usage, docs/skill-usage.md, docs/other-agents.md path table, SKILL.md Prerequisites and Step 2 workdir wording, pyproject.toml payload relevance, tests/test_build_pack_scaffold.py as the containment-test pattern to mirror; line citations below verified against the tree after P1-P4, not the original review snapshot)
- research: skipped (internal tool hardening and doc consistency; no external APIs, libraries, or version-sensitive choices)

## Research

research: skipped (internal tool hardening and doc consistency; no external APIs, libraries, or version-sensitive choices)

## Problem

`install.py` is the public install entrypoint (RR-S-02/03/15). Three independent gaps make a "successful" install unsafe or unusable, and the onboarding docs disagree with both the installer and the engine.

### (a) Uncontained namespace + force rmtree (I4 path half)

Native targets are built by joining a raw `--namespace` (default `jgs`) under each agent's skills root, with no token check and no resolve-and-contain gate:

```
# install.py L45-47, L52-58, L146-158 (verified)
def claude_home() -> Path:
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(cfg) if cfg else HOME / ".claude"

"claude":  target=lambda ns: claude_home() / "skills" / ns / SKILL
"openclaw": target=lambda ns: HOME / ".openclaw" / "skills" / ns / SKILL
"copilot":  target=lambda ns: HOME / ".copilot" / "skills" / ns / SKILL

ns = "" if args.flat else args.namespace  # pathlib drops the empty segment
target = a["target"](ns)
```

`install_native` then, on a non-dry run when the target already exists, deletes it before rewriting:

```
# install.py L97-105 (verified)
if target.exists() and not force and not dry:
    raise SystemExit(f"ERROR: {target} exists (use --force to overwrite).")
if dry:
    print(f"  would copy {len(PAYLOAD)} item(s) → {target}")
    return
if target.exists():
    shutil.rmtree(target)
target.mkdir(parents=True)
```

`--force` is required only to pass the exists guard; once past that guard, `rmtree` runs for any existing target on a real install. Combined with an unsanitized `ns`:

1. `--namespace /tmp/evil` (or any absolute segment): pathlib discards the left operand on an absolute right path, so the target becomes `/tmp/evil/jgs-reference-skill` (or the Windows equivalent) and `--force` can `rmtree` it.
2. `--namespace ../../outside`: the joined path resolves outside the skills directory; same destructive rewrite.
3. `$CLAUDE_CONFIG_DIR` is an intentional relocate of Claude's config home (documented, keep). Containment must still hold **under** that home's `skills/` root after resolve. A hostile or mistaken namespace must not walk out of `skills/` even when the home itself is relocated.

Gemini transform paths also embed `ns` (`~/.gemini/commands/<ns>/jgs-reference-skill.toml`). Codex and Cursor targets do not use `ns` in the path. Transform installs only `write_text` a single file (no `rmtree`), but a bad namespace can still place that file outside the intended commands tree. Namespace validation therefore applies once at CLI parse time for every agent; path containment is checked per target before any write or delete.

`--flat` sets `ns = ""` so pathlib drops the namespace segment and installs at `<skills-root>/jgs-reference-skill`. That is a supported, contained layout and must keep working.

`SECURITY.md` scopes "any tool that writes outside the intended pack/skill directory" as in-scope. The installer is that skill-directory write path.

### (b) PAYLOAD omits pyproject.toml (I4 payload half)

```
# install.py L37-40 (verified)
PAYLOAD = ["SKILL.md", "scripts", "tools", "book_to_skill", "docs", "templates",
           "LICENSE", "NOTICE", "ATTRIBUTION.md"]
```

Native install copies those items only. Repo meta intentionally stays out (comment L37-38). `pyproject.toml` is not meta-only: it defines the editable package and the `[all]` extras that extraction depends on.

Documented prerequisite (still current):

- `SKILL.md` Prerequisites: `` `pip install -e ".[all]"` for every format ``
- `docs/skill-usage.md` Prerequisites: same
- `CONTRIBUTING.md`: same for contributor setup

From an installed skill tree (no `pyproject.toml`), `pip install -e ".[all]"` fails. Operators and agents following SKILL.md after a default install hit a dead end; only `--install-missing` per package remains. `book_to_skill/` is already in PAYLOAD; hatchling packages that tree (`pyproject.toml` `[tool.hatch.build.targets.wheel] packages = ["book_to_skill"]`). Adding `pyproject.toml` is the missing piece for editable install from the installed copy. Do not add CI, landing page, or the installers themselves to PAYLOAD.

### (c) Doc path drift (I3)

Two onboarding lies, still present after P1-P4:

1. **Install path.** README Install (L51) correctly says namespaced under `~/.claude/skills/jgs/`. A later README paragraph (L115-116) still says install at `~/.claude/skills/jgs-reference-skill/` with no vendor namespace. `docs/other-agents.md` L12 already documents the correct `~/.claude/skills/<ns>/jgs-reference-skill/` form. Copy-paste from the later README paragraph lands the skill where the host will not discover the namespaced default.

2. **Workdir path.** README CLI Usage (L106, L109) and `docs/skill-usage.md` (L59-60) hard-code `/tmp/book_skill_work/...`. The engine does not:

```
# book_to_skill/config.py L5-10 (verified)
OUTPUT_DIR = Path(
    os.environ.get(
        "BOOK_SKILL_WORKDIR",
        str(Path(tempfile.gettempdir()) / "book_skill_work"),
    )
)
```

Default is `tempfile.gettempdir()/book_skill_work` (`/tmp/...` on many Unix hosts, `%TEMP%\book_skill_work` on Windows), overridable via `BOOK_SKILL_WORKDIR`. No current doc names that variable. SKILL.md Step 2 (L116) already uses the honest form `<tempdir>/book_skill_work/{full_text.txt,metadata.json}`; README and skill-usage do not. Copy-paste CLI runs on Windows chase a missing `full_text.txt`.

## Current structure (normative baseline for Goals)

Verified against `install.py` as of this spec (171 lines). Goals change this structure only where named.

| Piece | Current behaviour |
|---|---|
| `SKILL`, `NS`, `ROOT`, `HOME` | constants; `NS = "jgs"` |
| `PAYLOAD` | 9 entries listed above; dirs copytree with `__pycache__`/`*.pyc` ignore; missing src skipped |
| `claude_home()` | `$CLAUDE_CONFIG_DIR` or `~/.claude` |
| `AGENTS` | 6 agents; native: claude/openclaw/copilot; transform: codex (md), gemini (toml under ns), cursor (mdc, project-local, `in_all=False`) |
| `target(ns)` | lambda per agent; empty `ns` drops the segment |
| `install_native` | exists+!force+!dry → SystemExit; dry → print and return (no FS effect); else rmtree if exists, mkdir, copy PAYLOAD |
| `install_transform` | same exists guard; dry print; else parent mkdir + write_text rendered prompt |
| CLI | `--agent`, `--namespace` (default jgs), `--flat`, `--dry-run`, `--force`, `--list-agents` |
| Namespace validation | none |
| Containment | none |
| Exit | 0 success; `SystemExit` string errors from install_*; argparse errors otherwise |

No separate skills-root helper exists today. build_pack already ships the containment pattern this package should mirror (kebab regex, Windows reserved names, resolve parent, resolve join, require parent in `result.parents`, reject before any FS effect): `tools/build_pack.py` L42-46 and L134-145. Reuse the same rules for `--namespace` where they fit; do not import build_pack into install.py (install stays standalone stdlib at repo root).

## Goals

### 1. Namespace token gate (before any agent loop body does work)

When `--flat` is **not** set, validate `args.namespace` before resolving any target, listing agents, or installing:

1. **Kebab-case token** (same regex build_pack uses for slug): `^[a-z0-9]+(-[a-z0-9]+)*$`. Reject empty string, absolute paths, `.`, `..`, separators (`/`, `\`), whitespace, uppercase, underscores, dots-as-extension, and any other non-kebab form.
2. **Windows reserved device names**, case-insensitive, on the full token and on each hyphen-separated segment: `con`, `prn`, `aux`, `nul`, `com1`-`com9`, `lpt1`-`lpt9`.
3. On failure: print a clear ERROR to stderr naming the rule and the bad value, exit **nonzero**, create nothing, delete nothing. Applies to `--list-agents`, `--dry-run`, and real installs alike (validation is not skipped for dry-run or list).

When `--flat` **is** set: ignore `--namespace` for path building (keep today's `ns = ""` behaviour). Do not require the namespace flag to be valid under `--flat` (operators may pass anything unused, or omit it). Flat install target is `<agent-skills-or-commands-root>/jgs-reference-skill` (or the transform file path with no ns segment), which is contained by construction once Goal 2 holds.

Default `--namespace jgs` remains valid and is the documented default.

### 2. Resolve-and-contain every install target before mkdir/rmtree/write

After the token gate (or flat short-circuit), for **each** chosen agent:

1. Compute the target the same way today's lambdas do (no change to the intended layout for valid inputs).
2. **Resolve** the target with `Path.resolve()` (non-existent parents are fine on modern pathlib).
3. Compute the **containing root** for that agent kind and resolve it:
   - native claude: `(claude_home() / "skills").resolve()` (resolve the full path, matching the other roots, so a symlinked skills directory still passes containment)
   - native openclaw: `(HOME / ".openclaw" / "skills").resolve()`
   - native copilot: `(HOME / ".copilot" / "skills").resolve()`
   - transform gemini: `(HOME / ".gemini" / "commands").resolve()`
   - transform codex: `(HOME / ".codex" / "prompts").resolve()` (file lives directly here; ns unused)
   - transform cursor: `(Path.cwd() / ".cursor" / "rules").resolve()`
4. **Containment rule:** the resolved target must be a strict descendant of the containing root (`containing_root` in `target.parents`; never equal to the root, never outside). **Validate every chosen target first, then install** — a containment failure anywhere in a multi-agent `--agent all` run fails the whole `main` before any agent write, so no partial installs are possible. There is no sequential install-and-hope option.
5. Only after containment passes: call today's `install_native` / `install_transform` unchanged in force/dry/copy semantics. Residual note: containment is check-then-act, so a mid-component symlink swapped between check and delete is theoretically possible; that race is accepted under this tool's single-user, local-machine threat model and is not addressed here.

`$CLAUDE_CONFIG_DIR` stays honoured: relocating Claude home relocates the skills root; namespace still cannot escape that root. Openclaw/copilot/gemini/codex homes stay under `Path.home()` as today (no new env overrides in this package).

`--force` semantics for **contained** targets are preserved exactly: existing contained target + `--force` + not dry → `rmtree` then rewrite; existing + not force + not dry → SystemExit exists error; dry-run never deletes or writes.

### 3. Add `pyproject.toml` to PAYLOAD

Insert `"pyproject.toml"` **and** `"README.md"` into the `PAYLOAD` list. pyproject declares `readme = "README.md"`, so shipping pyproject without README still aborts the hatchling metadata build and `pip install -e` from the installed tree stays broken. `install_native` already copies files via `copy2` when `src.is_file()`.

After install, from the installed skill directory, `pip install -e ".[all]"` must be able to see the project metadata and the `book_to_skill` package (already copied). Do not expand PAYLOAD to tests, CI, installers, packs, or the landing page. Do not change hatch build config in this package.

Comment above PAYLOAD stays accurate: update it only if needed so it does not claim pyproject is excluded.

### 4. Docs consistency (exact file list)

Truthful install-path form and workdir form everywhere operators copy from. Written prose standard applies (no em dashes, staff-engineer voice).

| File | Required edits |
|---|---|
| `README.md` | (1) CLI Usage blocks that cite `/tmp/book_skill_work/...` (outline + check_overlap lines): replace with a form that matches the engine. Prefer a short note that extract writes to `tempfile.gettempdir()/book_skill_work` (Windows: under `%TEMP%`), overridable with `BOOK_SKILL_WORKDIR`, then show commands using a placeholder such as `$BOOK_SKILL_WORKDIR/full_text.txt` or `<workdir>/full_text.txt` with workdir defined one line above. Do not leave bare `/tmp/book_skill_work` as the only example. (2) The paragraph that says install at `~/.claude/skills/jgs-reference-skill/`: change to the namespaced default `~/.claude/skills/jgs/jgs-reference-skill/` (and optionally note `--flat` drops `jgs/`). Leave the Install section's already-correct namespaced line intact unless wording must align. |
| `docs/skill-usage.md` | Same workdir fix for the Running-the-tools-directly block (`/tmp/book_skill_work` on outline and check_overlap). One sentence on `BOOK_SKILL_WORKDIR` and the `gettempdir()` default. Install section already namespaced; keep it. |
| `docs/other-agents.md` | Path table already correct (`<ns>` default `jgs`). Touch only if a one-line note is needed that `--namespace` must be a single kebab-case token (no `..`, no absolute path), or if any residual non-namespaced example appears. Do not redesign the transform-agent limitation section (a-20 stays as-is). |
| `SKILL.md` | Step 2 already uses `<tempdir>/book_skill_work`. Add a brief mention that the directory is `BOOK_SKILL_WORKDIR` if set, else `tempfile.gettempdir()/book_skill_work`, so agents do not invent `/tmp/...` on Windows. Prerequisites `pip install -e ".[all]"` stays; it becomes true for installed trees once Goal 3 lands. Do not rework Step 9 or gate counts here (P4 owns those). |

Do not rewrite CONTRIBUTING beyond what a one-line workdir mention would need; CONTRIBUTING's pip line is clone-from-repo oriented and already valid at repo root. No CHANGELOG requirement in this package (release notes are P6/P9 territory unless the implementer is already there).

### 5. Regression coverage (existing test style)

Add a focused pytest module (suggested name `tests/test_install_containment.py`) mirroring `tests/test_build_pack_scaffold.py`:

- Import `install` from repo root via `sys.path` insert of `REPO_ROOT` (install.py lives at root, not under tools/).
- Drive `install.main(argv)` with a temp home: monkeypatch `install.HOME` and/or `os.environ["CLAUDE_CONFIG_DIR"]` to paths under `tmp_path` so tests never touch the real user profile.
- **Reject and no FS effect** (exit nonzero; nothing created or deleted outside the fake skills root; preferably nothing created under it either for pure rejection cases):
  - `--namespace` absolute path (use a guaranteed-absent absolute under `tempfile.gettempdir()` + uuid, same pattern as build_pack's absolute slug test)
  - `--namespace ../../x` or similar dot-dot
  - `--namespace "Bad Slug"` / underscores / empty string without `--flat`
  - `--namespace con` (Windows reserved)
  - At least one case with `--force` and a pre-existing decoy **outside** the skills root that would have been the rmtree target under the old join semantics: after the rejected run the decoy must still exist and be untouched
- **Happy paths unchanged:**
  - default `namespace=jgs` dry-run against fake CLAUDE_CONFIG_DIR prints the contained target and writes nothing
  - real install (no dry) of default namespace into fake home creates `skills/jgs/jgs-reference-skill/SKILL.md` and includes `pyproject.toml` in the installed tree
  - `--flat` installs to `skills/jgs-reference-skill/` (no `jgs/` segment) and still contains under skills root
  - `--force` on an existing **contained** target replaces it successfully (rmtree+rewrite semantics preserved)
- Do not require network, pip, or real agent hosts.

## Non-goals

- Transform-agent install format redesign (a-20; docs/other-agents.md limitation text stays).
- build_pack / pack scaffold work (P2, done).
- CI workflow (P1, done).
- Step 9 gate set, pack_eval, scan_generated_skill (P4, done). skill-usage.md's overview list still says "three gates" (stale since P4): fix that count unconditionally while editing the file for workdir text (one line).
- RELEASE-INFO / release-standard (P6, P9).
- New env vars beyond documenting the existing `BOOK_SKILL_WORKDIR` and existing `CLAUDE_CONFIG_DIR`.
- Changing default agent, default namespace `jgs`, PAYLOAD licence files, or transform render text.
- Adding argparse `--self-check` to install.py.
- Real YAML libraries, path libraries beyond stdlib `pathlib`, or any non-stdlib dependency.

## Constraints (locked)

1. Pure stdlib only in `install.py` (already true; keep it).
2. No behaviour change for valid default installs: `python install.py`, `python install.py --agent all`, valid `--namespace jgs`, `--flat`, `--dry-run`, and contained `--force` overwrite match today's outcomes aside from the additive `pyproject.toml` copy.
3. `--force` semantics preserved for contained targets (exists guard, rmtree, rewrite).
4. `$CLAUDE_CONFIG_DIR` remains the Claude home relocate; containment is under its `skills/` child.
5. Namespace rules align with build_pack's slug gate where applicable (kebab + Windows reserved) so operators learn one token language; install does not import tools/build_pack.py.
6. Written prose standard on docs this package edits: no em dashes, staff-engineer voice, avoid-ai-writing bar on durable prose.
7. Fewest files that close the gaps: `install.py`, one new test module, and the doc files in Goal 4.

## Success criteria

1. `python install.py --namespace /tmp/evil --force` (and Windows-absolute equivalents in tests), `--namespace ../../x --force`, `--namespace "Bad Slug"`, `--namespace con`, and `--namespace ""` without `--flat` each exit nonzero with a clear error, create nothing under the skills root, and delete nothing outside it (decoy-outside-root test proves no rmtree).
2. `python install.py --dry-run` and `python install.py --list-agents` with a bad namespace also exit nonzero and perform no writes. Goal 5's test list gains this case explicitly (the current `--list-agents` path early-returns before namespace use; the test must prove validation now runs on that path too).
3. Default install into a temp `CLAUDE_CONFIG_DIR` creates `<cfg>/skills/jgs/jgs-reference-skill/` containing `SKILL.md`, `pyproject.toml`, and `README.md` (plus the rest of today's PAYLOAD that exists at repo root); a metadata build check (`python -m pip install -e <installed> --dry-run --no-deps -q` or equivalent local build of the metadata) succeeds from the installed tree.
4. `--flat` install lands at `<cfg>/skills/jgs-reference-skill/` (contained), not under a namespace segment.
5. Contained `--force` overwrites an existing install directory successfully; dry-run never deletes.
6. From the installed tree, `pyproject.toml` is present so `pip install -e ".[all]"` is a viable documented path (test checks file presence; full pip invoke is optional).
7. README and docs/skill-usage.md no longer prescribe bare `/tmp/book_skill_work` as the only workdir; both document `BOOK_SKILL_WORKDIR` and the `gettempdir()` default (Windows `%TEMP%` called out).
8. README no longer advertises `~/.claude/skills/jgs-reference-skill/` as the primary install example without the `jgs/` namespace; namespaced form matches install.py and docs/other-agents.md.
9. SKILL.md names the workdir override consistently with config.py.
10. New containment tests green with the existing pytest suite; no new runtime dependencies.

## Recommended implementation shape (not sacred if behaviour holds)

```python
_NS_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_WINDOWS_RESERVED = {"con", "prn", "aux", "nul",
                     *(f"com{i}" for i in range(1, 10)),
                     *(f"lpt{i}" for i in range(1, 10))}

def validate_namespace(ns: str) -> None:
    if not _NS_RE.fullmatch(ns):
        raise SystemExit(f"ERROR: --namespace must be kebab-case ..., got: {ns!r}")
    if any(s.lower() in _WINDOWS_RESERVED for s in [ns, *ns.split("-")]):
        raise SystemExit(f"ERROR: --namespace must not use a Windows reserved ...")

def assert_under(root: Path, target: Path) -> None:
    root_r, tgt_r = root.resolve(), target.resolve()
    if root_r == tgt_r or root_r not in tgt_r.parents:
        raise SystemExit(f"ERROR: install target must resolve strictly under {root_r}, got: {tgt_r}")
```

Call `validate_namespace` once when not `--flat`. Two passes over the chosen agents: pass one derives `containing_root`, computes `target`, and runs `assert_under(containing_root, target)` for **every** chosen agent; pass two (only after every check passed) installs. PAYLOAD gains `"pyproject.toml"` and `"README.md"`.

## Out of scope (explicit)

Transform-agent install formats (a-20), build_pack (P2), CI (P1), Step 9 (P4), RELEASE-INFO (P6), website alignment (P8), release-repo-standard pass (P9).
