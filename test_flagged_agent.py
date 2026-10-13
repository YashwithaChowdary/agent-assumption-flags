import unittest
from flagged_agent import Step, Action, decide, Harness, ScriptedAgent


class DecideTests(unittest.TestCase):
    def test_confident_step_continues(self):
        self.assertEqual(decide(Step("x", 0.95)), Action.CONTINUE)

    def test_assumption_with_high_confidence_is_flagged(self):
        self.assertEqual(decide(Step("x", 0.85, ["a"])), Action.FLAG)

    def test_assumption_with_medium_confidence_is_deferred(self):
        self.assertEqual(decide(Step("x", 0.6, ["a"])), Action.DEFER)

    def test_low_confidence_asks(self):
        self.assertEqual(decide(Step("x", 0.3, ["a"])), Action.ASK)


class HarnessTests(unittest.TestCase):
    def test_wrong_assumption_is_surfaced(self):
        h = Harness(answer_fn=lambda s: "ok")
        h.run(ScriptedAgent())
        self.assertTrue(h.evaluate())


if __name__ == "__main__":
    unittest.main()
