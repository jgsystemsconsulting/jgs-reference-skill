# Copyright (c) 2026 JG Systems Consulting Ltd. See LICENSE.
# SPDX-License-Identifier: MIT
"""Token / boundary matcher for vet_source permissive-family branch.

Covers spec 2026-09-24-vet-licence-token-match Success criteria 1-7 at
classify level, plus a build_pack e2e for SC6.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_pack  # noqa: E402
import vet_source  # noqa: E402
from validate_pack import parse_simple_yaml  # noqa: E402

T2 = dict(license_tier=2, commercial_use=True, share_alike=False,
          attribution_required=True, excluded=False)


def _t2(v: dict) -> None:
    for k, exp in T2.items():
        assert v[k] is exp or v[k] == exp, (k, v[k], exp, v)


@pytest.mark.parametrize("lic", [
    "limitations of liability apply",
    "reviewed by committee",
    "may be distributed under site terms",
])
def test_sc1_sc2_false_positives_and_token_free(lic):
    v = vet_source.classify("Some Guide", "Author", lic)
    assert v["excluded"] is False
    assert v["license_tier"] == 3
    assert v["commercial_use"] is False


@pytest.mark.parametrize("lic", [
    "MIT",
    "Apache 2.0",
    "BSD 3-Clause",
    "MIT-style",
    "FreeBSD license",
    "MIT licence",
    "Apache Licence 2.0",
])
def test_sc3_true_grants(lic):
    _t2(vet_source.classify("Some Guide", "Author", lic))


@pytest.mark.parametrize("lic", [
    "MIT for non-commercial use only",
    "noncommercial MIT variant",
    "MIT, commercial use prohibited",
    "MIT; no commercial restrictions",
    "MIT NC",
    "licence nc only",
    "MIT, commercial use not allowed",
])
def test_sc3b_negated_grants(lic):
    v = vet_source.classify("Some Guide", "Author", lic)
    assert v["commercial_use"] is False
    assert v["license_tier"] == 3
    assert v["excluded"] is False


@pytest.mark.parametrize("title,publisher,lic", [
    ("AFOTEC CERT Guide", "AFOTEC", ""),
    ("Defense Acquisition Guidebook", "DoD", ""),
    ("DoD DAG summary", "OUSD", ""),
    ("SEI Technical Report", "Carnegie Mellon University", ""),
    ("CMU report", "Software Engineering Institute", ""),
])
def test_sc4_excluded_unchanged(title, publisher, lic):
    v = vet_source.classify(title, publisher, lic)
    assert v["excluded"] is True
    assert v["license_tier"] is None
    assert v["excluded_reason"]


def test_sc4_prior_self_check_rows_and_sebok():
    rows = [
        ("ISO/IEC/IEEE 15288", "ISO", "", True, None),
        ("SysML v2", "Object Management Group", "OMG Specification License", True, None),
        ("INCOSE SE Handbook", "Wiley", "", True, None),
        ("SE Handbook", "NASA", "Public Domain (US Government work)", False, 1),
        ("DoD SE Guidebook", "OUSD R&E", "Distribution A", False, 1),
        ("SEBoK", "BKCASE / Stevens", "CC BY-NC-SA 3.0", False, 2),
        ("Some Guide", "Author", "CC BY-ND 4.0", False, 3),
        ("Mystery Doc", "Random Blog", "freely available", False, 3),
    ]
    for title, pub, lic, exp_excl, exp_tier in rows:
        v = vet_source.classify(title, pub, lic)
        assert v["excluded"] is exp_excl and v["license_tier"] is exp_tier, (title, v)
    sebok = vet_source.classify("SEBoK", "Stevens", "CC BY-NC-SA 3.0")
    assert sebok["commercial_use"] is False and sebok["share_alike"] is True


def test_sc5_self_check_exit_zero():
    assert vet_source._self_check() == 0


def test_sc4_excluded_reasons_exact():
    from vet_source import classify
    # Frozen literals copied from tools/vet_source.py EXCLUDED at plan time.
    EXPECTED_REASONS = {
        ("Air Force Civil Engineering Center report", "AFOTEC"):
            "AFOTEC OT&E / CERT products are not a redistribution grant for this library",
        ("Defense Acquisition Guidebook", "DoD DAG"):
            "DAG is not packageable here",
        ("SEI handbook", "Carnegie Mellon Software Engineering Institute"):
            "SEI technical reports are not a blanket redistribution grant",
    }
    for title, publisher, license in [
        ("Air Force Civil Engineering Center report", "AFOTEC", "MIT"),
        ("Defense Acquisition Guidebook", "DoD DAG", "MIT"),
        ("SEI handbook", "Carnegie Mellon Software Engineering Institute", "MIT"),
    ]:
        v = classify(title, publisher, license)
        assert v["excluded"] is True
        # reason text frozen to the current strings (a swap between titles must fail)
        assert v["excluded_reason"] == EXPECTED_REASONS[(title, publisher)]


def test_sc7_stdlib_only():
    import ast, sys as _sys
    src = (REPO_ROOT / "tools" / "vet_source.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    stdlib = set(_sys.stdlib_module_names)
    local = {"vet_source"}
    assert imported <= stdlib | local, imported - stdlib - local


def test_sc6_build_pack_mit_e2e(tmp_path):
    out_dir = tmp_path / "packs"
    slug = "mit-token-match-demo"
    argv = [
        "build_pack.py",
        "--slug", slug,
        "--out-dir", str(out_dir),
        "--title", "Token Match Handbook",
        "--publisher", "Example Press",
        "--version", "1st ed. (2026)",
        "--license", "MIT",
    ]
    rc = build_pack.main(argv)
    assert rc == 0
    meta = parse_simple_yaml((out_dir / slug / "PACK.yaml").read_text(encoding="utf-8"))
    # parse_simple_yaml returns strings only (no typed ints/bools), so compare as strings
    assert meta["commercial_use"] == "true"
    assert meta["license_tier"] == "2"
