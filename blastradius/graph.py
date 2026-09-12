"""Build an import graph for a Python repo using only the standard library."""
from __future__ import annotations
import ast
import os
from dataclasses import dataclass, field


@dataclass
class Module:
    name: str            # dotted module name, e.g. shop.pricing
    path: str            # absolute file path
    imports: set[str] = field(default_factory=set)
    functions: dict[str, tuple[int, int]] = field(default_factory=dict)  # name -> (start, end line)
    is_test: bool = False


def _module_name(root: str, path: str) -> str:
    rel = os.path.relpath(path, root).replace(os.sep, "/")
    if rel.endswith("__init__.py"):
        rel = rel[: -len("__init__.py")].rstrip("/")
    else:
        rel = rel[:-3]
    return rel.replace("/", ".")


def _resolve(imported: str, known: set[str]) -> str | None:
    """Map an imported dotted name to the longest known in-repo module prefix."""
    parts = imported.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in known:
            return cand
    return None


SKIP_DIRS = {"node_modules", "__pycache__", "venv", ".venv", "media", "build", "dist"}


def build_graph(root: str) -> dict[str, Module]:
    root = os.path.abspath(root)
    modules: dict[str, Module] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            name = _module_name(root, path)
            if not name:
                continue
            posix = path.replace(os.sep, "/")
            is_test = fn.startswith("test_") or fn.endswith("_test.py") or "/tests/" in posix
            modules[name] = Module(name=name, path=path, is_test=is_test)

    known = set(modules)
    for mod in modules.values():
        try:
            with open(mod.path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=mod.path)
        except (SyntaxError, UnicodeDecodeError):
            continue
        parts = mod.name.split(".")
        is_pkg = mod.path.endswith("__init__.py")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    r = _resolve(alias.name, known)
                    if r and r != mod.name:
                        mod.imports.add(r)
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    keep = len(parts) - node.level + (1 if is_pkg else 0)
                    up = parts[:max(keep, 0)]
                    base = ".".join(up + ([base] if base else []))
                candidates = [base] + [f"{base}.{a.name}" if base else a.name for a in node.names]
                for c in candidates:
                    r = _resolve(c, known)
                    if r and r != mod.name:
                        mod.imports.add(r)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                end = getattr(node, "end_lineno", node.lineno)
                mod.functions[node.name] = (node.lineno, end)
    return modules


def reverse_graph(modules: dict[str, Module]) -> dict[str, set[str]]:
    dependents: dict[str, set[str]] = {m: set() for m in modules}
    for mod in modules.values():
        for imp in mod.imports:
            dependents.setdefault(imp, set()).add(mod.name)
    return dependents
