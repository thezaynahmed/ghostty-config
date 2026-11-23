# Agent Setup Instructions (AGENTS.md)

Use this file when a user asks an AI agent to install or configure this repository.

## 1. Automated Installation

Run the installer script for the user's operating system and tools:

```bash
git clone https://github.com/thezaynahmed/ghostty-config.git ~/.config/ghostty
~/.config/ghostty/install.sh --all
```

To configure only specific tools, pass individual flags to `install.sh`:

- `--cursor`: Merge terminal settings into Cursor IDE.
- `--vscode`: Merge terminal settings into VS Code.
- `--antigravity`: Merge terminal settings into Antigravity IDE.
- `--windsurf`: Merge terminal settings into Windsurf IDE.
- `--superset`: Install Superset terminal settings.
- `--zed`: Merge terminal settings into Zed.
- `--warp`: Copy all 22 themes to `~/.warp/themes`.
- `--alacritty`: Copy `alacritty.toml` to `~/.config/alacritty/`.
- `--wezterm`: Copy `wezterm.lua` to `~/.config/wezterm/`.
- `--kitty`: Copy `kitty.conf` to `~/.config/kitty/`.
- `--iterm2`: Install iTerm2 Dynamic Profile (macOS).
- `--macos-terminal`: Configure macOS Terminal.app profile (macOS).
- `--tmux`: Append pane dimming and truecolor rules to `~/.tmux.conf`.
- `--linux-fontconfig`: Install Linux Fontconfig rules to `~/.config/fontconfig/conf.d/`.
- `--zsh`: Source the steady-cursor Zsh hook in `~/.zshrc`.
- `--shell-icons`: Configure eza/fzf shell icons and the Zsh adapter.
- `--starship <minimal|context|powerline|portable>`: Select an optional Starship prompt profile.
- `--theme <name>`: Switch the active Ghostty theme.

For profile changes, troubleshooting, Linux prerequisites, and sync behavior, see [`docs/shell-icons.md`](docs/shell-icons.md). The shell icon integration keeps its profile selection under `~/.config/ghostty-shell/`; do not commit local selections.

## 2. Theme Switching (`ghostty-theme` / `theme-sync`)

`install.sh` links both `ghostty-theme` and the universal `theme-sync` alias into `PATH` to inspect, list, or switch themes across Ghostty and synced terminals/IDEs:

```bash
theme-sync current                # Read-only active theme check
theme-sync --signal               # Read-only Batcomputer Neofetch ANSI diagnostic TUI (alias: --fetch)
theme-sync --list                 # List all available themes
theme-sync year-one --all         # Gotham Noir - Year One across all synced tools
theme-sync batcomputer --all      # Gotham Noir - Batcomputer
theme-sync arkham --all           # Gotham Noir - Arkham Slate
theme-sync vengeance --all        # Gotham Noir - Vengeance
ghostty-theme "Gruvbox Material Dark Medium"
```

## 3. Validation

Verify the Ghostty configuration with:

```bash
ghostty +validate-config
```
