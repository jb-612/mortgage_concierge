---
name: commit
description: Create a conventional commit with workitem traceability and pre-commit checks
argument-hint: "[-m message]"
allowed-tools: Read, Glob, Grep, Bash
---

# Commit with Traceability

## Pre-Commit Checks (all must pass)
1. Run `uv run python -m pytest tests/unit/ --tb=short` — all tests pass
2. Scan staged files for secrets (API keys, passwords, .env content)
3. Verify no `.env` files are staged
4. Check if a workitem can be inferred from changed files

## Commit Message Format
```
<type>(<scope>): <short description>

<body — what changed and why>

Refs: PNN-FNN-TNN
Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `eval`, `chore`
Scopes: `tools`, `agents`, `models`, `state`, `prompt`, `eval`, `config`

## Rules
- NEVER push without asking for permission
- Use HEREDOC for commit message formatting
- Stage specific files, not `git add -A`
