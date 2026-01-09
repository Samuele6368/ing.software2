from __future__ import annotations

import logging
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from ui.app_gui import run_app  # noqa: E402


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    run_app()


if __name__ == "__main__":
    main()
