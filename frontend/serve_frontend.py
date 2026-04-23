from __future__ import annotations

import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from build_frontend import DIST_DIR, build_frontend

PORT = int(os.environ.get("FRONTEND_PORT", "8000"))
API_BASE_URL = os.environ.get("TASK_API_BASE_URL", "http://localhost:5000")


def write_runtime_config() -> None:
    config_file = DIST_DIR / "js" / "runtime-config.js"
    config_file.write_text(
        f'window.TASK_API_BASE_URL = "{API_BASE_URL}";\n',
        encoding="utf-8",
    )


def serve_frontend() -> None:
    build_frontend()
    write_runtime_config()
    os.chdir(DIST_DIR)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    print(f"Frontend available at http://localhost:{PORT}")
    print(f"Frontend configured to use API at {API_BASE_URL}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping frontend server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        serve_frontend()
    except Exception as error:
        print(f"Failed to serve frontend: {error}", file=sys.stderr)
        raise
