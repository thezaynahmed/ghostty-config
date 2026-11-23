# Contributing

Contributions, contrast audits, bug fixes, and new terminal/editor adapters are welcome. This project follows strict engineering standards: small focused PRs, reproducible tests, shell safety (`set -euo pipefail`, proper quoting), and explicit maintainer approval.

## Governance & Pull Request Approval

- Every pull request is reviewed and approved by the maintainer (`@thezaynahmed`, [zainahmed.net](https://zainahmed.net/)) via `.github/CODEOWNERS`.
- Keep each PR focused on a single clear change and explain **why** in the commit message and PR description.
- Never weaken branch protection rules or bypass CI checks.

## Adding or Tuning a Theme / Adapter

1. Place custom Ghostty theme files in [`themes/`](themes/) using Ghostty's `palette = N=#hex` format.
2. Verify primary foreground contrast (`>= 4.5:1` WCAG 2.1, aiming AAA `>= 7:1`) and red/green hue separation (`>= 110 deg`).
3. Place new terminal or editor adapters under [`adapters/`](adapters/) and document them in [`README.md`](README.md) and [`AGENTS.md`](AGENTS.md).
4. Validate locally before pushing:
   ```bash
   bash -n install.sh bin/ghostty-theme bin/ghostty-shell adapters/macos-terminal/apply-macos-terminal.sh
   zsh -n adapters/zsh/*.zsh
   python3 -m unittest discover -s tests -v
   ghostty +validate-config
   ```

## Community Standards

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). Security issues must be reported privately per [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions use the [MIT License](LICENSE).
