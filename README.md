# Assumption and Confidence Flags for an AI Agent

A small Python prototype for the space between "say nothing" and "stop and ask a full question" when a human works with an AI agent.

Each agent step carries a confidence score and the assumptions behind it. The harness then chooses how much human attention the step needs:

| Action | When | What the human sees |
|---|---|---|
| Continue | high confidence, no assumptions | nothing |
| Flag | assumptions, high confidence | an inline note |
| Defer | assumptions, medium confidence | a pinned question for later |
| Ask | low confidence | the agent stops and asks |

At the end there is a short review: pinned questions, flagged assumptions, and the option to accept the result with a caveat.

## Run

    python flagged_agent.py

The demo agent is scripted, so it runs offline and needs no API key.

## Test

    python -m unittest test_flagged_agent.py test_llm_eval.py

## Evaluate with a real LLM

`llm_eval.py` runs five small tasks, each with a built-in trap (ambiguous dates, missing values, unknown exchange rate, unclear time frame, unit mismatch). For each task the model answers twice: plain, and flagged (answer plus confidence and assumptions). The harness then decides whether to continue, flag, pin or ask. The script reports how many plain answers were silently wrong and how many of those the harness surfaced.

    set GEMINI_API_KEY=your_key      (or ANTHROPIC_API_KEY)
    py llm_eval.py

Results are written to `results.md` and `results.json`. The unit tests run the same pipeline offline with a fake model.

## Status

Prototype. `flagged_agent.py` uses a scripted agent; `llm_eval.py` uses a real model on five small tasks. Thresholds are hand-picked and there are no user studies yet.