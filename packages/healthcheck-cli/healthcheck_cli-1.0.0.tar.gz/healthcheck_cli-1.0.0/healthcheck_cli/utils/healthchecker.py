import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Tuple

import aiohttp

CONFIG_FILE = Path.home() / ".healthcheck" / "config.json"


class HealthChecker:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config_file.parent.mkdir(exist_ok=True)

    def load_config(self):
        if not self.config_file.exists():
            return {"endpoints": {}}

        try:
            with open(self.config_file, "r") as f:
                return json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):
            return {"endpoints": {}}

    def save_config(self, config: Dict):
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    async def check_endpoint_health(
        self, url: str, timeout: int = 10
    ) -> Tuple[str, int, float, str]:
        start_time = time.perf_counter()

        try:
            try:
                timeout_value = float(timeout)
            except (TypeError, ValueError):
                timeout_value = 10.0

            client_timeout = aiohttp.ClientTimeout(total=timeout_value)

            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url=url) as response:
                    response_time = (time.perf_counter() - start_time) * 1000
                    status_text = (
                        "🟢 Healthy" if 200 <= response.status < 400 else "🔴 Unhealthy"
                    )
                    return status_text, response.status, float(response_time), ""

        except asyncio.TimeoutError:
            response_time = (time.perf_counter() - start_time) * 1000
            return "⏰ Timeout", 0, float(response_time), "Request timed out"

        except Exception as e:
            response_time = (time.perf_counter() - start_time) * 1000
            return "❌ Error", 0, float(response_time), str(e)
