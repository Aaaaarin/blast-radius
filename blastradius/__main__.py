"""CLI: python -m blastradius --repo <path> [--base HEAD] [--run] [--serve]"""
import argparse
import json
import subprocess
import sys

from .engine import analyze, test_paths


def main() -> int:
    ap = argparse.ArgumentParser(prog="blastradius")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--run", action="store_true", help="run only the impacted tests")
    ap.add_argument("--serve", action="store_true", help="start the web console")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()

    if a.serve:
        import uvicorn
        from . import server
        server.REPO = a.repo
        server.BASE = a.base
        uvicorn.run(server.app, host="127.0.0.1", port=a.port, log_level="warning")
        return 0

    r = analyze(a.repo, a.base)
    if a.json:
        print(json.dumps(r.to_dict(), indent=2))
    else:
        print(f"Blast Radius  ({r.analysis_ms} ms, {r.module_count} modules)")
        print(f"  changed : {', '.join(r.changed_modules) or '-'}")
        for m, fns in r.changed_functions.items():
            print(f"            {m}: {', '.join(fns) or 'module-level'}")
        prod = [i for i in r.impacted if not i.is_test]
        print(f"  impacted: {len(prod)} modules, {len(r.tests_selected)}/{r.tests_total} tests")
        for i in r.impacted:
            tag = "  [sensitive]" if i.sensitive else ""
            print(f"            d{i.depth} {i.module}  (via {i.via}){tag}")
        print(f"  risk    : {r.risk_level} {r.risk_score}/100")
        for why in r.risk_reasons:
            print(f"            - {why}")
    if a.run and r.tests_selected:
        paths = test_paths(r)
        print(f"\nRunning {len(paths)} impacted test files with pytest...")
        return subprocess.call([sys.executable, "-m", "pytest", "-q", *paths], cwd=r.root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
