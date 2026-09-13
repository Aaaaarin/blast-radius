# Demo script (60 s)

Setup: `run.bat`, open http://127.0.0.1:8000, tree clean.

| t | screen | narration |
|---|---|---|
| 0-8 s | clean console, 21 nodes grey | Every pull request asks the same question: what else does this touch? Most teams answer it by running the whole suite and hoping. |
| 8-18 s | `python demo.py break`, click Re-analyze, graph lights up | One line changes inside apply_discount. Blast Radius maps the line to the function, walks the import graph, and lights up everything downstream: cart, payments, checkout. Risk HIGH, with reasons. |
| 18-30 s | Run impacted only, three failures | It selects four of ten test files and runs them. Three fail. The bug is caught before the PR exists. |
| 30-40 s | Run all | The full suite finds the same failures and runs six files that could not have been affected. |
| 40-52 s | reset, clean again | No LLM, no cloud, standard library plus one FastAPI process. Analysis takes under 300 milliseconds. |
| 52-60 s | README | Blast Radius. Change one line, see what it can break. Repo link in the description. |

Reset path: `python demo.py reset` then Re-analyze.
