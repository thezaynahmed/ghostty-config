#!/usr/bin/env python3
"""Install owned hooks with backups, preserving user configuration and theme choice."""
import argparse
import pathlib
import re
import shlex
import time


def configure(path: pathlib.Path, repo: pathlib.Path) -> bool:
    original = path.read_text() if path.exists() else ""
    content = re.sub(
        r"(?m)^# >>> ghostty shell (?:prompt|adapter) >>>\n.*?^# <<< ghostty shell (?:prompt|adapter) <<<\n?",
        "", original, flags=re.DOTALL,
    )
    # Migrate the legacy standalone source line produced by install.sh.
    hook = str(repo / "adapters/zsh/ade-terminal.zsh")
    lines = []
    for line in content.splitlines():
        try:
            tokens = shlex.split(line, comments=True)
        except ValueError:
            tokens = []
        if len(tokens) == 2 and tokens[0] in ("source", ".") and tokens[1] == hook:
            continue
        lines.append(line)
    content = "\n".join(lines)
    prompt_block = (
        "# >>> ghostty shell prompt >>>\n"
        f"source {shlex.quote(str(repo / 'adapters/zsh/prompt-select.zsh'))}\n"
        "# <<< ghostty shell prompt <<<\n"
    )
    # Oh My Zsh must see the selected profile before it starts a competing theme.
    omz = re.search(r"(?m)^\s*(?:source|\.)\s+[^\n]*oh-my-zsh\.sh[^\n]*$", content)
    if omz:
        content = content[:omz.start()] + prompt_block + content[omz.start():]
    else:
        content += "\n" + prompt_block
    content = content.rstrip() + (
        "\n\n# >>> ghostty shell adapter >>>\n"
        f"source {shlex.quote(hook)}\n"
        "# <<< ghostty shell adapter <<<\n"
    )
    if content == original:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(f"{path.name}.backup.{time.time_ns()}")
        backup.write_text(original)
        backup.chmod(path.stat().st_mode & 0o777)
        print(f"Backup: {backup}")
    path.write_text(content)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zshrc", type=pathlib.Path)
    parser.add_argument("repo", type=pathlib.Path)
    args = parser.parse_args()
    print("Zsh hooks updated." if configure(args.zshrc, args.repo.resolve()) else "Zsh hooks already current.")
