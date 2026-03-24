---
paths:
  - "tests/**/*.py"
---

# Testing Rules

## Unit Tests (tests/unit/)

1. Use `@pytest.mark.asyncio` for all async test functions
2. Mock tool context with `DummyToolContext` or `MockToolContext`:
   ```python
   class DummyToolContext:
       def __init__(self):
           self.state = {}
           self.session_id = "test-session-123"
           self.save_artifact = MagicMock(return_value="artifact-123")
   ```
3. NEVER call live API endpoints — use `monkeypatch`, `MagicMock`, `AsyncMock`
4. Use mock JSON files from `tests/unit/data/` for API response fixtures
5. Use `@pytest.fixture` for reusable test data
6. Use `@pytest.mark.parametrize` for table-driven tests

## Integration Tests (tests/integration/)

7. Mock HTTP calls (`requests.post`), do not call real APIs
8. Test full tool chains: calculate → recalculate → simulate → evaluate

## Eval Tests (tests/eval/)

9. Use `AgentEvaluator.evaluate()` from `google.adk.evaluation`
10. Evalset entries: `{query, expected_tool_use: [{tool_name, tool_input}], reference}`
11. Thresholds from `test_config.json`: tool_trajectory >= 0.8, response_match >= 0.7
12. NEVER lower thresholds without explicit justification
13. Before modifying prompts/tools: capture eval baseline, verify no regression after
14. Recorded sessions in `tests/eval/data/recorded-sessions/`
