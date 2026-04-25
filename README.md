# yotron-hermes-fork

Thin patch overlay on `nousresearch/hermes-agent:latest`.

Inserts Lark/Feishu **sender open_id** into the agent's message context so
the agent can pass per-user identity to `lark_*` MCP tools (via the companion
`yotron-lark-bridge` service) for true per-user OAuth routing.

## What it changes

One pattern in `gateway/run.py` (around line 3962):

```python
# Original
if _is_shared_multi_user and source.user_name:
    message_text = f"[{source.user_name}] {message_text}"

# Patched (this fork)
if (source.platform.value == "feishu" and source.user_name and source.user_id):
    message_text = (
        f"[Lark sender: {source.user_name} (open_id={source.user_id})] "
        f"{message_text}"
    )
elif _is_shared_multi_user and source.user_name:
    message_text = f"[{source.user_name}] {message_text}"
```

Effect: Every Lark inbound message (DM and group, isolated and shared sessions)
is prefixed with the sender's identity. The agent reads the open_id from the
prefix and passes it to lark_* tools.

Telegram, Discord, etc. are untouched — only `feishu` platform triggers the
new branch.

## Image

- `ghcr.io/roy6732856/yotron-hermes:latest` — patched image
- `ghcr.io/roy6732856/yotron-hermes:git-<sha>` — pinned to commit

## How to use

In Zeabur (or any container host), pull `ghcr.io/roy6732856/yotron-hermes:latest`
instead of `nousresearch/hermes-agent:latest`. Same env vars, same volume,
same entrypoint. Drop-in replacement.

## How the patch is applied

`Dockerfile` runs `patches/*.py` against the base image's `gateway/run.py`.
Each patch script is idempotent (checks for a marker comment before mutating).

If upstream Hermes changes the line we depend on, the patch will fail with
"expected pattern not found" and the build will halt — alerting us to update
the patch script.

## Update cadence

When `nousresearch/hermes-agent:latest` ships a new version we want, retag
or rebuild this image. If the patch breaks, edit `patches/*.py` and re-push.

## License

Patches MIT (this repo). Base image inherits Nous Research's MIT license.
