import asyncio
import json
import sys
from typing import Any

from .client import TradingClient


async def _main_async(argv: list[str]) -> int:
    base_url = argv[1] if len(argv) > 1 else "http://127.0.0.1"
    client = TradingClient(base_url=base_url)
    async with client:
        health = await client.health_check()
        print(json.dumps(health))
    return 0


def main() -> None:
    try:
        raise SystemExit(asyncio.run(_main_async(sys.argv)))
    except KeyboardInterrupt:
        raise SystemExit(130)


