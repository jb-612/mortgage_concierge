---
# Unconditional — always loaded
---

# Development Workflow Rules

## Mandatory Gate Sequence

Every code change MUST follow this workflow in order. Do not skip gates.

### 1. Feature Spec (GATE)
- Run `/feature-spec <epic> <feature> <name>`
- Creates `.workitems/PNN-FNN-<name>/` with `design.md` and `tasks.md`
- GATE: Workitem folder must exist before proceeding

### 2. Design Review (GATE)
- Run `/design-review <workitem-path>`
- Reviews design for completeness, architecture alignment, ADK patterns
- GATE: Design status must be `APPROVED` before implementation begins

### 3. Task Breakdown
- Run `/task-breakdown <workitem-path>`
- Decomposes feature into atomic tasks tagged `[TDD]` or `[Eval-DD]`
- Each task = one testable behavior change

### 4. Implementation
- **TDD tasks**: `/tdd-task` — RED→GREEN→REFACTOR with 3-agent separation
- **Eval-DD tasks**: `/eval-baseline` first, then `/prompt-tune`
- GATE: Each task must have passing test/eval before marking complete

### 5. Code Review (GATE)
- Run `/code-review [workitem-path]`
- Three-pass review: prerequisites+architecture, quality+security, test+eval coverage
- GATE: All passes must succeed

### 6. Commit
- Run `/commit`
- Conventional commit message with `Refs: PNN-FNN-TNN`
- Pre-checks: workitem exists, design approved, tests pass, no secrets
- NEVER push to Git without asking for permission

## Exceptions

- **Bug fixes**: May skip Feature Spec if referencing an existing workitem
- **Documentation-only**: May skip Design Review
- **Test-only**: May skip Design Review but must reference a workitem
- **Initial setup**: require-workitem hook exits 0 if no .workitems/ directory exists
