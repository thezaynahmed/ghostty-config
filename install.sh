#!/usr/bin/env bash
# ==============================================================================
# Ghostty + Universal Terminal Installer (Dyslexia + ADHD + Late-Night Edition)
# Platforms: macOS, Fedora, Ubuntu, Debian, Pop!_OS, Arch, openSUSE, WSL2
# ==============================================================================
set -euo pipefail

REPO_URL="https://github.com/thezaynahmed/ghostty-config.git"
TARGET_DIR="${GHOSTTY_CONFIG_DIR:-$HOME/.config/ghostty}"

INSTALL_ALL=0
INSTALL_WARP=0
INSTALL_ITERM2=0
INSTALL_MACOS_TERM=0
INSTALL_CURSOR=0
INSTALL_VSCODE=0
INSTALL_ANTIGRAVITY=0
INSTALL_WINDSURF=0
INSTALL_SUPERSET=0
INSTALL_ZED=0
INSTALL_ALACRITTY=0
INSTALL_WEZTERM=0
INSTALL_KITTY=0
INSTALL_TMUX=0
INSTALL_ZSH=0
INSTALL_FONTCONFIG=0
INITIAL_THEME=""

show_help() {
  cat << 'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --all               Configure Ghostty plus all detected terminals, editors, and shells
  --theme <name>      Set active Ghostty theme (e.g. "batman", "kanagawa-wave", "ef-dream")
  --cursor            Merge terminal settings into Cursor IDE
  --vscode            Merge terminal settings into VS Code
  --antigravity       Merge terminal settings into Antigravity IDE
  --windsurf          Merge terminal settings into Windsurf IDE
  --superset          Install Superset ADE terminal config
  --zed               Merge terminal settings into Zed editor
  --warp              Install all 18 themes to ~/.warp/themes
  --alacritty         Install ~/.config/alacritty/alacritty.toml
  --wezterm           Install ~/.config/wezterm/wezterm.lua
  --kitty             Install ~/.config/kitty/kitty.conf
  --tmux              Append split-dimming & truecolor config to ~/.tmux.conf
  --iterm2            Install iTerm2 Dynamic Profile (macOS)
  --macos-terminal    Configure macOS Terminal.app profile (macOS)
  --linux-fontconfig  Install Linux Fontconfig OpenType & hinting rules (Linux)
  --zsh               Add steady-cursor & contrast hook to ~/.zshrc
  -h, --help          Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) INSTALL_ALL=1; shift ;;
    --warp) INSTALL_WARP=1; shift ;;
    --iterm2) INSTALL_ITERM2=1; shift ;;
    --macos-terminal) INSTALL_MACOS_TERM=1; shift ;;
    --cursor) INSTALL_CURSOR=1; shift ;;
    --vscode) INSTALL_VSCODE=1; shift ;;
    --antigravity) INSTALL_ANTIGRAVITY=1; shift ;;
    --windsurf) INSTALL_WINDSURF=1; shift ;;
    --superset) INSTALL_SUPERSET=1; shift ;;
    --zed) INSTALL_ZED=1; shift ;;
    --alacritty) INSTALL_ALACRITTY=1; shift ;;
    --wezterm) INSTALL_WEZTERM=1; shift ;;
    --kitty) INSTALL_KITTY=1; shift ;;
    --tmux) INSTALL_TMUX=1; shift ;;
    --zsh) INSTALL_ZSH=1; shift ;;
    --linux-fontconfig) INSTALL_FONTCONFIG=1; shift ;;
    --theme) INITIAL_THEME="${2:-}"; shift 2 ;;
    -h|--help) show_help; exit 0 ;;
    *) shift ;;
  esac
done

install_monaspace_linux() {
  local font_dir="$HOME/.local/share/fonts/monaspace"
  if fc-list 2>/dev/null | grep -qi "Monaspace Neon"; then
    echo "✓ Monaspace fonts already installed."
    return 0
  fi
  echo "→ Installing GitHub Monaspace v1.400 fonts to $font_dir..."
  mkdir -p "$font_dir"
  local tmp_zip
  tmp_zip="$(mktemp /tmp/monaspace-XXXXXX.zip)"
  curl -fsSL "https://github.com/githubnext/monaspace/releases/download/v1.400/monaspace-static-v1.400.zip" -o "$tmp_zip"
  unzip -qo "$tmp_zip" -d "$font_dir"
  rm -f "$tmp_zip"
  fc-cache -fv "$font_dir" >/dev/null 2>&1 || true
  echo "✓ Monaspace fonts cached."
}

