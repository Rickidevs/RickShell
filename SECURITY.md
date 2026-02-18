# Security Policy

## ⚠️ Important Notice

RickShell is a penetration testing and red team tool. It is designed exclusively for use on systems you own or have **explicit written authorization** to test. Unauthorized use against third-party systems is illegal and unethical.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest (main) | ✔ |
| Older releases | ✘ |

Only the latest version on the `main` branch receives security updates.

---

## Reporting a Vulnerability

If you discover a security vulnerability in RickShell itself (e.g. unintended code execution on the attacker machine, insecure defaults, dependency issues), please report it responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

### How to report

1. Open a **private** GitHub Security Advisory via the [Security tab](../../security/advisories/new) of this repository.
2. Include the following information:
   - A clear description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your suggested fix (if any)

You can expect an initial response within **72 hours**.

---

## Scope

The following are considered in-scope for vulnerability reports:

- Remote code execution on the **attacker machine** (the machine running RickShell)
- Privilege escalation caused by RickShell itself
- Insecure handling of session data or socket connections
- Dependency vulnerabilities with direct exploitability

The following are **out of scope:**

- Vulnerabilities in payloads executed on target machines (that is the intended functionality)
- Issues arising from use on systems without authorization
- Social engineering of the maintainers

---

## Responsible Use

By using RickShell you agree to:

- Only use this tool on systems you own or have **explicit written permission** to test
- Comply with all applicable local, national, and international laws
- Not use this tool to cause harm, disrupt services, or compromise systems without authorization

The authors of RickShell are not responsible for any damage or legal consequences resulting from misuse of this software.

---

## Dependencies

RickShell depends on the following third-party library:

| Package | Purpose |
|---------|---------|
| `psutil` | Network interface detection |

Keep dependencies up to date. You can check for outdated packages with:

```bash
pip3 list --outdated
```
