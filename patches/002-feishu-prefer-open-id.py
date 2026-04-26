"""
Patch: Make Feishu adapter prefer open_id over tenant-scoped user_id.

By default Hermes' `_resolve_sender_profile` does:

    primary_id = user_id or open_id

This means when the app has the `contact:user.id` scope, the SessionSource
ends up with `user_id` set to the tenant-scoped ID. But the OAuth flow in
yotron-lark-bridge keys tokens by `open_id` — so the agent ends up looking
up tokens with the wrong key.

This patch flips the preference so `primary_id = open_id or user_id`,
making `source.user_id` always be the open_id. Combined with patch 001,
this gives the agent the open_id it needs to look up the correct token.
"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("/opt/hermes/gateway/platforms/feishu.py")
MARKER = "# YOTRON-PATCH:prefer-open-id"

OLD = "        primary_id = user_id or open_id"

NEW = "        primary_id = open_id or user_id  # YOTRON-PATCH:prefer-open-id"


def main() -> int:
    if not TARGET.exists():
        print(f"[patch] ERROR: {TARGET} not found", file=sys.stderr)
        return 1

    src = TARGET.read_text(encoding="utf-8")

    if MARKER in src:
        print("[patch] 002 already applied — skipping")
        return 0

    if OLD not in src:
        print(f"[patch] ERROR: expected pattern not found in {TARGET}", file=sys.stderr)
        return 2

    patched = src.replace(OLD, NEW, 1)
    TARGET.write_text(patched, encoding="utf-8")
    print(f"[patch] OK — applied prefer-open-id patch to {TARGET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
