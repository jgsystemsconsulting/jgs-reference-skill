# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Regression tests: validate_pack rejects unfilled scaffolds, passes filled ones.

Covers spec 2026-09-24-pack-scaffold-provenance criterion 5:
  - a fresh non-signpost scaffold fails validation, with findings naming the
    TODO marker, the zero build counters, and the LICENSE stub line;
  - the normative simulated-fill fixture passes with zero findings;
  - signpost packs skip the marker checks entirely (existing structural rules
    still apply).
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_pack  # noqa: E402
import validate_pack  # noqa: E402

OUT_DIR = "packs"
# Clean Tier-1 triple: no Excluded substring, no vetting warnings, no --force.
CLEAN = {
    "title": "Fill Demo Handbook",
    "publisher": "Example Press",
    "version": "1st ed. (2020)",
    "license": "Public Domain (US Government work)",
}
FILLED_PACK_YAML = """\
slug: fill-demo
title: "Fill Demo Handbook"
publisher: "Example Press"
source_version: "1st ed. (2020)"
license: "Public Domain (US Government work)"
license_tier: 1
commercial_use: true
share_alike: false
attribution_required: false
build:
  method: "jgs-reference-skill: vendored book-to-skill extraction + offset-mapped chapter synthesis"
  source_pages: 12
  chapters: 3
  built_on: "2026-09-24"
notes: >
  Derived from a US Government public-domain work; the licence carries no
  conditions to forward. Attribution courtesy note kept. Synthesised reference
  notes only; no long verbatim passages (verify with tools/check_overlap.py).
"""
FILLED_LICENSE = """\
fill-demo pack - content licence

Derived from:
    Fill Demo Handbook
    Example Press, 1st ed. (2020)

Source licence: Public Domain (US Government work). Reproduced terms: this is a
work of the United States Government placed in the public domain worldwide; it
may be reproduced, distributed, and adapted without permission. A courtesy
attribution note is retained in PACK.yaml.
"""
SIGNPOST_PACK_YAML = """\
kind: signpost
slug: sign-demo
title: "Locked Standard"
publisher: "Standards Consortium"
license: "All rights reserved (no redistribution grant)"
license_tier: 3
commercial_use: false
share_alike: false
attribution_required: true
build:
  method: "signpost: citation-only"
  source_pages: 0
  chapters: 0
  built_on: "TODO"
notes: >
  TODO: signpost pack; cite the owner and point to the official source.
"""


def scaffold(tmp_path, slug, **overrides):
    """Successful build_pack scaffold; returns the pack directory."""
    argv = ["build_pack.py", "--slug", slug, "--out-dir", str(tmp_path / OUT_DIR)]
    for key, value in {**CLEAN, **overrides}.items():
        argv += [f"--{key.replace('_', '-')}", value]
    rc = build_pack.main(argv)
    assert rc == 0, f"build_pack failed with rc={rc}"
    return tmp_path / OUT_DIR / slug


def write_minimal_skill(pack_dir, slug):
    """Minimal SKILL.md + one chapter so only the marker findings remain."""
    (pack_dir / "SKILL.md").write_text(
        f"---\nname: {slug}\ndescription: Minimal generated skill body.\n---\n"
        "## Chapter Index\n| 1 | Intro | [ch01](chapters/ch01-example.md) |\n",
        encoding="utf-8")
    (pack_dir / "chapters" / "ch01-example.md").write_text(
        "# Chapter 1\n\nSynthesised reference notes.\n", encoding="utf-8")


def test_fresh_scaffold_fails_validate_naming_markers(tmp_path):
    pack = scaffold(tmp_path, "fresh-demo")
    write_minimal_skill(pack, "fresh-demo")
    errors = validate_pack.check_pack(pack)
    assert errors, "unfilled scaffold must fail validation"
    assert any("unfilled TODO marker" in e for e in errors)
    assert any("source_pages still 0" in e for e in errors)
    assert any("chapters still 0" in e for e in errors)
    assert any("LICENSE" in e and "TODO: reproduce" in e for e in errors)


def test_simulated_fill_fixture_passes(tmp_path):
    pack = scaffold(tmp_path, "fill-demo")
    write_minimal_skill(pack, "fill-demo")
    # The unfilled scaffold from step 1 must fail before the fill.
    assert validate_pack.check_pack(pack), "unfilled scaffold must fail"
    (pack / "PACK.yaml").write_text(FILLED_PACK_YAML, encoding="utf-8")
    (pack / "LICENSE").write_text(FILLED_LICENSE, encoding="utf-8")
    assert validate_pack.check_pack(pack) == []


def test_signpost_skips_marker_checks(tmp_path):
    pack = tmp_path / OUT_DIR / "sign-demo"
    pack.mkdir(parents=True)
    (pack / "PACK.yaml").write_text(SIGNPOST_PACK_YAML, encoding="utf-8")
    (pack / "SKILL.md").write_text(
        "---\nname: sign-demo\ndescription: Citation-only signpost to a locked standard.\n---\n"
        "Cite and point to the owner; no reproduced content.\n", encoding="utf-8")
    # SKILL.md + PACK.yaml only (no chapters/, no LICENSE), PACK.yaml carries
    # TODO and zero counters -- signpost packs must pass structural checks and
    # must not trigger the marker findings.
    assert validate_pack.check_pack(pack) == []
    # Negative half: the signpost exemption skips marker checks only, not the
    # structural rules.
    (pack / "SKILL.md").unlink()
    assert "missing SKILL.md" in validate_pack.check_pack(pack)
