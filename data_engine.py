"""Legacy entrypoint used by GitHub Actions.

The live scanner is sector-first intraday: see intraday_scanner.py.
"""
from intraday_scanner import run_intraday


def run_pipeline():
    run_intraday()


if __name__ == "__main__":
    run_pipeline()