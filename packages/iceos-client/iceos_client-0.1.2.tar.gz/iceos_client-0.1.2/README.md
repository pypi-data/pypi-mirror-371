# iceos-client

Typed async Python client for the iceOS Orchestrator API.

## Install

```bash
pip install iceos-client
```

## Quickstart

```python
import asyncio
from ice_client import IceClient

async def main():
    client = IceClient("http://localhost:8000")
    # Quick discovery call (names only) to verify connectivity
    meta = await client.list_components()
    print("components (names only):", list(meta.keys()))
    exec_id = await client.run_bundle(
        "chatkit.rag_chat",
        inputs={
            "query": "Two-sentence summary for Stefano.",
            "org_id": "demo_org",
            "user_id": "demo_user",
            "session_id": "chat_demo"
        },
        # If bundle is not pre-registered on the server, auto-register from YAML:
        blueprint_yaml_path="Plugins/bundles/chatkit/workflows/rag_chat.yaml",
        wait_seconds=5,
    )
    print("execution_id:", exec_id)

asyncio.run(main())
```

## Smoke test (Dockerized)
```bash
docker run --rm -t --network host python:3.11.9-slim bash -lc "\
  python -m pip install -U pip && \
  pip install -q iceos-client && \
  python - <<'PY'\
import asyncio
from ice_client import IceClient
async def main():
    c = IceClient('http://localhost:8000')
    res = await c.list_library(limit=5)
    print('OK:', isinstance(res, dict), 'items:', len(res.get('items', [])))
    await c.close()
asyncio.run(main())
PY"
```
