#!/usr/bin/env bash
# ==============================================================================
# Apply terminal profile + Monaspace/MesloLGS to native macOS Terminal.app
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_NAME="${1:-Gruvbox Material Dark}"
THEME_FILE="${SCRIPT_DIR}/${PROFILE_NAME}.terminal"

if [[ ! -f "${THEME_FILE}" ]]; then
    echo "Error: Terminal profile not found at ${THEME_FILE}" >&2
    exit 1
fi

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

echo "==> macOS Terminal.app successfully configured with ${PROFILE_NAME}."
