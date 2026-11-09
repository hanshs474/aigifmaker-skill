#!/usr/bin/env python3
"""Make an animated GIF from text on AI GIF Maker (https://aigifmaker.ai).

    python3 scripts/aigifmaker.py credits
    python3 scripts/aigifmaker.py generate "a corgi in sunglasses dancing on a beach"
    python3 scripts/aigifmaker.py status <task id>

Reads the key from AIGIFMAKER_API_KEY. Standard library only.
Exit codes: 0 ok · 2 auth (no / bad key) · 3 out of credits · 4 rejected prompt ·
5 generation failed · 6 still running after the timeout · 1 anything else.
"""
from __future__ import annotations

import http.client as http_client
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("AIGIFMAKER_BASE_URL", "https://aigifmaker.ai").rstrip("/")
KEYS_URL = "https://aigifmaker.ai/settings/apikeys"
PRICING_URL = "https://aigifmaker.ai/pricing"


class Fail(Exception):
    def __init__(self, message, exit_code=1):
        super().__init__(message)
        self.exit_code = exit_code


def http(path, body, key):
    headers = {"Content-Type": "application/json", "User-Agent": "aigifmaker-skill/0.1.0"}
    if key:
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(BASE_URL + path, data=json.dumps(body or {}).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        raw = e.read() or b""
    try:
        return json.loads(raw)
    except ValueError:
        return {"code": -1, "message": raw[:200].decode("utf-8", "replace")}


def unwrap(env):
    """Every response is HTTP 200; the JSON code tells success (0) from refusal."""
    code = env.get("code")
    data = env.get("data") if isinstance(env.get("data"), dict) else {}
    if code == 0:
        if data.get("wall"):
            raise Fail(f"an API key is required: create one at {KEYS_URL} and set AIGIFMAKER_API_KEY", 2)
        return data
    msg = str(env.get("message") or "unexpected response")
    low = msg.lower()
    if "invalid api key" in low or "no auth" in low:
        raise Fail(msg, 2)
    if "insufficient credits" in low:
        raise Fail(f"{msg}. Top up at {PRICING_URL}", 3)
    if isinstance(code, int) and code not in (0, -1):
        raise Fail(msg, 4)
    raise Fail(msg, 1)


def call(path, body, transport=None):
    key = os.environ.get("AIGIFMAKER_API_KEY") or None
    return unwrap((transport or http)(path, body, key))


def submit(prompt, transport=None):
    data = call(
        "/api/ai/generate",
        {
            "provider": "openlux",
            "mediaType": "image",
            "model": "gif-maker-v1",
            "scene": "text-to-image",
            "prompt": prompt,
            "options": {"output_format": "gif"},
        },
        transport,
    )
    if not data.get("id"):
        raise Fail("the service returned no task id")
    return str(data["id"])


def status(task_id, transport=None):
    return call("/api/ai/query", {"taskId": task_id}, transport)


def wait(task_id, timeout=300.0, poll_every=3.0, transport=None):
    deadline = time.monotonic() + timeout
    while True:
        try:
            data = status(task_id, transport)
        except (OSError, http_client.HTTPException):
            data = {}  # a dropped poll is not a failed generation
        state = str(data.get("status") or "").lower()
        if state == "success" and data.get("images"):
            return str(data["images"][0])
        if state in ("failed", "canceled"):
            msg = str(data.get("errorMessage") or f"the GIF {state}")
            raise Fail(msg, 4 if data.get("failureKind") == "moderation" else 5)
        if time.monotonic() >= deadline:
            raise Fail(f"task {task_id} is still running; check it later with: status {task_id}", 6)
        time.sleep(poll_every)


def credits(transport=None):
    return int(call("/api/user/get-user-credits", None, transport).get("remainingCredits") or 0)


def main(argv):
    if len(argv) < 2 or argv[1] not in ("generate", "status", "credits"):
        print(__doc__.strip(), file=sys.stderr)
        return 1
    try:
        if argv[1] == "credits":
            print(credits())
        elif argv[1] == "status":
            print(json.dumps(status(argv[2]), indent=2))
        else:
            prompt = " ".join(argv[2:]).strip()
            if not prompt:
                raise Fail("give a prompt: generate \"<what the GIF shows>\"")
            print(wait(submit(prompt)))
        return 0
    except Fail as e:
        print("error: " + str(e), file=sys.stderr)
        return e.exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
