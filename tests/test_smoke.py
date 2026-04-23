import asyncio
import os
import tempfile
import unittest
from pathlib import Path

from core.brain import SecurityBrain
from core.cli_engine import ClaudeCLIPredator
from shadow import ShadowPredator


class ShadowSwarmSmokeTests(unittest.TestCase):
    def test_collect_candidate_files_returns_target_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target_file = Path(temp_dir) / "app.py"
            target_file.write_text("print('hello')\n", encoding="utf-8")

            predator = ShadowPredator(str(target_file))

            self.assertEqual(predator.collect_candidate_files(), [target_file.resolve()])

    def test_security_brain_reports_missing_key(self):
        previous_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            brain = SecurityBrain()
            result = asyncio.run(brain.audit_file("demo.py", "print('hello')"))
        finally:
            if previous_key is not None:
                os.environ["ANTHROPIC_API_KEY"] = previous_key

        self.assertIsInstance(result, dict)
        self.assertEqual(result["severity"], "ERROR")
        self.assertIn("ANTHROPIC_API_KEY", result["finding"])

    def test_cli_engine_reports_missing_binary(self):
        cli = ClaudeCLIPredator(claude_bin="")
        messages = []

        exit_code = cli.run_adversarial_audit(".", "test task", messages.append)

        self.assertEqual(exit_code, 127)
        self.assertTrue(messages)
        self.assertEqual(messages[0]["type"], "error")


if __name__ == "__main__":
    unittest.main()
