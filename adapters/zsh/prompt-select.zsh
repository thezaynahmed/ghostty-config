# Source after ZSH_THEME is assigned and before Oh My Zsh loads its theme.
typeset -g _GHOSTTY_STARSHIP_ALLOWED=0
typeset _ghostty_selected="${GHOSTTY_STARSHIP_PROFILE:-}"
typeset _ghostty_profile_file="${GHOSTTY_SHELL_STATE_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/ghostty-shell}/profile"
if [[ -z "$_ghostty_selected" && -f "$_ghostty_profile_file" ]]; then
  IFS= read -r _ghostty_selected < "$_ghostty_profile_file"
fi
if command -v starship >/dev/null 2>&1; then
  case "$_ghostty_selected" in
    minimal|context|portable) ZSH_THEME=''; _GHOSTTY_STARSHIP_ALLOWED=1 ;;
  esac
fi
unset _ghostty_selected _ghostty_profile_file
