---
name: tdd-task
description: Orchestrate a TDD RED-GREEN-REFACTOR cycle using three specialized agents
argument-hint: "<workitem-path> <task-number>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# TDD Task Orchestration

Execute TDD for task $ARGUMENTS.

## Prerequisites
- Read tasks.md, find the specified task
- Verify task is tagged `[TDD]` (for `[Eval-DD]`, suggest `/prompt-tune` instead)
- Verify design.md is `APPROVED`

## Setup
1. Derive project hash: `echo -n "<project-dir>" | md5`
2. Create marker directory: `mkdir -p /tmp/mc-tdd-markers/`

## RED Phase
1. Write marker: `echo "test-writer" > /tmp/mc-tdd-markers/<hash>`
2. Spawn `tdd-test-writer` agent with task context
3. Agent writes ONE failing test
4. Verify test fails: `uv run python -m pytest <test>::<func> -v`

## GREEN Phase
1. Write marker: `echo "code-writer" > /tmp/mc-tdd-markers/<hash>`
2. Spawn `tdd-code-writer` agent with failing test context
3. Agent writes minimum code to pass
4. Verify test passes: `uv run python -m pytest <test>::<func> -v`

## REFACTOR Phase
1. Write marker: `echo "refactorer" > /tmp/mc-tdd-markers/<hash>`
2. Spawn `tdd-refactorer` agent
3. Agent improves code quality while keeping tests green
4. Verify all tests pass: `uv run python -m pytest tests/ -v`

## Cleanup
1. Remove marker: `rm -f /tmp/mc-tdd-markers/<hash>`
2. Mark task `[x]` in tasks.md
3. Report: TDD cycle summary
