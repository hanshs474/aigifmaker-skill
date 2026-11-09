"""Unit tests for scripts/aigifmaker.py against the real response shapes (mocked; no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import aigifmaker as a  # noqa: E402


def ok(data):
    return {"code": 0, "message": "ok", "data": data}


def fake(calls, polls, submit_reply=None):
    polls = list(polls)

    def t(path, body, key):
        calls.append((path, body, key))
        if path == "/api/ai/generate":
            return submit_reply or ok({"id": "t1", "status": "pending", "taskId": "up-1"})
        if path == "/api/ai/query":
            return ok(polls.pop(0))
        return ok({"remainingCredits": 42, "made": 3})

    return t


class ScriptTests(unittest.TestCase):
    def setUp(self):
        os.environ["AIGIFMAKER_API_KEY"] = "sk-abc"

    def test_success(self):
        calls = []
        t = fake(calls, [{"status": "processing"}, {"status": "success", "images": ["https://cdn/x.gif"], "watermarked": [False]}])
        self.assertEqual(a.wait(a.submit("a dancing cat", t), poll_every=0, transport=t), "https://cdn/x.gif")
        self.assertEqual(calls[0], ("/api/ai/generate", {"provider": "openlux", "mediaType": "image", "model": "gif-maker-v1", "scene": "text-to-image", "prompt": "a dancing cat", "options": {"output_format": "gif"}}, "sk-abc"))
        self.assertEqual(calls[1][1], {"taskId": "t1"})

    def test_queued(self):
        t = fake([], [{"status": "processing", "queued": True, "queueEta": 30}, {"status": "success", "images": ["https://cdn/q.gif"]}])
        self.assertEqual(a.wait("t1", poll_every=0, transport=t), "https://cdn/q.gif")

    def test_failed(self):
        t = fake([], [{"status": "failed", "errorMessage": "upstream error"}])
        with self.assertRaises(a.Fail) as cm:
            a.wait("t1", poll_every=0, transport=t)
        self.assertEqual(cm.exception.exit_code, 5)

    def test_refusals(self):
        cases = [
            ({"code": -1, "message": "invalid API key — create one at https://aigifmaker.ai/settings/apikeys"}, 2),
            (ok({"wall": True, "reason": "anon_credits", "cost": 1, "remaining": 0, "grant": 0}), 2),
            ({"code": -1, "message": "insufficient credits"}, 3),
            ({"code": -2, "message": "slow down"}, 4),
            ({"code": -1, "message": "prompt too long"}, 1),
        ]
        for reply, exit_code in cases:
            with self.assertRaises(a.Fail) as cm:
                a.submit("x", fake([], [], reply))
            self.assertEqual(cm.exception.exit_code, exit_code, reply)

    def test_credits(self):
        self.assertEqual(a.credits(fake([], [])), 42)


if __name__ == "__main__":
    unittest.main()
