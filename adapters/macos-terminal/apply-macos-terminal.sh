#!/usr/bin/env bash
# ==============================================================================
# Apply Dyslexia + ADHD Typography & Steady Block Cursor to macOS Terminal.app
# ==============================================================================
set -euo pipefail

PROFILE_NAME="$(defaults read com.apple.Terminal "Default Window Settings" 2>/dev/null || echo "Pro")"
echo "Configuring macOS Terminal.app profile: $PROFILE_NAME"

# Disable cursor blink and set steady block cursor (CursorType = 0 in Terminal.app)
/usr/libexec/PlistBuddy -c "Set ':Window Settings:${PROFILE_NAME}:CursorBlink' false" ~/Library/Preferences/com.apple.Terminal.plist 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add ':Window Settings:${PROFILE_NAME}:CursorBlink' bool false" ~/Library/Preferences/com.apple.Terminal.plist

/usr/libexec/PlistBuddy -c "Set ':Window Settings:${PROFILE_NAME}:CursorType' 0" ~/Library/Preferences/com.apple.Terminal.plist 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Add ':Window Settings:${PROFILE_NAME}:CursorType' integer 0" ~/Library/Preferences/com.apple.Terminal.plist

/usr/libexec/PlistBuddy -c "Set ':Window Settings:${PROFILE_NAME}:FontAntialias' true" ~/Library/Preferences/com.apple.Terminal.plist 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Set ':Window Settings:${PROFILE_NAME}:UseBoldFonts' true" ~/Library/Preferences/com.apple.Terminal.plist 2>/dev/null || true

echo "macOS Terminal.app updated (Steady Block Cursor + Antialiasing enabled)."
