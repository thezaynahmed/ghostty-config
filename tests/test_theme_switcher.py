"""E2E and unit tests for ghostty-theme lore shortcuts, --signal, adapters, and multi-app sync."""

from __future__ import annotations

import json
import os
import plistlib
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GHOSTTY_THEME = ROOT / "bin" / "ghostty-theme"

LORE_THEMES = (
    "Gotham Noir - Year One",
    "Gotham Noir - Batcomputer",
    "Gotham Noir - Arkham Slate",
    "Gotham Noir - Vengeance",
)


class ThemeSwitcherTest(unittest.TestCase):
    def test_current_and_signal_are_readonly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "config"
            cfg.write_text("theme = Gotham Noir - Year One\nfont-size = 14.5\n", encoding="utf-8")
            env = dict(os.environ, GHOSTTY_CONFIG_DIR=str(ROOT), GHOSTTY_CONFIG_PATH=str(cfg))
            cur = subprocess.run([str(GHOSTTY_THEME), "current"], capture_output=True, text=True, env=env, check=True)
            self.assertEqual(cur.stdout.strip(), "Gotham Noir - Year One")

            sig = subprocess.run([str(GHOSTTY_THEME), "--signal"], capture_output=True, text=True, env=env, check=True)
            self.assertIn("DETECTIVE #27", sig.stdout)
            self.assertIn("Gotham Noir - Year One", sig.stdout)
            self.assertIn("YEAR-ONE // DETECTIVE-27", sig.stdout)
            self.assertIn("theme = Gotham Noir - Year One", cfg.read_text(encoding="utf-8"))

    def test_batman_lore_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "config"
            cfg.write_text("theme = Gruvbox Material Dark Medium\n", encoding="utf-8")
            env = dict(os.environ, GHOSTTY_CONFIG_DIR=str(ROOT), GHOSTTY_CONFIG_PATH=str(cfg))
            cases = (
                ("batman", "Gotham Noir - Year One"),
                ("year-one", "Gotham Noir - Year One"),
                ("detective-27", "Gotham Noir - Year One"),
                ("batcomputer", "Gotham Noir - Batcomputer"),
                ("oracle", "Gotham Noir - Batcomputer"),
                ("arkham", "Gotham Noir - Arkham Slate"),
                ("detective-mode", "Gotham Noir - Arkham Slate"),
                ("vengeance", "Gotham Noir - Vengeance"),
                ("red-hood", "Gotham Noir - Vengeance"),
            )
            for alias, expected in cases:
                with self.subTest(alias=alias):
                    subprocess.run([str(GHOSTTY_THEME), alias], capture_output=True, text=True, env=env, check=True)
                    self.assertIn(f"theme = {expected}", cfg.read_text(encoding="utf-8"))

    def test_warp_theme_yaml_exists_for_all_lore_variants(self) -> None:
        for name in LORE_THEMES:
            slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            yaml_path = ROOT / "adapters" / "warp" / "themes" / f"{slug}.yaml"
            self.assertTrue(yaml_path.exists(), f"Missing Warp YAML {yaml_path}")

    def test_all_adapters_parse_cleanly(self) -> None:
        for rel in (
            "adapters/vscode/settings.json",
            "adapters/cursor/settings.json",
            "adapters/antigravity/settings.json",
            "adapters/ade/settings.json",
            "adapters/windsurf/settings.json",
            "adapters/zed/settings.json",
            "adapters/superset/terminal.json",
            "adapters/windows-terminal/settings.json",
            "adapters/iterm2/dyslexia-adhd-profiles.json",
        ):
            json.loads((ROOT / rel).read_text(encoding="utf-8"))

        tomllib.loads((ROOT / "adapters" / "alacritty" / "alacritty.toml").read_text(encoding="utf-8"))
        for star in (ROOT / "adapters" / "starship").glob("*.toml"):
            tomllib.loads(star.read_text(encoding="utf-8"))

        fc_xml = (ROOT / "adapters" / "linux-fontconfig" / "70-monaspace-dyslexia.conf").read_text(encoding="utf-8")
        self.assertEqual(ET.fromstring(fc_xml).tag, "fontconfig")

        for name in LORE_THEMES:
            term_path = ROOT / "adapters" / "macos-terminal" / f"{name}.terminal"
            self.assertTrue(term_path.exists(), f"Missing {term_path}")
            pl = plistlib.loads(term_path.read_bytes())
            self.assertEqual(pl["name"], name)
            self.assertEqual(plistlib.loads(pl["BackgroundColor"])["$archiver"], "NSKeyedArchiver")

        for sh in (
            ROOT / "bin" / "ghostty-theme",
            ROOT / "bin" / "ghostty-shell",
            ROOT / "install.sh",
            ROOT / "adapters" / "macos-terminal" / "apply-macos-terminal.sh",
        ):
            subprocess.run(["bash", "-n", str(sh)], check=True)

    def test_end_to_end_sync_all_variants(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            home = tmp / "home"
            repo = tmp / "repo"
            home.mkdir()
            shutil.copytree(ROOT / "themes", repo / "themes")
            shutil.copytree(ROOT / "adapters", repo / "adapters")
            shutil.copytree(ROOT / "bin", repo / "bin")
            shutil.copy2(ROOT / "config", repo / "config")

            is_darwin = os.uname().sysname == "Darwin"
            app_support = (home / "Library" / "Application Support") if is_darwin else (home / ".config")
            for ide in ("Code", "Cursor", "Antigravity", "Antigravity IDE", "Windsurf"):
                u = app_support / ide / "User"
                u.mkdir(parents=True)
                (u / "settings.json").write_text("{}\n", encoding="utf-8")

            (home / ".config" / "zed").mkdir(parents=True)
            shutil.copy2(ROOT / "adapters" / "zed" / "settings.json", home / ".config" / "zed" / "settings.json")
            (home / ".config" / "alacritty").mkdir(parents=True)
            shutil.copy2(ROOT / "adapters" / "alacritty" / "alacritty.toml", home / ".config" / "alacritty" / "alacritty.toml")
            (home / ".config" / "kitty").mkdir(parents=True)
            shutil.copy2(ROOT / "adapters" / "kitty" / "kitty.conf", home / ".config" / "kitty" / "kitty.conf")
            (home / ".config" / "wezterm").mkdir(parents=True)
            shutil.copy2(ROOT / "adapters" / "wezterm" / "wezterm.lua", home / ".config" / "wezterm" / "wezterm.lua")
            (home / ".config" / "superset").mkdir(parents=True)
            shutil.copy2(ROOT / "adapters" / "superset" / "terminal.json", home / ".config" / "superset" / "terminal.json")
            shutil.copy2(ROOT / "adapters" / "tmux" / "tmux.conf", home / ".tmux.conf")

            env = dict(
                os.environ,
                HOME=str(home),
                XDG_CONFIG_HOME=str(home / ".config"),
                GHOSTTY_CONFIG_DIR=str(repo),
                GHOSTTY_CONFIG_PATH=str(repo / "config"),
            )
            cases = (
                ("batman", "Gotham Noir - Year One", "#15171a", "#d8d6cf", "#f0c946", "gotham_noir_year_one.yaml"),
                ("batcomputer", "Gotham Noir - Batcomputer", "#101215", "#dce0e5", "#f5d042", "gotham_noir_batcomputer.yaml"),
                ("arkham", "Gotham Noir - Arkham Slate", "#1d1f21", "#dad5c7", "#e6c15a", "gotham_noir_arkham_slate.yaml"),
                ("vengeance", "Gotham Noir - Vengeance", "#151417", "#ddd8d5", "#e5535c", "gotham_noir_vengeance.yaml"),
            )
            for alias, expected_name, bg, fg, cursor, warp_file in cases:
                with self.subTest(alias=alias):
                    subprocess.run([str(repo / "bin" / "ghostty-theme"), alias, "--all"], env=env, check=True, capture_output=True)
                    self.assertIn(f"theme = {expected_name}", (repo / "config").read_text(encoding="utf-8"))
                    for ide in ("Code", "Cursor", "Antigravity", "Antigravity IDE", "Windsurf"):
                        s = json.loads((app_support / ide / "User" / "settings.json").read_text(encoding="utf-8"))
                        c = s["workbench.colorCustomizations"]
                        self.assertEqual(c["terminal.background"], bg)
                        self.assertEqual(c["terminal.foreground"], fg)
                        self.assertEqual(c["terminalCursor.foreground"], cursor)

                    z = json.loads((home / ".config" / "zed" / "settings.json").read_text(encoding="utf-8"))
                    self.assertEqual(z["experimental.theme_overrides"]["terminal.background"], bg)

                    ala = tomllib.loads((home / ".config" / "alacritty" / "alacritty.toml").read_text(encoding="utf-8"))
                    self.assertEqual(ala["colors"]["primary"]["background"], bg)
                    self.assertEqual(ala["colors"]["primary"]["foreground"], fg)

                    self.assertIn(f"background {bg}", (home / ".config" / "kitty" / "kitty.conf").read_text(encoding="utf-8"))
                    self.assertIn(f"background = '{bg}'", (home / ".config" / "wezterm" / "wezterm.lua").read_text(encoding="utf-8"))
                    self.assertIn(f"bg={bg}", (home / ".tmux.conf").read_text(encoding="utf-8"))
                    self.assertTrue((home / ".warp" / "themes" / warp_file).exists())

                    sup = json.loads((home / ".config" / "superset" / "terminal.json").read_text(encoding="utf-8"))
                    self.assertEqual(sup["terminal"]["theme"], expected_name)

    @unittest.skipUnless(shutil.which("ghostty"), "ghostty CLI not available")
    def test_gotham_noir_themes_validate_in_ghostty(self) -> None:
        for name in LORE_THEMES:
            theme_path = ROOT / "themes" / name
            self.assertTrue(theme_path.exists(), f"Missing {theme_path}")
            res = subprocess.run(
                ["ghostty", "+validate-config", f"--config-file={theme_path}"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, f"{name}: {res.stderr}\n{res.stdout}")
        res_main = subprocess.run(
            ["ghostty", "+validate-config", f"--config-file={ROOT / 'config'}"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_main.returncode, 0, f"Main config failed: {res_main.stderr}\n{res_main.stdout}")


if __name__ == "__main__":
    unittest.main()
