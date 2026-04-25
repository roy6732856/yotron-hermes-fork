"""
Patch script: Inject Lark/Feishu sender open_id into the agent's context.

Modifies /opt/hermes/gateway/run.py so every Lark inbound message is prefixed
with `[Lark sender: <name> (open_id=<ou_...>)]` regardless of session-isolation
mode. This lets the agent extract the open_id and pass it to lark_* MCP tools
for true per-user OAuth routing.

Idempotent — safe to run multiple times. Verifies the patched marker before
re-applying.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("/opt/hermes/gateway/run.py")
MARKER = "# YOTRON-PATCH:feishu-sender-open-id"

OLD = """        if _is_shared_multi_user and source.user_name:
            message_text = f"[{source.user_name}] {message_text}"
"""

NEW = """        # YOTRON-PATCH:feishu-sender-open-id
        if (
            source.platform is not None
            and getattr(source.platform, "value", "") == "feishu"
            and source.user_name
            and source.user_id
        ):
            message_text = (
                f"[Lark sender: {source.user_name} (open_id={source.user_id})] "
                f"{message_text}"
            )
        elif _is_shared_multi_user and source.user_name:
            message_text = f"[{source.user_name}] {message_text}"
"""


def main() -> int:
    if not TARGET.exists():
        print(f"[patch] ERROR: {TARGET} not found", file=sys.stderr)
        return 1

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("[patch] Already applied (marker present) — skipping")
        return 0

    if OLD not in src:
        print(f"[patch] ERROR: expected pattern not found in {TARGET}", file=sys.stderr)
        print("[patch] Hermes upstream may have changed — patch needs update", file=sys.stderr)
        return 2

    patched = src.replace(OLD, NEW, 1)
    TARGET.write_text(patched, encoding="utf-8")
    print(f"[patch] OK — applied feishu-sender-open-id patch to {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
