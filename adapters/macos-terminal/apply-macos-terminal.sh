#!/usr/bin/env bash
# ==============================================================================
# Apply Gruvbox Material Dark + MesloLGS NF to native macOS Terminal.app
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_FILE="${SCRIPT_DIR}/Gruvbox Material Dark.terminal"
PROFILE_NAME="Gruvbox Material Dark"

echo "==> Importing '${PROFILE_NAME}' into macOS Terminal.app..."
open "${THEME_FILE}"
sleep 1

echo "==> Setting '${PROFILE_NAME}' as default and startup profile..."
osascript <<EOF
tell application "Terminal"
    set default settings to settings set "${PROFILE_NAME}"
    set startup settings to settings set "${PROFILE_NAME}"
    repeat with w in windows
        repeat with t in tabs of w
            set current settings of t to settings set "${PROFILE_NAME}"
        end repeat
    end repeat
end tell
EOF

defaults write com.apple.Terminal "Default Window Settings" -string "${PROFILE_NAME}"
defaults write com.apple.Terminal "Startup Window Settings" -string "${PROFILE_NAME}"

echo "==> macOS Terminal.app successfully configured with Gruvbox Material Dark + MesloLGS NF."
