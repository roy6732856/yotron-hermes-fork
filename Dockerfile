## YOTRON Hermes — patched Hermes Agent image
##
## Layer-thin overlay on the official nousresearch/hermes-agent image.
## Applies a single small patch to gateway/run.py to inject Lark sender
## open_id into the agent context (enabling per-user OAuth routing via
## yotron-lark-bridge MCP).
##
## To rebuild the patch when upstream changes, edit patches/*.py to match
## the new pattern.

FROM nousresearch/hermes-agent:latest

USER root

COPY patches/ /opt/yotron/patches/

RUN set -eux; \
    for patch in /opt/yotron/patches/*.py; do \
        echo "Applying $patch..."; \
        python3 "$patch"; \
    done; \
    # Bytecode cleanup so patched .py is what's loaded
    find /opt/hermes -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true; \
    # Keep ownership consistent with upstream image conventions
    chmod -R a+rX /opt/hermes /opt/yotron

# Inherit entrypoint, default user, volume from the base.
# Hermes binds the API server to 8642 by default — declare so Zeabur routes here.
EXPOSE 8642

# Set the gateway-run command so the container starts as the messaging gateway
# (Telegram + Lark + API server) rather than dropping into interactive CLI.
CMD ["gateway", "run"]
