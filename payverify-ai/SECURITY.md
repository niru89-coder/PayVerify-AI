# Security Policy

## Supported versions

PayVerify AI is currently pre-1.0 and under active development. Only the latest commit on
`main` receives security fixes.

| Version | Supported |
|---|---|
| `main` (latest) | ✅ |
| Older tagged releases | ❌ |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, report privately via one of:

- GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing/privately-reporting-a-security-vulnerability)
  feature on this repository (Security tab → "Report a vulnerability"), or
- Email the maintainer directly at: `niru.rajavel@gmail.com` (update this
  before the repo goes public).

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce (proof-of-concept if possible)
- Any relevant logs/screenshots (redact real employee/payroll data)

We aim to acknowledge reports within 5 business days and to provide a remediation timeline
within 14 days of confirming the issue.

## Scope notes specific to this project

- PayVerify AI processes payroll data, which may include personally identifiable information
  (PII) such as national ID numbers, salaries, and bank details in uploaded CSVs. Any
  vulnerability that could expose this data (e.g. path traversal in the upload handlers,
  SQL injection, missing authentication/authorization on data-access endpoints, SSRF via the
  Claude API integration) is considered **high severity**.
- The current MVP has **no authentication/authorization layer** — this is a known,
  intentionally scoped limitation (see README "Known limitations"), not something you need to
  separately report, but please do not deploy a build without auth in front of real employee
  payroll data.
- Claude (Anthropic) API usage is scoped to variance-explanation text only; the AI Gateway
  (Phase 3.5) enforces that raw payroll registers/PII are never sent to the Claude API. A
  vulnerability that bypasses that data-minimization boundary is high severity.
