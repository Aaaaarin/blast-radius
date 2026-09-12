"""Read the working-tree diff and map changed lines to functions."""
from __future__ import annotations
import re
import subprocess

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def changed_lines(root: str, base: str = "HEAD") -> dict[str, set[int]]:
    """Return {relative/path.py: {new line numbers touched}} for the diff against base."""
    try:
        out = subprocess.run(
            ["git", "diff", "-U0", base, "--", "."],
            cwd=root, capture_output=True, text=True, check=False,
        ).stdout
        prefix = subprocess.run(
            ["git", "rev-parse", "--show-prefix"], cwd=root, capture_output=True, text=True, check=False,
        ).stdout.strip()
    except FileNotFoundError:
        return {}
    result: dict[str, set[int]] = {}
    current = None
    for line in out.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            if p == "/dev/null":
                current = None
            else:
                current = p[2:] if p.startswith("b/") else p
                if prefix and current.startswith(prefix):
                    current = current[len(prefix):]
                if not current.endswith(".py"):
                    current = None
                    continue
                result.setdefault(current, set())
        elif line.startswith("@@") and current:
            m = HUNK.match(line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2)) if m.group(2) is not None else 1
                result[current].update(range(start, start + max(count, 1)))
    return result


def functions_hit(functions: dict[str, tuple[int, int]], lines: set[int]) -> list[str]:
    hit = []
    for name, (s, e) in functions.items():
        if any(s <= ln <= e for ln in lines):
            hit.append(name)
    return hit


def rel_to_module(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel.endswith("__init__.py"):
        rel = rel[: -len("__init__.py")].rstrip("/")
    else:
        rel = rel[:-3]
    return rel.replace("/", ".")
