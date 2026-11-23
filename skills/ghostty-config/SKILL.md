---
name: ghostty-config
description: Installs, configures, validates, and troubleshoots the Ghostty Dyslexia, ADHD & Late-Night terminal setup and universal theme-sync CLI across 16+ terminals and IDEs. Use when the user wants to set up Ghostty, install Monaspace Neon fonts, sync themes across VS Code/Cursor/Antigravity/Zed/Warp/Kitty/Alacritty/WezTerm/tmux, configure Starship shell icons, or run theme-sync diagnostics.
---

# Ghostty Config & Universal Theme-Sync Skill

Install, configure, or troubleshoot `thezaynahmed/ghostty-config` on macOS and Linux.

## Quick Setup Workflow

1. Clone and install across Ghostty plus detected terminals/IDEs:
   ```bash
   git clone https://github.com/thezaynahmed/ghostty-config.git ~/.config/ghostty
   ~/.config/ghostty/install.sh --all
   ```
   Or target specific tools (`--cursor`, `--vscode`, `--antigravity`, `--windsurf`, `--superset`, `--zed`, `--warp`, `--alacritty`, `--wezterm`, `--kitty`, `--iterm2`, `--macos-terminal`, `--tmux`, `--linux-fontconfig`, `--zsh`, `--shell-icons`, `--starship context`).
2. Verify Ghostty config:
   ```bash
   ghostty +validate-config
   ```

## Theme Switching & Diagnostics (`ghostty-theme` / `theme-sync`)

Both `ghostty-theme` and `theme-sync` symlink to `bin/ghostty-theme`:

```bash
theme-sync current                # Read-only active theme check
theme-sync --signal               # Read-only 78-col Neofetch contrast & ANSI TUI (alias: --fetch)
theme-sync --list                 # List all 22 calibrated themes
theme-sync year-one --all         # Sync Gotham Noir - Year One across all tools
theme-sync batcomputer --all      # Sync Gotham Noir - Batcomputer
theme-sync arkham --all           # Sync Gotham Noir - Arkham Slate
theme-sync vengeance --all        # Sync Gotham Noir - Vengeance
```

On macOS, Ghostty does not reload on `SIGUSR2`; prompt the user to press `Cmd+Shift+,` to hot-reload.

## Shell Icons & Starship Prompt

```bash
ghostty-shell doctor
ghostty-shell profile powerline   # minimal | context | powerline | portable | off
ghostty-shell icons never
```

Profile selections live outside the repository in `~/.config/ghostty-shell/`. Never commit local profile files.

## Verification

```bash
bash -n install.sh bin/ghostty-theme bin/ghostty-shell adapters/macos-terminal/apply-macos-terminal.sh
zsh -n adapters/zsh/*.zsh
python3 -m unittest discover -s tests -v
ghostty +validate-config
```
