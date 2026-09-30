"""Entry point for the chitchat server.

Usage:
    uv run chitchat --serve    # Start FastAPI + MCP server
"""

from __future__ import annotations

import argparse
import logging

from .config import config


def main() -> None:
    parser = argparse.ArgumentParser(description="Chitchat server")
    parser.add_argument("--serve", action="store_true", help="Start HTTP server")
    parser.add_argument("--port", type=int, default=config.backend_port, help="Backend port")
    args = parser.parse_args()

    if args.serve:
        logging.basicConfig(
            level=getattr(logging, config.log_level.upper(), logging.INFO),
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        )
        import uvicorn

        uvicorn.run(
            "chitchat.app:app",
            host=config.host,
            port=args.port,
            log_level=config.log_level,
        )


if __name__ == "__main__":
    main()
