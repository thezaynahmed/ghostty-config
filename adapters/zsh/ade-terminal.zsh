# ==============================================================================
# Zsh Ergonomics & ADE (Agent Dev Environment) Integration
# Source in ~/.zshrc:
#   source ~/.config/ghostty/adapters/zsh/ade-terminal.zsh
# ==============================================================================

[[ -o interactive ]] || return 0

typeset -g _ghostty_repo_dir="${${(%):-%N}:A:h:h:h}"
typeset -g _ghostty_state_dir="${GHOSTTY_SHELL_STATE_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/ghostty-shell}"
typeset _ghostty_profile="${GHOSTTY_STARSHIP_PROFILE:-}"
typeset _ghostty_icons="${GHOSTTY_SHELL_ICONS:-}"
if [[ -z "$_ghostty_profile" && -f "$_ghostty_state_dir/profile" ]]; then
  IFS= read -r _ghostty_profile < "$_ghostty_state_dir/profile"
fi
if [[ -z "$_ghostty_icons" && -f "$_ghostty_state_dir/icons" ]]; then
  IFS= read -r _ghostty_icons < "$_ghostty_state_dir/icons"
fi
case "$_ghostty_profile" in minimal|context|portable|off) ;; *) _ghostty_profile=off ;; esac
case "$_ghostty_icons" in auto|never) ;; *) _ghostty_icons=auto ;; esac
[[ "$_ghostty_profile" != portable ]] || _ghostty_icons=never

# 1. Force steady block cursor (\e[2 q) after every command & vim mode switch
#    Prevents Neovim, vi-mode, or SSH sessions from leaving a blinking bar cursor
_ade_steady_block_cursor() {
  printf '\e[2 q'
}
autoload -Uz add-zsh-hook
add-zsh-hook precmd _ade_steady_block_cursor

# 2. High-legibility LSCOLORS (macOS BSD ls) and LS_COLORS (GNU coreutils)
#    Replaces unreadable dark-blue directory ANSI codes with high-contrast cyan/sky
export LSCOLORS="Gxfxcxdxbxegedabagacad"
export LS_COLORS="di=1;36:ln=35:so=32:pi=33:ex=31:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=30;42:ow=30;43"

# 3. Quick CLI alias for switching themes
if [[ -x "$_ghostty_repo_dir/bin/ghostty-theme" ]]; then
  alias gtheme="${(q)_ghostty_repo_dir}/bin/ghostty-theme"
fi
alias ghostty-shell="${(q)_ghostty_repo_dir}/bin/ghostty-shell"

# 4. Icon-rich file listing via eza (modern Nerd Font icons)
if command -v eza >/dev/null 2>&1; then
  alias ls="eza --icons=$_ghostty_icons --group-directories-first"
  alias ll="eza -la --icons=$_ghostty_icons --git --group-directories-first"
  alias lt="eza --tree --level=2 --icons=$_ghostty_icons"
fi

# 5. Interactive Tab-Completion with Icons (fzf-tab + eza)
typeset _ghostty_fzf_tab="${ZSH_CUSTOM:-${ZSH:-$HOME/.oh-my-zsh}/custom}/plugins/fzf-tab/fzf-tab.plugin.zsh"
if command -v fzf >/dev/null 2>&1 && [[ -f "$_ghostty_fzf_tab" ]]; then
  # Oh My Zsh normally loads it; standalone users must run compinit first.
  if (( $+functions[compdef] && ! $+functions[fzf-tab-complete] )); then
    source "$_ghostty_fzf_tab"
  fi
  zstyle ':completion:*:descriptions' format '[%d]'
  zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
  if command -v eza >/dev/null 2>&1; then
    if [[ "$_ghostty_icons" == never ]]; then
      zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always --icons=never --group-directories-first -- "$realpath"'
    else
      zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always --icons=always --group-directories-first -- "$realpath"'
    fi
  fi
fi

# A saved profile is an explicit opt-in; otherwise keep the current prompt.
if [[ "$_ghostty_profile" != off && "${_GHOSTTY_STARSHIP_ALLOWED:-1}" == 1 ]] && command -v starship >/dev/null 2>&1; then
  export STARSHIP_CONFIG="$_ghostty_repo_dir/adapters/starship/$_ghostty_profile.toml"
  if [[ -z "${_GHOSTTY_STARSHIP_INITIALIZED:-}" ]]; then
    eval "$(starship init zsh)"
    typeset -g _GHOSTTY_STARSHIP_INITIALIZED=1
  fi
fi
unset _ghostty_profile _ghostty_icons _ghostty_fzf_tab
