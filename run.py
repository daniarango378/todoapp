from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DEFAULT_BACKEND_PORT = 5000
DEFAULT_FRONTEND_PORT = 8000


def is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def find_available_port(start_port: int, max_attempts: int = 20) -> int:
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(
        f"No available port found between {start_port} and {start_port + max_attempts - 1}."
    )


def start_process(
    args: list[str], env: dict[str, str] | None = None
) -> subprocess.Popen:
    return subprocess.Popen(args, cwd=ROOT_DIR, env=env)


def stop_processes(processes: list[subprocess.Popen]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    for process in processes:
        if process.poll() is None:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def main() -> int:
    requested_backend_port = int(
        os.environ.get("BACKEND_PORT", str(DEFAULT_BACKEND_PORT))
    )
    backend_port = find_available_port(requested_backend_port)
    frontend_port = find_available_port(
        int(os.environ.get("FRONTEND_PORT", str(DEFAULT_FRONTEND_PORT)))
    )

    backend_env = os.environ.copy()
    backend_env["BACKEND_PORT"] = str(backend_port)
    backend_env["FLASK_DEBUG"] = backend_env.get("FLASK_DEBUG", "true")
    backend_env["FLASK_USE_RELOADER"] = backend_env.get("FLASK_USE_RELOADER", "false")

    frontend_env = os.environ.copy()
    frontend_env["FRONTEND_PORT"] = str(frontend_port)
    frontend_env["TASK_API_BASE_URL"] = f"http://localhost:{backend_port}"

    processes = [
        start_process([sys.executable, "backend/app/main.py"], env=backend_env),
        start_process([sys.executable, "frontend/serve_frontend.py"], env=frontend_env),
    ]

    def handle_signal(signum, frame):  # noqa: ARG001
        stop_processes(processes)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print(f"Backend available at http://localhost:{backend_port}")
    print(f"Frontend available at http://localhost:{frontend_port}")
    if backend_port != requested_backend_port:
        print(
            f"Port {requested_backend_port} was busy, so the backend was moved to {backend_port}."
        )
    if frontend_port != DEFAULT_FRONTEND_PORT:
        print(
            f"Port {DEFAULT_FRONTEND_PORT} was busy, so the frontend was moved to {frontend_port}."
        )

    try:
        while True:
            for process in processes:
                if process.poll() is not None:
                    stop_processes(processes)
                    return process.returncode or 0
            time.sleep(0.5)
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
