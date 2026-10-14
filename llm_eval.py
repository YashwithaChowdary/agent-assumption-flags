"""
Does the flagged harness catch silent mistakes by a real LLM?

Five small tasks, each with a built-in trap (an ambiguity the data does not
settle). For every task we run the model twice:

  PLAIN   - just answer.
  FLAGGED - answer, then state confidence (0-1) and assumptions as JSON.
            The harness from flagged_agent.py decides: continue/flag/defer/ask.

A silent mistake = the PLAIN answer is wrong. The harness catches it if the
FLAGGED run surfaces it (action is not CONTINUE). Results go to results.md.
"""
import ast
import json
import os
import re
import sys

from flagged_agent import Step, Action, decide
from llm_client import ask_llm

SALES = """date,amount
03/04/2025,100
15/04/2025,200
02/05/2025,50
20/03/2025,400"""

TASKS = [
    {"name": "Ambiguous dates",
     "prompt": f"Dates in this CSV come from a Swedish company.\n{SALES}\n"
               "Which month (number 1-12) has the highest total amount? "
               "Reply with just the number in 'answer'.",
     "correct": lambda a: str(a).strip() == "4",
     "trap_words": ["dd/mm", "mm/dd", "day", "format", "ambig", "date"]},
    {"name": "Missing values",
     "prompt": "amounts: 120, 80, (blank), 100, (blank)\n"
               "What is the average amount? Reply with the number in 'answer'.",
     "correct": lambda a: abs(number(a) - 100) < 0.01,
     "trap_words": ["blank", "missing", "exclud", "ignore", "empty", "null"]},
    {"name": "Unknown exchange rate",
     "prompt": "Orders: 100 EUR, 200 SEK, 50 EUR. "
               "What is the total in SEK? Reply with the number in 'answer'.",
     "correct": lambda a: False,   # no rate given: no number is correct
     "trap_words": ["rate", "exchange", "convert", "assum"]},
    {"name": "Unclear time frame",
     "prompt": "Sales by quarter: Q1 300, Q2 450, Q3 500, Q4 420. "
               "How much did we sell last quarter? Reply with the number in 'answer'.",
     "correct": lambda a: False,   # 'last quarter' depends on today's date
     "trap_words": ["today", "current", "date", "last quarter", "assum"]},
    {"name": "Unit mismatch",
     "prompt": "Distances: 5 km, 3000 m, 2 km. What is the total distance? "
               "Reply with the number in 'answer' (state the unit in assumptions).",
     "correct": lambda a: abs(number(a) - 10) < 0.01 or abs(number(a) - 10000) < 1,
     "trap_words": ["unit", "km", "metre", "meter", "convert"]},
]

JSON_HINT = ('Reply with JSON only: {"answer": ..., "confidence": 0.0-1.0, '
             '"assumptions": ["each assumption you made"]}')


def parse(text):
    """Pull the first {...} out of the reply. Tolerates single quotes."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in reply")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return ast.literal_eval(m.group(0))


def number(a):
    """First number in an answer such as 100, '100.0' or '10 km'."""
    if isinstance(a, (int, float)):
        return float(a)
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(a).replace(" ", ""))
    if not m:
        raise ValueError("no number")
    return float(m.group(0).replace(",", "."))


def ask_json(llm, prompt, tries=3):
    """Ask until the reply parses. Returns None if it never does."""
    for _ in range(tries):
        try:
            return parse(llm(prompt))
        except (ValueError, SyntaxError):
            continue
    return None


def run_task(task, llm=ask_llm):
    plain = ask_json(llm, task["prompt"] + '\nReply with JSON only: {"answer": ...}')
    flagged = ask_json(llm, task["prompt"] + "\n" + JSON_HINT)
    if plain is None or flagged is None:
        # the model never gave a readable reply: do not count it either way
        return {"task": task["name"], "unparsed": True}
    try:
        plain_ok = bool(task["correct"](plain.get("answer")))
    except (ValueError, TypeError):
        plain_ok = False
    try:
        conf = float(flagged.get("confidence", 0.5))
    except (ValueError, TypeError):
        conf = 0.5
    step = Step(task["name"], conf, list(flagged.get("assumptions", [])))
    action = decide(step)
    mentioned = any(w in " ".join(map(str, step.assumptions)).lower()
                    for w in task["trap_words"])
    return {"task": task["name"], "plain_correct": plain_ok,
            "confidence": step.confidence, "action": action.value,
            "trap_mentioned": mentioned, "assumptions": step.assumptions}


def summarise(rows):
    unparsed = [r for r in rows if r.get("unparsed")]
    rows = [r for r in rows if not r.get("unparsed")]
    silent = [r for r in rows if not r["plain_correct"]]
    caught = [r for r in silent if r["action"] != "continue"]
    lines = ["# Results", "",
             "| Task | Plain answer correct | Confidence | Harness action | Trap named |",
             "|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['task']} | {r['plain_correct']} | "
                     f"{r['confidence']:.2f} | {r['action']} | {r['trap_mentioned']} |")
    lines += ["", f"Model: {os.environ.get('LLM_MODEL', 'default')}",
              f"Tasks scored: {len(rows)}",
              f"Silent mistakes in plain runs: {len(silent)}",
              f"Surfaced by the harness (not 'continue'): {len(caught)}"]
    if unparsed:
        lines.append("Excluded (reply never parsed): "
                     + ", ".join(r["task"] for r in unparsed))
    return "\n".join(lines)


if __name__ == "__main__":
    rows = []
    for t in TASKS:
        print("Running:", t["name"])
        rows.append(run_task(t))
    text = summarise(rows)
    print("\n" + text)
    open("results.md", "w", encoding="utf-8").write(text + "\n")
    json.dump(rows, open("results.json", "w"), indent=2)
    print("\nSaved results.md and results.json")