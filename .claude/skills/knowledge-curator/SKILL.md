---
name: knowledge-curator
description: Manage bank docs and loan tracks in the knowledge base
argument-hint: "[add|validate|test-search] [file-path]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Knowledge Base Curator

Mode: $ARGUMENTS

## Mode: add
1. Validate file format (.txt or .md)
2. Place in `_knowledge_base/bank_docs/`
3. Verify ingestion by testing search after bootstrap

## Mode: validate
1. List all files in `_knowledge_base/bank_docs/` and `_knowledge_base/json/`
2. Check file sizes and encoding
3. Verify `interest_tracks.json` has valid JSON structure
4. Report document count and coverage areas

## Mode: test-search
1. Run test queries against `search_bank_docs`
2. Verify relevant documents are returned
3. Report retrieval quality metrics

## Key Files
- `_knowledge_base/bank_docs/` (bank documents)
- `_knowledge_base/json/interest_tracks.json` (loan tracks)
- `mortgage_concierge/shared_libraries/memory_ingestion.py` (ingestion logic)
