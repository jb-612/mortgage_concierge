# Integration Tests for Mortgage Concierge

This directory contains integration tests for the Mortgage Concierge application, focusing on testing the full flows of key features.

## Test Types

1. **Unit-Level Integration Tests**: These tests validate the interaction between closely related components without requiring an external ADK API server. They use mocking to simulate the environment.

2. **ADK API Server Tests**: These tests use the ADK API server to run full agent interactions, allowing for end-to-end testing of agent behavior.

## Running the Tests

### Unit-Level Integration Tests

These can be run with pytest:

```bash
# Run specific test
python -m pytest tests/integration/test_loan_calculator_integration.py::TestLoanCalculatorIntegration::test_full_calculation_flow -v

# Run all integration tests
python -m pytest tests/integration/ -v
```

### ADK API Server Tests

1. Start the ADK API server:
```bash
adk api_server --port 8765
```

2. Run the test script:
```bash
python tests/integration/run_adk_tests.py
```

Alternatively, run the test marked with the `@pytest.mark.skip` decorator by explicitly selecting it:
```bash
python -m pytest tests/integration/test_loan_calculator_integration.py::TestLoanCalculatorIntegration::test_agent_with_adk_server -v
```

## Test Data

- **loan_calculator.test.json**: Contains test cases for the loan calculator flow
- **test_config.json**: Contains the evaluation criteria for the test cases

## ADK Evaluation

For more comprehensive evaluation using ADK's built-in evaluation tools:

```bash
adk eval mortgage_concierge tests/integration/loan_calculator.test.json --config_file_path=tests/integration/test_config.json --print_detailed_results
```

## Next Steps

1. Add more detailed test cases for different loan scenarios
2. Add tests for the multi-track simulation functionality (Phase 3)
3. Add additional mock scenarios for fallback testing
4. Create an evaluation dataset (.evalset.json) for more comprehensive testing