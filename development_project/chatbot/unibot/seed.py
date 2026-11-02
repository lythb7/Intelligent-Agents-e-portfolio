"""Create and populate the local database: ``python -m unibot.seed``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .clock import clock_from_setting
from .config import Settings
from .db import connect, seed, write_credentials_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the UniBot demonstration database.")
    parser.add_argument("--reset", action="store_true", help="delete any existing database first")
    args = parser.parse_args(argv)
    settings = Settings.from_env()
    if args.reset and settings.database_path.exists():
        settings.database_path.unlink()
    credentials_path: Path = settings.data_dir / "demo_credentials.json"
    existing = json.loads(credentials_path.read_text()) if credentials_path.exists() else None
    conn = connect(settings.database_path)
    passwords = seed(conn, settings.documents_dir, clock_from_setting(settings.fake_now), existing)
    write_credentials_file(credentials_path, passwords)
    print(f"Database ready at {settings.database_path}")
    print(f"Demo accounts (synthetic) written to {credentials_path}:")
    for username, password in passwords.items():
        print(f"  username: {username:8s} password: {password}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
