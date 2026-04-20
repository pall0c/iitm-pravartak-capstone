from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from src.philosophy.config import load_configuration
from src.philosophy.service import PhilosophyService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest philosophy PDFs into Chroma.")
    parser.add_argument("--reset", action="store_true", help="Delete the persisted Chroma store first.")
    args = parser.parse_args()

    service = PhilosophyService(load_configuration())
    report = service.ingest(reset=args.reset)
    print(json.dumps(asdict(report), indent=2))


if __name__ == "__main__":
    main()
