"""Free live smoke tests against https://aigifmaker.ai. No generation runs."""
import os
import subprocess
import sys
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "aigifmaker.py")


def run(*args, key=None):
    env = {k: v for k, v in os.environ.items() if k != "AIGIFMAKER_API_KEY"}
    if key:
        env["AIGIFMAKER_API_KEY"] = key
    return subprocess.run([sys.executable, SCRIPT, *args], env=env, capture_output=True, text=True, timeout=90)


class LiveSmoke(unittest.TestCase):
    def test_invalid_key_is_auth(self):
        r = run("credits", key="sk-invalidtest000")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("invalid API key", r.stderr)

    def test_no_key_hits_wall(self):
        r = run("generate", "smoke test: a blinking star")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("API key is required", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
