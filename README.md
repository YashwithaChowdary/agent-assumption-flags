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
    set LLM_MODEL=gemini-3.5-flash-lite      (optional, picks the model)
    py llm_eval.py

If no key is set, the script asks for one when it starts (the input is hidden and the key is never saved). Replies that are not valid JSON are retried up to three times; a task that never parses is excluded from the scores instead of being counted as wrong.

Results are written to `results.md` and `results.json`. The unit tests run the same pipeline offline with a fake model.

## Results (first run)

Model: `gemini-3.5-flash-lite`, 5 tasks, one run, temperature 0.

| Task | Plain answer correct | Confidence | Harness action | Trap named |
|---|---|---|---|---|
| Ambiguous dates | False | 1.00 | flag | True |
| Missing values | True | 0.50 | defer | True |
| Unknown exchange rate | False | 0.95 | flag | True |
| Unclear time frame | False | 1.00 | flag | True |
| Unit mismatch | True | 1.00 | flag | True |

- 3 of 5 plain answers were silently wrong. The harness surfaced all 3.
- The model reported 0.95 to 1.00 confidence on those 3 wrong answers, so the stated assumptions carried the signal, not the confidence score.
- The harness also flagged both correct answers, so it is not selective yet.
- Limits: five tasks, one model, one run, hand-picked thresholds, no user study. The traps and the correctness checks are my own, so this shows the idea works on small cases and is not a benchmark.

## Status

Prototype. `flagged_agent.py` uses a scripted agent; `llm_eval.py` runs a real model on five small tasks. Next: more tasks, a rule for how many assumptions should count as a flag, and a user study.