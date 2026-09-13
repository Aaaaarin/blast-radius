# Devpost form: copy-paste blocks

Deadline: 12 Sep 2026, 5:30 PM PDT. Track: Automated Software Engineering (fallback: Other). Mode: online.

## Project name (60 chars)

Blast Radius

## Elevator pitch (200 chars)

Change one line, see exactly what it can break, and run only the tests that matter. Import-graph impact analysis and risk scoring for any Python repo, no LLM, no cloud.

## About the project (Markdown)

## Inspiration

Every pull request asks the same question: what else does this touch? Most teams answer it by running the whole suite and hoping, or by asking a language model to guess. I wanted a deterministic answer that fits in one process and works on a plane.

## What it does

Blast Radius reads your uncommitted diff, maps every changed line to the function it lives in, walks the repo's import graph to find every module and test downstream, scores the risk of the change with named reasons, and runs just the impacted tests. A live force graph shows the change (black), everything it reaches (orange), and the tests that need to run (blue).

The demo: one line changes inside `apply_discount()` in a synthetic shop backend. The graph lights up cart, payments and checkout. Four of ten test files are selected. Three fail in under three seconds. The bug is caught before the PR exists. The full suite finds the same failures and also runs six files that could not have been affected.

## How I built it

- `blastradius/graph.py`: import graph from Python's `ast`, resolving absolute and relative imports to in-repo modules and recording every function's line span.
- `blastradius/diff.py`: parses `git diff -U0` hunks and maps touched lines to functions.
- `blastradius/engine.py`: breadth-first search over the reverse import graph, depth and "via" path per module, risk score from breadth, depth, sensitive paths (payment, auth, pricing, migration) and missing test coverage.
- `blastradius/server.py` and `ui.html`: one FastAPI process serving a D3 console with a "run impacted only" button that shells out to pytest.
- CLI: `python -m blastradius --repo . --run` does the same thing without a browser, for CI.

Standard library for all analysis. FastAPI is the only dependency beyond pytest. No external services, offline-first.

## Challenges

Relative-import resolution inside packages, mapping diff hunks to function spans (the `-U0` trick), and keeping the whole thing one command to run. The risk model went through three versions before the reasons read like something a reviewer would actually say.

## Accomplishments

- 6 of 6 own tests passing, analysis under 300 ms on a 21-module repo.
- Impacted-only run selects 4 of 10 test files on the demo change and still catches every failure.
- Built and shipped solo in one sitting.

## What I learned

Static import graphs get you most of the way to test-impact analysis without instrumentation. The hard part is presentation: a risk number nobody trusts is useless, so every point on the score has a reason next to it.

## What's next

- Call-graph-level propagation (function to function, not module to module) to shrink the selected set further.
- A GitHub Action that comments the blast radius and the impacted-test result on every PR.
- JavaScript and Go graph builders plugging into the same engine.

## Disclosures

AI products: Claude Code (Anthropic), model Claude Fable 5.1, used as a pair programmer throughout the build. All design decisions (wedge, risk model, demo arc) are mine. No paid services, sponsored credits, or donated resources. No LLM runs inside the product.

## Built with (tags)

python, fastapi, uvicorn, pytest, d3.js, ast, git, html, javascript

## Try it out links

- https://github.com/Aaaaarin/blast-radius

## Video demo link

Upload `media/blast-radius-demo.mp4` to YouTube (unlisted is fine) and paste the link.

## Image gallery

media/01-clean.png, media/02-blast-radius.png, media/03-impacted-tests-fail.png, media/04-run-all.png