merge_json_settings() {
  local target_file="$1"
  local source_file="$2"
  mkdir -p "$(dirname "$target_file")"
  python3 - "$target_file" "$source_file" << 'PY'
import json, os, sys

target_path, source_path = sys.argv[1], sys.argv[2]
with open(source_path, "r", encoding="utf-8") as f:
    src = json.load(f)

dst = {}
if os.path.exists(target_path):
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            dst = json.load(f)
    except Exception:
        dst = {}

for k, v in src.items():
    if isinstance(v, dict) and isinstance(dst.get(k), dict):
        dst[k].update(v)
    else:
        dst[k] = v

with open(target_path, "w", encoding="utf-8") as f:
    json.dump(dst, f, indent=2)
    f.write("\n")
PY
}

OS="$(uname -s)"
if [[ "$OS" == "Darwin" ]]; then
  echo "→ Detected macOS"
  if command -v brew >/dev/null 2>&1; then
    brew list --cask ghostty >/dev/null 2>&1 || brew install --cask ghostty
    brew list --cask font-monaspace >/dev/null 2>&1 || brew install --cask font-monaspace
    brew list --cask font-symbols-only-nerd-font >/dev/null 2>&1 || brew install --cask font-symbols-only-nerd-font
  fi
elif [[ "$OS" == "Linux" ]]; then
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "${ID:-}" in
      fedora|rhel|centos|nobara|bazzite)
        echo "→ Detected Fedora / RPM Linux (${ID})"
        if ! command -v ghostty >/dev/null 2>&1; then
          sudo dnf copr enable -y pgdev/ghostty
          sudo dnf install -y ghostty unzip curl fontconfig git python3
        fi
        install_monaspace_linux
        ;;
      ubuntu|debian|pop|linuxmint|kali|elementary)
        echo "→ Detected Ubuntu / Debian Linux (${ID})"
        sudo apt-get update -qq
        sudo apt-get install -y unzip curl fontconfig git python3
        if ! command -v ghostty >/dev/null 2>&1; then
          sudo snap install ghostty --classic 2>/dev/null || echo "Note: Install ghostty package from https://ghostty.org/docs/install/binary"
        fi
        install_monaspace_linux
        ;;
      arch|cachyos|endeavouros|manjaro)
        echo "→ Detected Arch Linux (${ID})"
        sudo pacman -S --needed --noconfirm ghostty otf-monaspace git python
        ;;
      opensuse*|suse*)
        echo "→ Detected openSUSE (${ID})"
        sudo zypper install -y ghostty unzip curl fontconfig git python3
        install_monaspace_linux
        ;;
      *)
        echo "→ Detected Linux (${ID:-generic})"
        install_monaspace_linux
        ;;
    esac
  fi
fi

# Clone ~/.config/ghostty if invoked via curl | bash
if [[ ! -f "$TARGET_DIR/config" ]]; then
  if [[ -d "$TARGET_DIR" && ! -d "$TARGET_DIR/.git" ]]; then
    mv "$TARGET_DIR" "${TARGET_DIR}.backup.$(date +%s)"
  fi
  git clone "$REPO_URL" "$TARGET_DIR"
fi

chmod +x "$TARGET_DIR/bin/ghostty-theme" "$TARGET_DIR/adapters/macos-terminal/apply-macos-terminal.sh" 2>/dev/null || true

# Link ghostty-theme CLI into ~/.local/bin or /opt/homebrew/bin if writable
if [[ -d "/opt/homebrew/bin" && -w "/opt/homebrew/bin" ]]; then
  ln -sf "$TARGET_DIR/bin/ghostty-theme" "/opt/homebrew/bin/ghostty-theme"
elif [[ -d "/usr/local/bin" && -w "/usr/local/bin" ]]; then
  ln -sf "$TARGET_DIR/bin/ghostty-theme" "/usr/local/bin/ghostty-theme"
else
  mkdir -p "$HOME/.local/bin"
  ln -sf "$TARGET_DIR/bin/ghostty-theme" "$HOME/.local/bin/ghostty-theme"
fi

# Determine OS-specific editor config base path
if [[ "$OS" == "Darwin" ]]; then
  APP_SUPPORT="$HOME/Library/Application Support"
