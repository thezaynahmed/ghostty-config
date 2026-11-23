# Security Policy

## Supported Versions

Only the latest `main` branch of `thezaynahmed/ghostty-config` receives security fixes and installer updates.

## Reporting a Vulnerability

Please **do not** open a public GitHub Issue for security vulnerabilities (for example shell injection in `install.sh`, `bin/ghostty-theme`, `bin/ghostty-shell`, Zsh hooks, checksum bypasses, or CI workflow issues).

Report vulnerabilities privately using [GitHub Security Advisories](https://github.com/thezaynahmed/ghostty-config/security/advisories/new) or contact the maintainer via [zainahmed.net](https://zainahmed.net/).

You can expect an initial acknowledgement within 72 hours.

## Security Posture

- **Pinned supply-chain downloads:** Downloaded font archives and pinned CI binaries verify SHA-256 checksums before extraction.
- **Deterministic merge gates:** Branch ruleset `26415451` blocks direct pushes and force pushes to `main` and requires `zsh-and-shell-icons` CI to pass on an up-to-date branch.
- **Automated scanning:** GitHub CodeQL (`actions`, `python`), Secret Scanning with Push Protection, and Dependabot security updates are enabled.
- **Maintainer approval:** All pull requests are reviewed by `@thezaynahmed` via `.github/CODEOWNERS`. Full governance details live in [`docs/security-and-review.md`](docs/security-and-review.md).
