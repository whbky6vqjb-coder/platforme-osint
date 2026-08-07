import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from osint_core.engine import InvestigationEngine
from osint_core.engine.webui import HermesWebUIBridge, WebUIConfig


async def main():
    print("=== Platforme OSINT ===")
    print("Initializing...")

    config_path = os.path.join(os.path.dirname(__file__), "config", "platform.yaml")
    config = {}
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        except ImportError:
            pass

    engine = InvestigationEngine(config)

    web_config = WebUIConfig(
        host=config.get("hermes_webui", {}).get("host", "0.0.0.0"),
        port=config.get("hermes_webui", {}).get("port", 5000),
        debug=config.get("hermes_webui", {}).get("debug", False),
    )
    webui = HermesWebUIBridge(web_config)

    print(f"Web UI: http://{web_config.host}:{web_config.port}")
    print("Starting investigation engine...")

    await webui.start()


if __name__ == "__main__":
    asyncio.run(main())