---
name: eval-baseline
description: Run ADK evaluations and capture current scores as a baseline before making changes
argument-hint: "[workitem-path]"
allowed-tools: Read, Write, Bash, Glob
---

# Eval Baseline Capture

Capture eval scores for $ARGUMENTS.

## Steps

1. Find all evalset files: `ls tests/eval/data/*.evalset.json`
2. For each evalset, run:
   ```
   adk eval mortgage_concierge tests/eval/data/<file> \
     --config_file_path=tests/eval/data/test_config.json \
     --print_detailed_results
   ```
3. Parse output to extract:
   - `tool_trajectory_avg_score`
   - `response_match_score`
   - Per-query breakdown
4. Store results in `.workitems/<current>/eval-baseline.json`:
   ```json
   {
     "timestamp": "<ISO-8601>",
     "evalsets": {
       "<evalset-name>": {
         "tool_trajectory_avg_score": 0.85,
         "response_match_score": 0.72
       }
     },
     "thresholds": {
       "tool_trajectory_avg_score": 0.8,
       "response_match_score": 0.7
     }
   }
   ```
5. Report scores in a table format

## Regression Check
When run AFTER changes, compare against existing baseline:
- Flag any metric that dropped below baseline
- Flag any metric that dropped below config thresholds
- Display delta table (before/after/change)
