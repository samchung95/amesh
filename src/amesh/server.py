from __future__ import annotations

import uvicorn

from amesh.config import get_settings
from amesh.observability import configure_structured_logging


def main() -> None:
    settings = get_settings()
    configure_structured_logging(settings.log_level)
    uvicorn.run(
        "amesh.app:app",
        host=settings.app_host,
        port=settings.app_port,
        log_config=None,
        access_log=True,
    )


if __name__ == "__main__":
    main()
