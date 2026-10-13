import json
import unittest
from llm_eval import TASKS, run_task, summarise


def fake_llm(prompt):
    """Offline stand-in: plain run is confidently wrong, flagged run hedges."""
    if "confidence" in prompt:
        return json.dumps({"answer": "3", "confidence": 0.6,
                           "assumptions": ["I assumed MM/DD date format"]})
    return json.dumps({"answer": "3"})


class EvalTests(unittest.TestCase):
    def test_pipeline_runs_and_catches_silent_mistake(self):
        rows = [run_task(t, llm=fake_llm) for t in TASKS]
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["action"] != "continue" for r in rows))
        self.assertIn("Surfaced by the harness", summarise(rows))

    def test_json_inside_text_is_parsed(self):
        from llm_eval import parse
        self.assertEqual(parse('Sure!\n{"answer": 4}\nDone')["answer"], 4)


if __name__ == "__main__":
    unittest.main()
