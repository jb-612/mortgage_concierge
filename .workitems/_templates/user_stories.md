---
id: Pnn/Fnn
parent_id: Pnn
type: user_stories
version: 1
status: draft
dependencies: []
tags: []
created_by: planner
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# User Stories: Feature Name

## US-01: Story Title

**As a** borrower chatting with the mortgage concierge
**I want** [capability]
**So that** [benefit]

### Acceptance Criteria

- [ ] Agent calls the correct tool without asking permission
- [ ] Response includes [specific data points]
- [ ] Session state is updated with [key(s)]

### Conversation Scenario

**User says**: "example user message"
**Agent does**: calls `tool_name(params)` then responds with [description]
**State after**: `state_key` contains [expected value]

### Eval Mapping

| Criterion | Test type | Artifact |
|-----------|-----------|----------|
| Correct tool called | Eval-DD | `feature.evalset.json` entry N |
| Return data valid | TDD | `test_tool.py::test_name` |
| State updated | TDD | `test_tool.py::test_state` |

---

## US-02: Story Title

**As a** borrower chatting with the mortgage concierge
**I want** [capability]
**So that** [benefit]

### Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

### Conversation Scenario

**User says**: "example user message"
**Agent does**: [expected behavior]
**State after**: [expected state changes]

### Eval Mapping

| Criterion | Test type | Artifact |
|-----------|-----------|----------|
| Criterion 1 | TDD/Eval-DD | artifact path |

---

## Edge Cases

| Scenario | Expected Behavior | Test Type |
|----------|-------------------|-----------|
| Missing prerequisite state | Agent explains what's needed | Eval-DD |
| Invalid input values | Tool returns error, agent explains | TDD + Eval-DD |
| Multiple valid interpretations | Agent picks most likely, confirms | Eval-DD |
| Adversarial input | Agent maintains role, no hallucination | Eval-DD |
