from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChitchatConfig:
    backend_port: int = int(os.getenv("CHITCHAT_PORT", "10974"))
    frontend_port: int = int(os.getenv("CHITCHAT_FRONTEND_PORT", "10975"))
    host: str = os.getenv("CHITCHAT_HOST", "127.0.0.1")
    archive_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "CHITCHAT_ARCHIVE_DIR",
                str(Path(__file__).resolve().parent.parent.parent / "archive"),
            )
        )
    )
    docsops_base: str = os.getenv("CHITCHAT_DOCSOPS_BASE", "http://127.0.0.1:10795")
    log_level: str = os.getenv("CHITCHAT_LOG_LEVEL", "info")

    def __post_init__(self) -> None:
        self.archive_dir.mkdir(parents=True, exist_ok=True)


config = ChitchatConfig()
