# Testing Strategy — Mortgage Concierge

## Four-Tier Testing Pyramid

### Tier 1: Unit Tests (`tests/unit/`)
- **Scope**: Individual tool functions, model validation, helper functions
- **Framework**: pytest with `@pytest.mark.asyncio`
- **Isolation**: `DummyToolContext` / `MockToolContext` for tool tests, `monkeypatch` for env vars
- **Speed**: < 1 second total
- **Coverage target**: All deterministic tool logic
- **Run**: `uv run python -m pytest tests/unit/ -v`

### Tier 2: Integration Tests (`tests/integration/`)
- **Scope**: Full tool chains (calculate → recalculate → simulate → evaluate)
- **Framework**: pytest with mocked HTTP endpoints
- **Isolation**: Mock `requests.post`, never call real APIs
- **Speed**: < 10 seconds total
- **Coverage target**: Cross-tool data flow, state propagation
- **Run**: `uv run python -m pytest tests/integration/ -v`

### Tier 3: Eval Tests (`tests/eval/`)
- **Scope**: Agent behavior — tool selection, response quality, conversation flow
- **Framework**: ADK `AgentEvaluator` with evalset JSON
- **Isolation**: Full agent execution against test cases
- **Speed**: 30-120 seconds (depends on LLM latency)
- **Coverage target**: All tool invocation patterns, response accuracy
- **Thresholds**: tool_trajectory >= 0.8, response_match >= 0.7
- **Run**: `adk eval mortgage_concierge tests/eval/data/<evalset>.evalset.json --config_file_path=tests/eval/data/test_config.json`

### Tier 4: Adversarial Tests (via `/adversary` skill)
- **Scope**: Agent resilience against malicious/edge-case inputs
- **Framework**: Custom adversarial generation + eval scoring
- **Modes**: prompt-injection, edge-case-borrower, conversation-stress, hallucination-probe
- **Coverage target**: Security, robustness, factual grounding
- **Run**: `/adversary <mode> [iterations]`

## Test Data
- Mock API responses: `tests/unit/data/*.json`
- Evalset files: `tests/eval/data/*.evalset.json`
- Eval config: `tests/eval/data/test_config.json`
- Recorded sessions: `tests/eval/data/recorded-sessions/`

## TDD vs Eval-DD

| Code Type | Test Approach | Test Location |
|-----------|--------------|---------------|
| Tool functions | TDD (unit tests) | `tests/unit/test_<tool>.py` |
| Pydantic models | TDD (unit tests) | `tests/unit/test_<model>.py` |
| State helpers | TDD (unit tests) | `tests/unit/test_state_helpers.py` |
| Agent prompts | Eval-DD (eval tests) | `tests/eval/data/<evalset>.evalset.json` |
| Tool selection | Eval-DD (eval tests) | `tests/eval/data/<evalset>.evalset.json` |
| Response quality | Eval-DD (eval tests) | `tests/eval/data/<evalset>.evalset.json` |
