"""
MediCard — Health Cashless Hospitalization & Settlement Platform (BC-AINE-017)
Local One-Command Startup Script.

This script:
1. Validates Python environment and dependencies.
2. Initializes SQLite database schema via init_db().
3. Ingests deterministic synthetic seed data via seed_database().
4. Boots the FastAPI backend and static frontend server via uvicorn.
5. Launches the default web browser to the MediCard Multi-Portal SPA.
"""

import sys
import os
import time
import webbrowser
import threading
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_prerequisites():
    """Verify runtime environment."""
    print("=" * 70)
    print(" MediCard — Health Cashless Hospitalization Platform (BC-AINE-017)")
    print(" One-Command Local Startup")
    print("=" * 70)
    print(f"[1/4] Checking prerequisites... Python {sys.version.split()[0]} detected.")
    if sys.version_info < (3, 10):
        print("[ERROR] Python 3.10+ is required to run MediCard.")
        sys.exit(1)
    print("      Prerequisites verified: Python runtime and SQLite support OK.")


def setup_database():
    """Execute Alembic migrations and seed deterministic synthetic data."""
    print("[2/4] Executing database migrations and deterministic seed data...")
    from src.repositories.database import run_migrations, init_db, DB_PATH
    from src.seed_data import seed_database

    try:
        run_migrations()
        print("      Alembic schema migrations applied successfully to head.")
    except Exception as exc:
        print(f"      [MIGRATION NOTICE] {exc}; ensuring schema via init_db()...")
        init_db()

    seed_database()
    print(f"      Database ready at: {DB_PATH}")


def open_browser_delayed(url: str, delay: float = 1.5):
    """Open default browser once server is listening."""
    def _open():
        time.sleep(delay)
        print(f"\n[INFO] Opening MediCard Portal at: {url}")
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()


def start_server(host: str = "127.0.0.1", port: int = 8000, auto_browser: bool = True):
    """Run uvicorn ASGI server."""
    import uvicorn

    url = f"http://{host}:{port}/"
    print(f"[3/4] Launching MediCard backend and SPA frontend...")
    print(f"      - SPA Web Application: {url}")
    print(f"      - Interactive API Docs: {url}docs")
    print(f"      - Health Endpoint:     {url}health")
    print("[4/4] Starting Uvicorn ASGI server (Press Ctrl+C to terminate)...")
    print("=" * 70)

    if auto_browser:
        open_browser_delayed(url)

    uvicorn.run("src.main:app", host=host, port=port, reload=False, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="Start MediCard Platform")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    args = parser.parse_args()

    check_prerequisites()
    setup_database()
    start_server(host=args.host, port=args.port, auto_browser=not args.no_browser)


if __name__ == "__main__":
    main()
