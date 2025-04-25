# Evaluation Tests for Mortgage Concierge

This directory contains comprehensive evaluation tests for the Mortgage Concierge application using the ADK evaluation framework.

## Structure

- `test_eval.py` - Main test script using AgentEvaluator
- `data/` - Directory containing test data
  - `loan_calculator.evalset.json` - Test cases for loan calculator functionality
  - `test_config.json` - Evaluation criteria configuration
  - `recorded-sessions/` - Directory for evalset files recorded from web sessions

## Test Scenarios

The evaluation tests cover the following scenarios:

1. Basic mortgage calculation
2. Interest rate recalculation
3. Loan term recalculation
4. Comparison of multiple loan terms
5. Comparison of different interest rates
6. Maximum affordable loan amount calculation

## Running Evaluation Tests

### Using pytest

```bash
# Run the evaluation tests
python -m pytest tests/eval/test_eval.py -v
```

### Using ADK CLI

```bash
# Run with evalset file
adk eval mortgage_concierge tests/eval/data/loan_calculator.evalset.json --config_file_path=tests/eval/data/test_config.json --print_detailed_results

# Run with recorded session
adk eval mortgage_concierge tests/eval/data/recorded-sessions/evalset67a47d.evalset.json --config_file_path=tests/eval/data/test_config.json --print_detailed_results
```

### Recording Web Sessions

To record a web session for evaluation:

1. Start the ADK web server:
```bash
adk web mortgage_concierge
```

2. Access the web interface at http://localhost:8080
3. Create a conversation with the agent
4. In the Eval tab, click "Add Current Session"
5. Save the evalset file

The recorded sessions will be saved in the project root. Move them to the `tests/eval/data/recorded-sessions/` directory for organization.

### Using the ADK Web UI

1. Start the ADK web server:
```bash
adk web mortgage_concierge
```

2. Access the web interface at http://localhost:8080
3. Navigate to the Eval tab
4. Select the evalset file to run

## Evaluation Criteria

- Tool trajectory score: 0.8 (80% accuracy expected)
- Response match score: 0.7 (70% similarity expected)

## Adding New Test Cases

To add new test cases:

1. Edit the `loan_calculator.evalset.json` file
2. Add a new test case with:
   - `query`: The user's question
   - `expected_tool_use`: Tools the agent should use
   - `reference`: Expected response from the agent

## Continuous Integration

These tests can be integrated into CI/CD pipelines to ensure agent behavior remains consistent across code changes.