import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("configure_zsh", ROOT / "scripts/configure-zsh.py")
configure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configure)


class ShellIconsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ghostty shell ")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.env = dict(os.environ, GHOSTTY_SHELL_STATE_DIR=str(self.path / "state"), ZDOTDIR=str(self.path))
        self.env.pop("GHOSTTY_STARSHIP_PROFILE", None)
        self.env.pop("GHOSTTY_SHELL_ICONS", None)

    def cli(self, *args, **kwargs):
        return subprocess.run([str(ROOT / "bin/ghostty-shell"), *args], env=self.env,
                              text=True, capture_output=True, **kwargs)

    def zsh(self, command, interactive=True):
        flags = "-dfi" if interactive else "-df"
        return subprocess.run(["zsh", flags, "-c", command], env=self.env, cwd=ROOT,
                              text=True, capture_output=True, check=True)

    def test_default_preserves_prompt(self):
        result = self.zsh("PROMPT='original>'; source adapters/zsh/ade-terminal.zsh; print -r -- $PROMPT")
        self.assertEqual(result.stdout.strip(), "original>")

    def test_noninteractive_shell_is_untouched(self):
        result = self.zsh("source adapters/zsh/ade-terminal.zsh; alias ls 2>/dev/null || true", False)
        self.assertEqual(result.stdout, "")

    def test_invalid_profile_is_never_written(self):
        result = self.cli("profile", "$(touch should-not-exist)")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.path / "state/profile").exists())

    def test_unsafe_saved_value_is_not_evaluated(self):
        state = self.path / "state"
        state.mkdir()
        (state / "profile").write_text("$(touch should-not-exist)\n")
        result = self.zsh("PROMPT='original>'; source adapters/zsh/ade-terminal.zsh; print -r -- $PROMPT")
        self.assertEqual(result.stdout.strip(), "original>")
        self.assertFalse((ROOT / "should-not-exist").exists())

    def test_configure_is_idempotent_and_backs_up_original(self):
        zshrc = self.path / ".zshrc"
        original = '# Enable Powerlevel10k instant prompt.\nif [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then\n  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"\nfi\nZSH_THEME="powerlevel10k/powerlevel10k"\nsource "$ZSH/oh-my-zsh.sh"\n# user alias\nalias mine="echo mine"\n'
        zshrc.write_text(original)
        self.assertTrue(configure.configure(zshrc, ROOT))
        first = zshrc.read_text()
        self.assertIn('ZSH_THEME="powerlevel10k/powerlevel10k"', first)
        self.assertIn('GHOSTTY_SKIP_P10K_INSTANT:-0', first)
        self.assertIn("ghostty shell instant prompt guard", first)
        self.assertLess(first.index("prompt-select.zsh"), first.index("oh-my-zsh.sh"))
        self.assertIn('alias mine="echo mine"', first)
        self.assertFalse(configure.configure(zshrc, ROOT))
        self.assertEqual(first, zshrc.read_text())
        backups = list(self.path.glob(".zshrc.backup.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)

    def test_early_guard_selects_starship_and_suppresses_p10k_instant_prompt(self):
        zshrc = self.path / ".zshrc"
        zshrc.write_text('if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then\n  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"\nfi\nZSH_THEME="powerlevel10k/powerlevel10k"\nsource "$ZSH/oh-my-zsh.sh"\n')
        configure.configure(zshrc, ROOT)
        result = self.zsh(f'GHOSTTY_SHELL_STATE_DIR={self.env["GHOSTTY_SHELL_STATE_DIR"]!r}; mkdir -p "$GHOSTTY_SHELL_STATE_DIR"; print context > "$GHOSTTY_SHELL_STATE_DIR/profile"; source {str(zshrc)!r}; print -r -- "$GHOSTTY_SKIP_P10K_INSTANT|$ZSH_THEME"')
        self.assertIn("1|", result.stdout)

    def test_late_starship_path_keeps_existing_theme(self):
        tools = self.path / "late-tools"
        tools.mkdir()
        starship = tools / "starship"
        starship.write_text('#!/bin/sh\necho "PROMPT=starship"\n')
        starship.chmod(0o755)
        self.env['GHOSTTY_STARSHIP_PROFILE'] = 'context'
        result = self.zsh(f'path=(/usr/bin /bin); ZSH_THEME=p10k; source adapters/zsh/prompt-select.zsh; path+=({str(tools)!r}); PROMPT=original; source adapters/zsh/ade-terminal.zsh; print -r -- "$ZSH_THEME|$PROMPT"')
        self.assertEqual(result.stdout.strip(), 'p10k|original')

    def test_profile_selection_migrates_old_installed_guard(self):
        zshrc = self.path / '.zshrc'
        zshrc.write_text('# >>> ghostty shell instant prompt guard >>>\ntypeset -g GHOSTTY_SKIP_P10K_INSTANT=0\n# <<< ghostty shell instant prompt guard <<<\nalias mine="echo preserved"\n')
        self.cli('profile', 'powerline', check=True)
        self.assertIn('prompt-guard.zsh', zshrc.read_text())
        self.assertIn('alias mine="echo preserved"', zshrc.read_text())
        result = self.zsh(f'source {str(zshrc)!r}; print -r -- "$GHOSTTY_SKIP_P10K_INSTANT"')
        self.assertEqual(result.stdout.strip(), '1')
        self.assertEqual(len(list(self.path.glob('.zshrc.backup.*'))), 1)

    def test_symlink_finds_repo(self):
        link = self.path / "shell helper"
        link.symlink_to(ROOT / "bin/ghostty-shell")
        result = subprocess.run([str(link), "specimen"], text=True, capture_output=True, check=True)
        self.assertIn("ASCII ruler", result.stdout)
        self.assertNotIn("\x1b", result.stdout)

    def test_legacy_hook_with_other_user_commands_is_preserved(self):
        zshrc = self.path / ".zshrc"
        compound = f'source "{ROOT}/adapters/zsh/ade-terminal.zsh"; export MY_FLAG=1'
        zshrc.write_text(compound + "\n")
        configure.configure(zshrc, ROOT)
        self.assertIn(compound, zshrc.read_text())

    def test_completion_plugin_loads_only_once(self):
        if not shutil.which("fzf"):
            self.skipTest("fzf is optional")
        custom = self.path / "custom plugins"
        plugin = custom / "plugins/fzf-tab/fzf-tab.plugin.zsh"
        plugin.parent.mkdir(parents=True)
        plugin.write_text('(( LOADS += 1 )); fzf-tab-complete() { :; }\n')
        self.env["ZSH_CUSTOM"] = str(custom)
        result = self.zsh('compdef() { :; }; typeset -gi LOADS=0; source adapters/zsh/ade-terminal.zsh; source adapters/zsh/ade-terminal.zsh; print -r -- $LOADS')
        self.assertEqual(result.stdout.strip(), "1")

    def test_icons_never_and_quoted_completion_preview(self):
        self.cli("icons", "never", check=True)
        result = self.zsh('source adapters/zsh/ade-terminal.zsh; print -r -- "$aliases[ls]"')
        if shutil.which("eza"):
            self.assertIn("--icons=never", result.stdout)
        hook = (ROOT / "adapters/zsh/ade-terminal.zsh").read_text()
        self.assertIn('-- "$realpath"', hook)

    def test_sync_refuses_dirty_checkout(self):
        # Test against a disposable repo to avoid a network request.
        repo = self.path / "repo"
        (repo / "bin").mkdir(parents=True)
        shutil.copy2(ROOT / "bin/ghostty-shell", repo / "bin/ghostty-shell")
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        result = subprocess.run([str(repo / "bin/ghostty-shell"), "sync"], text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Local changes", result.stderr)

    @unittest.skipUnless(shutil.which("starship"), "Starship rendering is optional locally")
    def test_powerline_profile_and_rendering(self):
        self.cli('profile', 'powerline', check=True)
        selected = self.zsh('ZSH_THEME=previous; source adapters/zsh/prompt-select.zsh; source adapters/zsh/ade-terminal.zsh; print -r -- "$ZSH_THEME|$STARSHIP_CONFIG|$_GHOSTTY_STARSHIP_INITIALIZED"')
        self.assertIn('|'+str(ROOT/'adapters/starship/powerline.toml')+'|1', selected.stdout)
        repo = self.path / 'project'
        repo.mkdir()
        subprocess.run(['git', 'init', '-q', '--initial-branch=main', str(repo)], check=True)
        subprocess.run(['git', '-C', str(repo), '-c', 'user.name=Test User', '-c', 'user.email=test@example.invalid', 'commit', '-q', '--allow-empty', '-m', 'fixture'], check=True)
        (repo/'untracked.txt').write_text('fixture\n')
        env = dict(self.env, STARSHIP_CONFIG=str(ROOT/'adapters/starship/powerline.toml'), STARSHIP_CACHE=str(self.path/'cache'), TERM='xterm-256color')
        for code in ('0', '7'):
            result = subprocess.run(['starship', 'prompt', '--path', str(repo), '--status', code, '--terminal-width', '140'], env=env, text=True, capture_output=True, check=True)
            clean = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', result.stdout)
            self.assertIn('main', clean)
            self.assertIn('?1', clean)
            self.assertRegex(clean, r'\d{2}:\d{2}:\d{2} [AP]M')
            self.assertIn('', clean)
            self.assertIn('╰─', clean)
            self.assertNotIn('Unknown', result.stderr)
            self.assertNotIn('Error', result.stderr)
            self.assertNotRegex(result.stdout, r'\x1b\[[0-9;]*(?:38|48);2;', 'Powerline must use theme ANSI colors rather than RGB escape sequences')
            if code == '7':
                self.assertIn('exit:7', clean)
            else:
                self.assertIn('✔', clean)
                self.assertNotIn('exit:0', clean)

    @unittest.skipUnless(shutil.which("starship"), "Starship rendering is optional locally")
    def test_profiles_render_failure_and_production_context(self):
        (self.path / "aws-config").write_text("[profile demo]\nregion = us-east-1\n")
        (self.path / "kubeconfig").write_text("apiVersion: v1\nkind: Config\ncurrent-context: prod-demo\ncontexts:\n- name: prod-demo\n  context:\n    cluster: demo\n    user: demo\n    namespace: apps\n")
        env = dict(self.env, STARSHIP_CACHE=str(self.path / "cache"),
                   AWS_CONFIG_FILE=str(self.path / "aws-config"), AWS_SHARED_CREDENTIALS_FILE="/dev/null",
                   AWS_PROFILE="demo", KUBECONFIG=str(self.path / "kubeconfig"),
                   AZURE_CONFIG_DIR=str(self.path / "azure"), NO_COLOR="1", TERM="xterm-256color")
        for profile in ("minimal", "context", "portable"):
            env["STARSHIP_CONFIG"] = str(ROOT / f"adapters/starship/{profile}.toml")
            result = subprocess.run(["starship", "prompt", "--path", str(self.path), "--status", "7"], env=env,
                                    text=True, capture_output=True, check=True)
            clean = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", result.stdout)
            self.assertIn("exit:7", clean)
            self.assertNotIn("Unknown", result.stderr)
            self.assertNotIn("Error", result.stderr)
            if profile == "portable":
                self.assertTrue(clean.isascii(), clean)
            if profile == "context":
                right = subprocess.run(["starship", "prompt", "--right", "--path", str(self.path)], env=env,
                                       text=True, capture_output=True, check=True)
                self.assertIn("prod-demo", right.stdout)
                self.assertIn("apps", right.stdout)


if __name__ == "__main__":
    unittest.main()
