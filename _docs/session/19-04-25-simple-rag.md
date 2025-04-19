 I’ve added two simple FunctionTools and wired them into your agent:

    • Created mortgage_concierge/tools/bank_docs.py
      – search_bank_docs(query) scans a configurable directory of .txt files for your query and returns
    filename/snippet matches.
      – Path is driven by BANK_DOCS_PATH (env, default _knowledge_base/bank_docs).

    • Created mortgage_concierge/tools/loan_tracks.py
      – list_loan_tracks() loads and returns the contents of a configurable JSON file of loan‑track scenarios.
      – Path is driven by LOAN_TRACKS_PATH (env, default _knowledge_base/loan_tracks.json).

    • Updated agent.py to import and register these two tools in root_agent.tools.

    • Enhanced your Phase 1 prompt to tell the agent when and how to call these tools for factual grounding and
    product listing.

    • Extended .env.example with the two new environment variables.

    Next, spin up the server with:

      adk web mortgage_concierge

    Then in the UI try prompts like:

      “What does our bank policy say about maximum LTV?”
      (“search_bank_docs('maximum LTV')” → snippets → agent summarizes)

      “Show me the repayment tracks we offer.”
      (“list_loan_tracks()” → JSON list → agent walks through options)

 I discovered that FunctionTool only takes your function as its one positional argument (it infers tool.name
    from the function’s name and its docstring), so I:

    • Renamed the internal impl functions back to “_…_impl”
    • Overrode their name to the desired tool name (e.g. "search_bank_docs")
    • Wrapped them simply with FunctionTool(_impl_func)

    I also removed the LiteLlm import (and dependency on litellm) by passing the raw model ID string
    into Agent(model=MODEL_ID). That gets routed through ADK’s LLMRegistry under the covers.

    With these fixes:

      • search_bank_docs now constructs a proper FunctionTool
      • list_loan_tracks likewise
      • your agent no longer crashes on import

    I’ve updated your agent definition so that any openai/… model string (like your openai/gpt-4.1-nano) is now
    automatically wrapped in LiteLLM rather than being treated as a Google model. Specifically:

    • After reading MODEL_ID, we try: to import LiteLlm.
    • If the model string starts with openai/ and LiteLLM is available, we replace it with LiteLlm(model=…).
    • We then pass that _LLM_MODEL into your Agent instead of the raw string.

    With this in place, ADK will invoke the LiteLLM/OpenAI backend and won’t try (and fail) to look up
    openai/gpt-4.1-nano as a Google model.

  I’ve extended the search_bank_docs tool so that:

    • BANK_DOCS_PATH can now point to either
      – A directory (it will pick up both .txt and .md files), or
      – A single file (of any extension you point it at, e.g. your mortgage-poalim-heb.md).
    • If it’s neither a dir nor a file, it still errors, but now .md files in a dir or a lone file path will work.

    Next steps:

        1. Restart your ADK service so the new code is picked up.
        2. Leave your `.env` pointing `BANK_DOCS_PATH` at either:
            * The folder (`…/_knowledge_base/bank_docs`), or

            * Directly to the `.md` file you want (`…/bank_docs/mortgage-poalim-heb.md`).
        3. Try again: `search_bank_docs("…")` should now find and return snippets from your Hebrew markdown.