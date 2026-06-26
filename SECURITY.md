<!-- Copyright (c) 2026 JG Systems Consulting Ltd. MIT License (see LICENSE). SPDX-License-Identifier: MIT -->

# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ |

Only the latest released `0.x` line receives security fixes.

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Report it privately through GitHub: open a
[security advisory](https://github.com/jgsystemsconsulting/jgs-reference-skill/security/advisories/new)
on this repository (**Security** tab, then **Report a vulnerability**). Include:

- a description of the issue and its impact,
- steps to reproduce (a proof-of-concept if you have one),
- the affected file(s)/version.

You can expect an acknowledgement within **5 working days** and an assessment with a
remediation plan or a reasoned dismissal within **15 working days**. Please keep the
report private until a fix is released (coordinated disclosure).

This is a report-only policy: there is **no bug-bounty or paid reward** programme.

## Scope

This repository is a local developer/agent tool. The most relevant classes of issue:

- the text-extraction engine processes untrusted documents (parser crashes,
  resource exhaustion, or path-traversal on output) are in scope;
- any tool that writes outside the intended pack/skill directory;
- supply-chain concerns in the optional extraction dependencies.

Out of scope: vulnerabilities in the third-party source documents you choose to feed
the tool, and in the optional dependencies' own upstreams (report those upstream).
