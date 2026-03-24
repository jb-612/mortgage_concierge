---
name: code-review
description: Three-pass code review checking prerequisites, code quality, and test/eval coverage
argument-hint: "[workitem-path]"
allowed-tools: Read, Glob, Grep, Bash
---

# Code Review

Review code changes for $ARGUMENTS (or current branch changes if no argument).

## Pass 1 — Prerequisites & Architecture
- Workitem exists with `APPROVED` design
- All tasks marked `[x]` complete in tasks.md
- Layer separation: tools in `mortgage_concierge/tools/`, models in `sub_agents/*/models.py`
- No circular imports (check with grep for cross-layer imports)
- State contracts match `constants.py`

## Pass 2 — Code Quality & Security
- Run `radon cc -s -n C` on modified files — flag CC > 5
- Check for hardcoded secrets, API keys, credentials
- OWASP basics: no eval/exec, no unsafe deserialization, no SQL injection patterns
- Import order: stdlib → third-party → local
- Docstrings on public functions
- Pydantic models have Field descriptions

## Pass 3 — Test & Eval Coverage
- For each [TDD] task: verify test exists in `tests/unit/` or `tests/integration/`
- For each [Eval-DD] task: verify eval case exists in `tests/eval/data/`
- Run `uv run python -m pytest tests/unit/ --tb=short` — report results
- Check eval thresholds in `test_config.json` have not been lowered
- New tools must have at least one eval case

## Verdict
- **LGTM**: All passes succeed
- **LGTM_WITH_NITS**: Minor issues that don't block merge
- **REQUEST_CHANGES**: Blocking issues found — list each with severity
