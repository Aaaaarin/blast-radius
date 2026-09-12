"""Compute blast radius, risk score and the minimal test set for a change."""
from __future__ import annotations
import os
import time
from collections import deque
from dataclasses import dataclass, field, asdict

from .graph import build_graph, reverse_graph, Module
from .diff import changed_lines, functions_hit, rel_to_module

SENSITIVE = {
    "payment": 35, "billing": 30, "auth": 30, "login": 30, "crypto": 30, "secret": 30,
    "migration": 30, "checkout": 25, "permission": 25, "session": 20, "token": 20,
    "pricing": 20, "schema": 20, "admin": 20,
}


@dataclass
class Impact:
    module: str
    depth: int
    via: str
    is_test: bool
    sensitive: bool


@dataclass
class Report:
    root: str
    base: str
    changed_modules: list[str]
    changed_functions: dict[str, list[str]]
    impacted: list[Impact]
    tests_selected: list[str]
    tests_total: int
    tests_changed: bool
    risk_score: int
    risk_level: str
    risk_reasons: list[str]
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    analysis_ms: float = 0.0
    module_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def _sensitive(name: str) -> tuple[bool, int, str | None]:
    low = name.lower()
    for key, weight in SENSITIVE.items():
        if key in low:
            return True, weight, key
    return False, 0, None


def analyze(root: str, base: str = "HEAD", changed_override: list[str] | None = None) -> Report:
    t0 = time.perf_counter()
    root = os.path.abspath(root)
    modules = build_graph(root)
    dependents = reverse_graph(modules)

    changed_functions: dict[str, list[str]] = {}
    changed_modules: list[str] = []
    if changed_override:
        changed_modules = [m for m in changed_override if m in modules]
    else:
        for rel, lines in changed_lines(root, base).items():
            name = rel_to_module(rel)
            if name in modules:
                changed_modules.append(name)
                changed_functions[name] = functions_hit(modules[name].functions, lines)

    depth: dict[str, int] = {m: 0 for m in changed_modules}
    via: dict[str, str] = {m: m for m in changed_modules}
    q = deque(changed_modules)
    while q:
        cur = q.popleft()
        for dep in sorted(dependents.get(cur, ())):
            if dep not in depth:
                depth[dep] = depth[cur] + 1
                via[dep] = cur
                q.append(dep)

    impacted = [
        Impact(module=m, depth=d, via=via[m], is_test=modules[m].is_test, sensitive=_sensitive(m)[0])
        for m, d in sorted(depth.items(), key=lambda kv: (kv[1], kv[0]))
        if d > 0
    ]
    all_tests = sorted(m for m in modules if modules[m].is_test)
    tests_selected = sorted(m for m in depth if modules[m].is_test)
    tests_changed = any(modules[m].is_test for m in changed_modules)

    score = 0
    reasons: list[str] = []
    prod_impacted = [i for i in impacted if not i.is_test]
    if prod_impacted:
        pts = min(40, 8 * len(prod_impacted))
        score += pts
        reasons.append(f"{len(prod_impacted)} production modules downstream (+{pts})")
    max_depth = max((i.depth for i in impacted), default=0)
    if max_depth >= 2:
        score += 10
        reasons.append(f"impact reaches depth {max_depth} (+10)")
    for m in changed_modules + [i.module for i in prod_impacted]:
        hit, w, key = _sensitive(m)
        if hit:
            score += w
            reasons.append(f"sensitive path '{key}' in {m} (+{w})")
            break
    if changed_modules and not tests_selected:
        score += 25
        reasons.append("no test covers the changed modules (+25)")
    if changed_modules and not tests_changed and prod_impacted:
        score += 10
        reasons.append("production code changed, no test file changed (+10)")
    score = min(100, score)
    level = "LOW" if score < 30 else "MEDIUM" if score < 60 else "HIGH"
    if not changed_modules:
        level, reasons = "NONE", ["working tree matches base"]

    nodes = []
    for m, mod in modules.items():
        state = "changed" if m in changed_modules else "impacted" if m in depth else "clean"
        nodes.append({"id": m, "state": state, "depth": depth.get(m, -1), "test": mod.is_test,
                      "sensitive": _sensitive(m)[0]})
    edges = [{"source": mod.name, "target": imp} for mod in modules.values() for imp in mod.imports]

    return Report(
        root=root, base=base, changed_modules=changed_modules, changed_functions=changed_functions,
        impacted=impacted, tests_selected=tests_selected, tests_total=len(all_tests),
        tests_changed=tests_changed, risk_score=score, risk_level=level, risk_reasons=reasons,
        nodes=nodes, edges=edges, analysis_ms=round((time.perf_counter() - t0) * 1000, 2),
        module_count=len(modules),
    )


def test_paths(report: Report, modules: dict[str, Module] | None = None) -> list[str]:
    modules = modules or build_graph(report.root)
    return [modules[m].path for m in report.tests_selected if m in modules]
