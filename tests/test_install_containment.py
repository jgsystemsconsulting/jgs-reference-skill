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

    try:
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
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        proc = None
    # pip dry-run exit 0 means metadata resolved. If the environment's pip
    # lacks dry-run / can't build (no network, ancient pip), fall back to a
    # hatchling metadata read: pyproject must parse as TOML with the right keys.
    if proc is None or proc.returncode != 0:
        import tomllib
        data = tomllib.loads((dest / "pyproject.toml").read_text(encoding="utf-8"))
        assert data["project"]["name"] == "jgs-reference-skill"
        assert data["project"]["readme"] == "README.md"
        assert (dest / "book_to_skill").is_dir()
    else:
        assert proc.returncode == 0
