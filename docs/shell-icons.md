# Shell icons and prompt profiles

This repository ships a Zsh integration for `eza`, `fzf`/`fzf-tab`, and optional Starship profiles. It does not bundle third-party executables or fonts. The scripts use the upstream tools installed on the machine, and Nerd Font symbols are installed separately for terminals that need them. Ghostty itself embeds a Nerd Font symbol subset; keep Monaspace Neon as the text face and select the symbols font only when glyphs render as boxes.

## Install

On macOS with Homebrew:

```bash
./install.sh --starship context
```

This selects the Zsh integration, installs missing eza, fzf, Starship, and Nerd Font symbols through Homebrew, and saves the `context` profile. To add icons while retaining the current prompt, use `./install.sh --shell-icons`.

On Linux, install `zsh`, `eza`, and `fzf` with the distribution package manager. Install Starship from its official release/package instructions if selecting a prompt. Then run:

```bash
./install.sh --shell-icons
./install.sh --starship context
```

The installer installs the pinned Nerd Fonts Symbols Only v3.5.1 font archive after checking its SHA-256 digest. It reports missing eza/fzf as optional dependencies. Starship must already be on `PATH` when its profile is selected. Restart the terminal or reload the font cache/session after font installation.

## Choose a profile

| Profile | Prompt and icons |
| --- | --- |
| `minimal` | Compact path, Git branch/status, command duration, and failure indicator. Nerd Font symbols are used. |
| `context` | Minimal details plus SSH host, language/toolchain, jobs, AWS/Azure, and Kubernetes context. A context whose name contains `prod` is red and bold. |
| `portable` | ASCII prompt and file listings, avoiding Nerd Font glyph assumptions on remote hosts and logs. |
| `off` | Starship is disabled; the prompt configured before this integration (including Powerlevel10k, if configured) is used again. |

Use `ghostty-shell profile context` to change the selected profile. It takes effect in the next shell. The `GHOSTTY_STARSHIP_PROFILE` environment variable can override the saved choice. Profiles use repository TOML and do not overwrite `~/.config/starship.toml`; the adapter sets `STARSHIP_CONFIG` only in shells using a selected profile.

Starship must be on `PATH` before Oh My Zsh loads. Put any custom Starship `PATH` setup above `source "$ZSH/oh-my-zsh.sh"`. If it is unavailable at that point, the integration keeps the existing theme for that shell instead of initializing a second prompt later.

`ghostty-shell icons auto|never` selects eza and fzf-tab icon behavior. `auto` lets eza decide based on output/terminal capabilities; `never` disables glyphs. The `portable` profile also disables file icons. Install/configure the `fzf-tab` Oh My Zsh plugin separately if interactive tab completion previews are desired. Follow the [upstream load-order guidance](https://github.com/Aloxaf/fzf-tab#install): after `compinit`, and before plugins that wrap Zsh widgets, such as `zsh-autosuggestions` and `fast-syntax-highlighting`.

## Commands

```text
ghostty-shell profile [minimal|context|portable|off]
ghostty-shell icons [auto|never]
ghostty-shell doctor
ghostty-shell specimen
ghostty-shell sync
```

`doctor` shows selected modes and available commands. `specimen` prints the plain-text icon sample for checking font rendering. `sync` runs `git pull --ff-only` only when the repository checkout is clean; it does not change the saved profile. Review updates before restarting a shell if using a fork or local modifications.

The installer backs up `.zshrc` before adding its managed blocks, preserves existing aliases and the selected P10k theme, and makes the Starship selection before Oh My Zsh initializes its theme. When Starship is selected, it skips the existing P10k instant-prompt snippet. Choosing `off` restores the prior P10k flow in the next shell. To remove the integration entirely, restore the `.zshrc.backup.*` file created during installation.

## Third-party licenses

No upstream source or binary is vendored in this repository. The referenced projects retain their own licenses: [Starship (ISC)](https://github.com/starship/starship/blob/master/LICENSE), [eza (EUPL-1.2)](https://github.com/eza-community/eza/blob/main/LICENSE.txt), [fzf (MIT)](https://github.com/junegunn/fzf/blob/master/LICENSE), [fzf-tab (MIT)](https://github.com/Aloxaf/fzf-tab/blob/master/LICENSE), [Monaspace (OFL-1.1)](https://github.com/githubnext/monaspace/blob/main/LICENSE), and [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts/blob/master/license.txt) (upstream font/license terms vary). The repository's MIT license applies to original repository files, not those third-party projects.

## Updating pinned setup dependencies

The Linux symbol-font release and its digest, plus the Starship version and release checksum in CI, are intentionally pinned. Verify new upstream release artifacts and checksums before changing those pins. Local Homebrew installation follows the current Homebrew formula.
