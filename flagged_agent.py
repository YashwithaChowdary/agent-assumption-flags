"""
Assumption and Confidence Flags for an AI Agent
-----------------------------------------------
A small harness that sits between "say nothing" and "stop and ask".

Each agent step carries: the work done, the assumptions behind it, and a
confidence score. The harness then picks one of four actions:

  CONTINUE  - confident, no assumptions: keep going silently
  FLAG      - assumptions present: show an inline flag, keep going
  DEFER     - medium confidence: pin a question for later, keep going
  ASK       - low confidence: stop and ask the human now

At the end the human gets a short review: pinned questions, flagged
assumptions, and can accept the result with a caveat.

The agent here is scripted so the demo runs offline. Swap ScriptedAgent for
a class that calls an LLM API; the harness does not change.
"""
from dataclasses import dataclass, field
from enum import Enum


class Action(Enum):
    CONTINUE = "continue"
    FLAG = "flag"
    DEFER = "defer"
    ASK = "ask"


@dataclass
class Step:
    text: str
    confidence: float                      # 0.0 - 1.0
    assumptions: list = field(default_factory=list)
    wrong_assumption: bool = False         # used only for evaluation


def decide(step, ask_below=0.5, defer_below=0.75):
    """The policy: how much human attention does this step deserve?"""
    if step.confidence < ask_below:
        return Action.ASK
    if step.assumptions and step.confidence < defer_below:
        return Action.DEFER
    if step.assumptions:
        return Action.FLAG
    return Action.CONTINUE


class ScriptedAgent:
    """Stand-in for an LLM agent working on 'summarise monthly sales'."""
    def __init__(self):
        self.steps = [
            Step("Loaded sales.csv (1,240 rows)", 0.95),
            Step("Treated the 'date' column as day-month-year", 0.80,
                 ["Dates are DD/MM/YYYY, not MM/DD/YYYY"], wrong_assumption=True),
            Step("Dropped 38 rows with missing 'amount'", 0.70,
                 ["Missing amount means no sale, not unknown"]),
            Step("Converted all amounts to SEK at a fixed rate", 0.40,
                 ["Fixed rate 1 EUR = 11.0 SEK is acceptable"]),
            Step("Grouped by month and summed amount", 0.92),
            Step("Wrote summary table to report.md", 0.90),
        ]

    def run(self):
        yield from self.steps


class Harness:
    def __init__(self, answer_fn):
        self.answer_fn = answer_fn         # how the human answers an ASK
        self.log, self.pinned, self.flags = [], [], []

    def run(self, agent):
        for i, step in enumerate(agent.run(), 1):
            action = decide(step)
            self.log.append((i, step, action))
            print(f"[{i}] {step.text}  (confidence {step.confidence:.2f})")
            if action is Action.FLAG:
                self.flags.append((i, step))
                print(f"    FLAG   assumed: {'; '.join(step.assumptions)}")
            elif action is Action.DEFER:
                self.pinned.append((i, step))
                print(f"    PINNED for later: {'; '.join(step.assumptions)}")
            elif action is Action.ASK:
                print(f"    ASK    I'm unsure: {'; '.join(step.assumptions)}")
                print(f"    human: {self.answer_fn(step)}")
        self.review()

    def review(self):
        print("\n--- Review ---")
        print(f"Steps: {len(self.log)} | flagged: {len(self.flags)} | "
              f"pinned: {len(self.pinned)} | asked: "
              f"{sum(a is Action.ASK for _, _, a in self.log)}")
        for i, s in self.pinned:
            print(f"  Pinned question (step {i}): {s.assumptions[0]}?")
        for i, s in self.flags:
            print(f"  Flagged assumption (step {i}): {s.assumptions[0]}")
        print("Accept result with caveat: unresolved pinned questions above.")

    def evaluate(self):
        """Did the harness surface every step with a wrong assumption?"""
        wrong = [i for i, s, _ in self.log if s.wrong_assumption]
        surfaced = [i for i, s, a in self.log
                    if s.wrong_assumption and a is not Action.CONTINUE]
        print(f"\nWrong assumptions: {wrong} | surfaced to human: {surfaced}")
        return len(surfaced) == len(wrong)


if __name__ == "__main__":
    h = Harness(answer_fn=lambda step: "Yes, use the fixed rate for now.")
    h.run(ScriptedAgent())
    print("All wrong assumptions surfaced:", h.evaluate())
