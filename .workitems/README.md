# Work Items

Structured planning artifacts for the mortgage concierge agent. Created before implementation begins.

## Naming Convention

Two-level hierarchy: `PNN/FNN-<snake_case_name>/`
- `PNN/` = Phase directory (P01 = Core, P02 = Quality, P03 = Hardening, P04 = Features)
- `FNN-name/` = Feature folder within phase

Reserved directories:
- `_templates/` = workitem folder templates

Examples: `P01/F01-borrower_profiling/`, `P04/F02-package_comparison/`

## Files Per Feature

| File | Purpose | Created By |
|------|---------|------------|
| `design.md` | Conversation flow, tool interface, state contract, eval strategy | Planner |
| `user_stories.md` | Borrower-facing scenarios with conversation examples | Planner |
| `tasks.md` | Atomic tasks tagged `[TDD]` or `[Eval-DD]` with status tracking | Planner |

All files include YAML frontmatter with: `id`, `parent_id`, `type`, `version`, `status`.

## Templates

```bash
mkdir -p .workitems/PNN/FNN-name
cp .workitems/_templates/*.md .workitems/PNN/FNN-name/
```

The `/feature-spec` skill handles this automatically.

## Rules

1. **Plan before code** — workitem must exist before implementation
2. **Design verdict required** — `status: approved` before coding starts
3. **Tasks are atomic** — each task < 2 hours, one testable behavior
4. **TDD for tools** — deterministic tool logic tested with pytest
5. **Eval-DD for behavior** — prompt/routing changes tested with ADK evals
6. **State keys declared** — all new state keys added to `constants.py`
7. **Every file <= 100 lines** — split the feature if exceeded

## Design Verdict Values

| Status | Meaning |
|--------|---------|
| `draft` | Initial creation, not yet reviewed |
| `reviewed` | Design review complete |
| `approved` | Approved, ready for implementation |
| `changes_required` | Must address findings first |

## Progress Tracking

Update `master-plan.md` when:
- A new feature is created: add entry with `[ ]`
- A feature reaches 100%: mark `[x]` and update Done count
