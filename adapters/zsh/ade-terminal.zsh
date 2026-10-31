# ==============================================================================
# Zsh Ergonomics & ADE (Agent Dev Environment) Integration
# Source in ~/.zshrc:
#   source ~/.config/ghostty/adapters/zsh/ade-terminal.zsh
# ==============================================================================

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
if [[ -x "$HOME/.config/ghostty/bin/ghostty-theme" ]]; then
  alias gtheme="$HOME/.config/ghostty/bin/ghostty-theme"
fi

# 4. Icon-rich file listing via eza (modern Nerd Font icons)
if command -v eza >/dev/null 2>&1; then
  alias ls="eza --icons=auto --group-directories-first"
  alias ll="eza -la --icons=auto --git --group-directories-first"
  alias lt="eza --tree --level=2 --icons=auto"
fi

# 5. Interactive Tab-Completion with Icons (fzf-tab + eza)
if [[ -d "$HOME/.oh-my-zsh/custom/plugins/fzf-tab" ]]; then
  zstyle ':completion:*:descriptions' format '[%d]'
  zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
  if command -v eza >/dev/null 2>&1; then
    zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always --icons=always --group-directories-first $realpath'
  fi
fi
