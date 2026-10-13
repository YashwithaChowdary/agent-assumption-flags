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

The demo agent is scripted, so it runs offline and needs no API key. To use a real model, replace `ScriptedAgent` with a class that returns `Step` objects from an LLM.

## Test

    python -m unittest test_flagged_agent.py

## Status

Prototype. The agent in this demo is scripted and the thresholds are hand-picked. It has not been tested with real users.
