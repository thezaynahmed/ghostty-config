# Read the opt-in before Powerlevel10k's cached instant prompt can start.
# Keep this in the repository so profile additions propagate with normal updates.
typeset -g GHOSTTY_SKIP_P10K_INSTANT=0
typeset _ghostty_early_profile="${GHOSTTY_STARSHIP_PROFILE:-}"
if [[ -z "$_ghostty_early_profile" ]]; then
  typeset _ghostty_early_state="${GHOSTTY_SHELL_STATE_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/ghostty-shell}/profile"
  [[ ! -f "$_ghostty_early_state" ]] || IFS= read -r _ghostty_early_profile < "$_ghostty_early_state"
fi
case "$_ghostty_early_profile" in
  minimal|context|powerline|portable) GHOSTTY_SKIP_P10K_INSTANT=1 ;;
esac
unset _ghostty_early_profile _ghostty_early_state
