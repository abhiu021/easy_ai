"""Utility for syncing Tally data with the backend service."""

import argparse
import os
from typing import Iterable

import requests
from dotenv import load_dotenv

from tally_tool import main as tally


load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CLIENT_ID = os.getenv("CLIENT_ID", "demo")
CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")


def backend_post(route: str, data: dict) -> requests.Response:
    """POST helper that adds the authentication header."""
    headers: dict[str, str] = {}
    if CLIENT_TOKEN:
        headers["Authorization"] = f"Bearer {CLIENT_TOKEN}"
    resp = requests.post(f"{BACKEND_URL}{route}", data=data, headers=headers)
    resp.raise_for_status()
    return resp


def sync_data(types: Iterable[str], from_date: str, to_date: str, voucher_no: str | None = None) -> None:
    """Sequentially fetch the requested data and upload to the backend."""

    for dtype in types:
        dtype = dtype.strip().lower()
        if dtype == "ledgers":
            payload = tally.get_ledgers()
        elif dtype == "vouchers":
            payload = tally.get_vouchers("All")
        elif dtype == "specific_voucher" and voucher_no:
            payload = tally.get_specific_voucher(voucher_no)
        elif dtype == "outstanding":
            payload = tally.get_outstanding_receivables(from_date, to_date)
        elif dtype == "daybook":
            payload = tally.get_day_book(from_date, to_date)
        else:
            # Unknown or improperly configured type
            continue

        backend_post(
            "/upload_voucher",
            {
                "client_id": CLIENT_ID,
                "data_type": "xml",
                "payload": payload,
            },
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Tally data with backend")
    parser.add_argument(
        "--types",
        default=os.getenv("SYNC_TYPES", "ledgers"),
        help="Comma separated list of data types to sync",
    )
    parser.add_argument("--from-date", default=os.getenv("SYNC_FROM_DATE", ""))
    parser.add_argument("--to-date", default=os.getenv("SYNC_TO_DATE", ""))
    parser.add_argument("--voucher-no", default=os.getenv("SYNC_VOUCHER_NO"))
    args = parser.parse_args()

    types = [t.strip() for t in args.types.split(",") if t.strip()]
    sync_data(types, args.from_date, args.to_date, args.voucher_no)


if __name__ == "__main__":
    main()

