# Security, Merge Protection, and Advisory AI Review

This document records the merge-gate rules, deterministic security controls, and third-party app scope for `thezaynahmed/ghostty-config`.

## 1. Required Merge Protection (`main`)

Protected by GitHub branch ruleset `26415451` (**Main: required CI and pull requests**):

- **Pull request required:** Direct pushes, force pushes, and branch deletions on `main` are blocked.
- **Required status check:** `zsh-and-shell-icons` (`.github/workflows/shell-quality.yml`) must pass on an up-to-date branch (`strict_required_status_checks_policy: true`).
- **Conversation resolution:** All pull request review threads must be resolved before merge (`required_review_thread_resolution: true`).
- **Bypass actors:** None (`bypass_actors: []`). Nobody, including the repository owner or third-party apps, can bypass this ruleset.

## 2. Deterministic Security Baseline (Public Repo, $0)

Merge protection relies on deterministic checks, never LLM approval:

- **Secret Scanning & Push Protection:** Enabled on GitHub.
- **CodeQL Code Scanning:** Enabled via GitHub default setup (`actions`, `python`). Kept advisory until observed stable across pull requests before considering promotion to a required ruleset check.
- **Dependabot Alerts & Security Updates:** Enabled on GitHub.

## 3. Advisory AI Pull Request Review (CodeRabbit)

- **Repository scope:** When installed, the CodeRabbit GitHub App (`coderabbitai`) is restricted to **Only select repositories** (`thezaynahmed/ghostty-config` and `thezaynahmed/gotham-noir`), never broad "All repositories" access.
- **Advisory posture:** `.coderabbit.yaml` sets `reviews.request_changes_workflow: false` so CodeRabbit never blocks merges via formal change requests and never replaces deterministic CI.
- **Zero cache retention:** `.coderabbit.yaml` sets `reviews.disable_cache: true` so repository code is not cached across runs.
- **Thread resolution note:** Because ruleset `26415451` requires resolved review threads, inline advisory comments from CodeRabbit must be reviewed and resolved before merging.

## 4. Safe No-Cost Strategy for Private Repositories

GitHub Free does not include native CodeQL, Secret Scanning, Push Protection, or Dependency Review on private repos, and CodeRabbit Free only provides PR summaries (not full cloud PR reviews) on private repos. For private repositories:

- **Deterministic security ($0):** Enable GitHub Dependabot alerts/security updates (free on private repos) and run open-source GitHub Actions (`gitleaks`, `semgrep` / `bandit` / `shellcheck`, `trivy`) as required CI checks.
- **AI review ($0 SaaS / private-safe):** Use local CLI/agent review before pushing, or run open-source MIT-licensed `PR-Agent` in your own GitHub Actions workflow using a zero-retention BYOK API key so proprietary code never passes through a third-party review SaaS.
