# Integration Tests for Mortgage Concierge

This directory contains integration tests for the Mortgage Concierge application, focusing on testing the full flows of key features.

## Test Types

1. **Unit-Level Integration Tests**: These tests validate the interaction between closely related components without requiring an external ADK API server. They use mocking to simulate the environment.

2. **ADK API Server Tests**: These tests use the ADK API server to run full agent interactions, allowing for end-to-end testing of agent behavior.

3. **ADK Evaluation Tests**: These use the ADK evaluation framework to comprehensively validate agent behavior against expected trajectories.

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

### ADK Evaluation Framework

The ADK evaluation framework offers more comprehensive testing:

```bash
# Run with a single test file
adk eval mortgage_concierge tests/integration/loan_calculator.test.json --config_file_path=tests/integration/test_config.json --print_detailed_results

# Create an evaluation file from a web session
adk web mortgage_concierge  # Then add sessions to an eval set via the UI
```

## Test Data

- **loan_calculator.test.json**: Contains test cases for the loan calculator flow
- **test_config.json**: Contains the evaluation criteria for the test cases

## Structure of Test Files

### test_loan_calculator_integration.py
Unit tests that validate the loan calculator tools integration, with both live API and fallback modes.

### loan_calculator.test.json
A sequence of test cases that validate:
1. Initial user profile information storage
2. Initial loan calculation
3. Rate recalculation  
4. Term recalculation

### run_adk_tests.py
Script for running tests against a live ADK API server, validating full agent functionality.

## Creating an Evaluation Set

For more comprehensive evaluation, create an `.evalset.json` file with multiple test sessions:

```bash
# Create a new directory for evaluation tests
mkdir -p tests/eval/data

# Create a test_eval.py file similar to the eval.example/test_eval.py
# Create an evalset.json file with multiple test sessions
```

## Next Steps

1. **Full Evaluation Set**: Create a comprehensive evaluation dataset with multiple sessions
2. **Testing Infrastructure**: Add GitHub actions for automated evaluation testing
3. **Extended Test Scenarios**: Add test coverage for Phase 3's multi-track simulation
4. **Reference Outputs**: Improve reference outputs with more detailed financial explanations
5. **Test Metrics**: Track custom metrics like accuracy of financial calculations