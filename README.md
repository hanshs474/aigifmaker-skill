# aigifmaker skill

Turn text into animated GIFs with AI GIF Maker. Native GIF generation — no video conversion. Type what you want and download your GIF in about a minute.

An agent skill (Claude Code, Codex, Cursor and other agents that read `SKILL.md`) that makes GIFs with [AI GIF Maker](https://aigifmaker.ai/?utm_source=skill&utm_medium=package) using your own API key. Ask your agent for "a GIF of a cat doing a backflip" and it comes back with the GIF.

## Install

Copy this folder (with `SKILL.md` and `scripts/`) into your agent's skills directory, for example:

```bash
git clone https://github.com/hanshs474/aigifmaker-skill ~/.claude/skills/aigifmaker
```

Then create a key at https://aigifmaker.ai/settings/apikeys and set it:

```bash
export AIGIFMAKER_API_KEY=sk-...
```

The script needs Python 3 and nothing else.

## Cost

Each GIF costs 1 credit on your AI GIF Maker account, the same as on the website. New accounts get one free GIF (it carries a small aigifmaker.ai badge). A GIF that fails to generate gives its credit back. Credit packs are on the [pricing](https://aigifmaker.ai/pricing?utm_source=skill&utm_medium=package) page.

## What it covers

- text to GIF through submit and poll, returning the GIF URL
- the credit balance (free to check)
- the queue an account without purchased credits may wait in
- what each refusal means and what to do next (no key, bad key, out of credits, refused prompt, failed run)

Text to GIF only: no frame count, size, photo-to-GIF or editing.

## Tests

```bash
python3 -m unittest tests/test_script.py   # mocked, offline
python3 tests/smoke_live.py                 # two free live checks, no generation
```

MIT licensed. Questions: support@aigifmaker.ai
