"""Application entry point for the Flask backend service."""

from __future__ import annotations

import os
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app  # pylint: disable=wrong-import-position

app = create_app()


def main() -> None:
    """Run the Flask application using environment-based configuration."""
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "true").lower() == "true",
        port=int(os.environ.get("BACKEND_PORT", "5000")),
        use_reloader=os.environ.get("FLASK_USE_RELOADER", "true").lower() == "true",
    )


if __name__ == "__main__":
    main()
