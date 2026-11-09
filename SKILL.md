---
name: aigifmaker
description: Turn a text prompt into an animated GIF with AI GIF Maker (aigifmaker.ai), using the user's own API key in AIGIFMAKER_API_KEY. Use when the user asks for a GIF, a reaction GIF, an animated greeting or a looping sticker from a description. Text to GIF only; no frame count, size, photo-to-GIF or editing.
license: MIT
---

# AI GIF Maker

Turn text into animated GIFs with AI GIF Maker. Native GIF generation — no video conversion. Type what you want and download your GIF in about a minute.

This skill calls [AI GIF Maker](https://aigifmaker.ai/?utm_source=skill&utm_medium=package) over its HTTP API with the user's key.

## When to use it

- "Make me a GIF of a cat doing a backflip"
- "A happy birthday GIF for Sam with balloons"
- "A looping reaction GIF: a dog shrugging"
- The user asks how many credits they have left

Not available: choosing the frame count or size, turning a photo into a GIF, or editing an existing GIF. Say so instead of trying.

## Before the first GIF

The key must be in `AIGIFMAKER_API_KEY`. If it is missing, tell the user to create one at https://aigifmaker.ai/settings/apikeys and set it; do not ask them to paste it into chat.

Each GIF costs 1 credit on the user's AI GIF Maker account, the same as on the website. New accounts get one free GIF (it carries a small aigifmaker.ai badge). Check the balance first (free), and confirm with the user before making several GIFs in a row.

## The script

`scripts/aigifmaker.py` (Python 3 standard library only):

```bash
python3 scripts/aigifmaker.py credits                    # remaining credits, free
python3 scripts/aigifmaker.py generate "a corgi in sunglasses dancing on a beach, looping"
python3 scripts/aigifmaker.py status <task id>            # the raw task record
```

`generate` submits, polls every 3 seconds for up to 15 minutes and prints the GIF URL. Download it as binary and hand the file to the user, or give them the URL.

Exit codes: `0` ok · `2` no key or bad key · `3` out of credits (send the user to the [pricing](https://aigifmaker.ai/pricing?utm_source=skill&utm_medium=package) page) · `4` the prompt was refused or a cooldown is active (reword it, do not resend the same text) · `5` the generation failed (its credit is refunded; try once more) · `6` still running after 15 minutes (check later with `status`, do not resubmit).

## The API, if you would rather call it directly

All responses are HTTP 200; `{"code":0,"data":{…}}` is success, `{"code":-1,"message":"…"}` a refusal. Send `Authorization: Bearer $AIGIFMAKER_API_KEY`.

```bash
curl -s -X POST https://aigifmaker.ai/api/ai/generate \
  -H "Authorization: Bearer $AIGIFMAKER_API_KEY" -H "Content-Type: application/json" \
  -d '{"provider":"openlux","mediaType":"image","model":"gif-maker-v1","scene":"text-to-image",
       "prompt":"a corgi in sunglasses dancing on a beach","options":{"output_format":"gif"}}'
# -> data.id

curl -s -X POST https://aigifmaker.ai/api/ai/query \
  -H "Authorization: Bearer $AIGIFMAKER_API_KEY" -H "Content-Type: application/json" \
  -d '{"taskId":"<data.id>"}'
# -> data.status pending | processing | success | failed; data.images[0] is the GIF
```

Keep the request body exactly as shown; only `prompt` changes.

## Things that happen

- **`queued: true` while `status` is `processing`**: an account that has not bought credits yet waits in a short queue (`queueEta` seconds). Keep polling.
- **`data.wall: true` with `code: 0`**: the request went out without a key. Set `AIGIFMAKER_API_KEY`.
- **`invalid API key`**: the key is wrong or deleted; create a new one.
- **`insufficient credits`**: the account is empty.
- **`status: failed`**: read `errorMessage`; with `failureKind: "moderation"` the prompt was refused, so rewrite it. A failed GIF gives its credit back.
