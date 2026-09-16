from __future__ import annotations

import os
import signal
import subprocess  # nosec B404 - commands are static and shell execution is disabled
import sys
import time
from pathlib import Path


def _terminate(processes: list[subprocess.Popen[object]]) -> None:
    """
    Termina todos los procesos hijos de forma controlada.
    """

    for process in processes:
        if process.poll() is None:
            process.terminate()

    deadline = time.monotonic() + 15

    for process in processes:
        if process.poll() is not None:
            continue

        remaining = max(0.1, deadline - time.monotonic())

        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> None:
    """
    Ejecuta los procesos necesarios para el deployment gratuito
    de MedLab Platform en Render.

    Procesos:

    - Celery Worker
    - Celery Beat
    - FastAPI/Uvicorn
    """

    port = os.getenv("PORT", "8000")

    reports_dir = os.getenv(
        "REPORTS_DIR",
        "/app/reports",
    )

    Path(reports_dir).mkdir(
        parents=True,
        exist_ok=True,
    )

    commands = [
        [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "app.workers.celery_app.celery_app",
            "worker",
            "--loglevel=INFO",
            "--concurrency=1",
        ],
        [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "app.workers.celery_app.celery_app",
            "beat",
            "--loglevel=INFO",
        ],
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            os.getenv("HOST", "0.0.0.0"),  # nosec B104 - required for Render container networking
            "--port",
            port,
        ],
    ]

    processes: list[subprocess.Popen[object]] = []

    def handle_signal(
        signum: int,
        _frame: object,
    ) -> None:
        _terminate(processes)
        raise SystemExit(128 + signum)

    signal.signal(
        signal.SIGTERM,
        handle_signal,
    )

    signal.signal(
        signal.SIGINT,
        handle_signal,
    )

    try:
        for command in commands:
            processes.append(
                subprocess.Popen(command)  # nosec B603 - static command lists, shell=False
            )

        while True:
            for process in processes:
                return_code = process.poll()

                if return_code is not None:
                    raise RuntimeError(
                        "Managed process exited unexpectedly: "
                        f"pid={process.pid} "
                        f"code={return_code}"
                    )

            time.sleep(1)

    except KeyboardInterrupt:
        pass

    finally:
        _terminate(processes)


if __name__ == "__main__":
    main()