else
  APP_SUPPORT="${XDG_CONFIG_HOME:-$HOME/.config}"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_WARP" -eq 1 ]]; then
  mkdir -p "$HOME/.warp/themes"
  cp -f "$TARGET_DIR"/adapters/warp/themes/*.yaml "$HOME/.warp/themes/"
  echo "✓ Installed 18 themes to ~/.warp/themes"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_CURSOR" -eq 1 ]]; then
  merge_json_settings "$APP_SUPPORT/Cursor/User/settings.json" "$TARGET_DIR/adapters/cursor/settings.json"
  echo "✓ Configured Cursor terminal settings"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_VSCODE" -eq 1 ]]; then
  merge_json_settings "$APP_SUPPORT/Code/User/settings.json" "$TARGET_DIR/adapters/vscode/settings.json"
  echo "✓ Configured VS Code terminal settings"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_ANTIGRAVITY" -eq 1 ]]; then
  merge_json_settings "$APP_SUPPORT/Antigravity/User/settings.json" "$TARGET_DIR/adapters/antigravity/settings.json"
  if [[ -d "$APP_SUPPORT/Antigravity IDE/User" ]]; then
    merge_json_settings "$APP_SUPPORT/Antigravity IDE/User/settings.json" "$TARGET_DIR/adapters/antigravity/settings.json"
  fi
  echo "✓ Configured Antigravity IDE terminal settings"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_WINDSURF" -eq 1 ]]; then
  merge_json_settings "$APP_SUPPORT/Windsurf/User/settings.json" "$TARGET_DIR/adapters/windsurf/settings.json"
  echo "✓ Configured Windsurf IDE terminal settings"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_SUPERSET" -eq 1 ]]; then
  mkdir -p "$HOME/.config/superset"
  cp -f "$TARGET_DIR/adapters/superset/terminal.json" "$HOME/.config/superset/terminal.json"
  echo "✓ Configured Superset terminal settings"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_ZED" -eq 1 ]]; then
  merge_json_settings "$HOME/.config/zed/settings.json" "$TARGET_DIR/adapters/zed/settings.json"
  echo "✓ Configured Zed terminal settings"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_ALACRITTY" -eq 1 ]]; then
  mkdir -p "$HOME/.config/alacritty"
  cp -f "$TARGET_DIR/adapters/alacritty/alacritty.toml" "$HOME/.config/alacritty/alacritty.toml"
  echo "✓ Installed ~/.config/alacritty/alacritty.toml"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_WEZTERM" -eq 1 ]]; then
  mkdir -p "$HOME/.config/wezterm"
  cp -f "$TARGET_DIR/adapters/wezterm/wezterm.lua" "$HOME/.config/wezterm/wezterm.lua"
  echo "✓ Installed ~/.config/wezterm/wezterm.lua"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_KITTY" -eq 1 ]]; then
  mkdir -p "$HOME/.config/kitty"
  cp -f "$TARGET_DIR/adapters/kitty/kitty.conf" "$HOME/.config/kitty/kitty.conf"
  echo "✓ Installed ~/.config/kitty/kitty.conf"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_TMUX" -eq 1 ]]; then
  if [[ ! -f "$HOME/.tmux.conf" ]] || ! grep -q "Dyslexia + ADHD" "$HOME/.tmux.conf"; then
    cat "$TARGET_DIR/adapters/tmux/tmux.conf" >> "$HOME/.tmux.conf"
    echo "✓ Added split-dimming config to ~/.tmux.conf"
  fi
fi

if [[ ("$INSTALL_ALL" -eq 1 || "$INSTALL_ITERM2" -eq 1) && "$OS" == "Darwin" ]]; then
  mkdir -p "$HOME/Library/Application Support/iTerm2/DynamicProfiles"
  cp -f "$TARGET_DIR/adapters/iterm2/dyslexia-adhd-profiles.json" \
    "$HOME/Library/Application Support/iTerm2/DynamicProfiles/dyslexia-adhd-profiles.json"
  echo "✓ Installed iTerm2 Dynamic Profile"
fi

if [[ "$INSTALL_MACOS_TERM" -eq 1 && "$OS" == "Darwin" ]]; then
  "$TARGET_DIR/adapters/macos-terminal/apply-macos-terminal.sh"
fi

if [[ ("$INSTALL_ALL" -eq 1 || "$INSTALL_FONTCONFIG" -eq 1) && "$OS" == "Linux" ]]; then
  mkdir -p "$HOME/.config/fontconfig/conf.d"
  cp -f "$TARGET_DIR/adapters/linux-fontconfig/70-monaspace-dyslexia.conf" \
    "$HOME/.config/fontconfig/conf.d/70-monaspace-dyslexia.conf"
  fc-cache -f >/dev/null 2>&1 || true
  echo "✓ Installed Linux Fontconfig Monaspace rules"
fi

if [[ "$INSTALL_ALL" -eq 1 || "$INSTALL_ZSH" -eq 1 ]]; then
  touch "$HOME/.zshrc"
  if ! grep -q "ade-terminal.zsh" "$HOME/.zshrc"; then
    printf '\n# Dyslexia + ADHD Terminal Ergonomics\nsource "%s/adapters/zsh/ade-terminal.zsh"\n' "$TARGET_DIR" >> "$HOME/.zshrc"
    echo "✓ Added Zsh hook to ~/.zshrc"
  fi
fi

if [[ -n "$INITIAL_THEME" ]]; then
  "$TARGET_DIR/bin/ghostty-theme" "$INITIAL_THEME"
fi

echo "✓ Setup complete at $TARGET_DIR"
