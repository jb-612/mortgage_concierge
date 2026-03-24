---
name: eval-analyst
description: Deep analysis of ADK eval results with failure pattern identification and improvement suggestions
argument-hint: "[eval-output-path | 'latest']"
allowed-tools: Read, Bash, Glob, Grep
---

# Eval Result Analyst

Analyze: $ARGUMENTS

## Process

1. Run eval or read saved results
2. Categorize failures:
   - **Tool trajectory**: wrong tool called, wrong arguments, missing tool call
   - **Response match**: missing information, incorrect values, wrong format
3. Identify patterns:
   - Which tools are most often called incorrectly?
   - Which query patterns cause failures?
   - Are failures correlated with specific prompt sections?
4. Suggest improvements:
   - Prompt adjustments for tool selection issues
   - Eval case updates for response match issues
   - New eval cases for uncovered scenarios
5. Create regression test cases from failure patterns
6. Compare against previous baselines for trend tracking
