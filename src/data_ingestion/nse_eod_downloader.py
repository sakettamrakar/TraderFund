"""NSE India end-of-day data downloader."""

from __future__ import annotations

import os
import datetime as _dt
import requests
import zipfile


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.nseindia.com/",
}


def _download_file(url: str, dest_path: str) -> bool:
    """Download a file from ``url`` to ``dest_path``.

    Returns ``True`` on success, ``False`` otherwise.
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"Failed to download {url}: HTTP {resp.status_code}")
            return False
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        print(f"Downloaded {url} -> {dest_path}")
        return True
    except requests.RequestException as exc:  # pragma: no cover - network
        print(f"Error downloading {url}: {exc}")
        return False


def _extract_zip(zip_path: str, dest_dir: str) -> None:
    """Extract ``zip_path`` to ``dest_dir``."""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest_dir)
        print(f"Extracted {zip_path}")
    except zipfile.BadZipFile as exc:  # pragma: no cover - corrupt zip
        print(f"Failed to extract {zip_path}: {exc}")


def download_nse_eod(date: _dt.date | None = None, root: str = "nse_eod_files") -> None:
    """Download NSE EOD data for ``date`` (defaults to today)."""
    date = date or _dt.date.today()
    folder = os.path.join(root, date.strftime("%Y-%m-%d"))
    os.makedirs(folder, exist_ok=True)

    ddmmyy = date.strftime("%d%m%y")
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    equity_url = (
        f"https://www1.nseindia.com/content/historical/EQUITIES/"
        f"{year}/{month}/{day}/cm{ddmmyy}bhav.csv.zip"
    )
    fo_url = (
        f"https://www1.nseindia.com/content/historical/DERIVATIVES/"
        f"{year}/{month}/{day}/fo{ddmmyy}bhav.csv.zip"
    )
    mto_url = f"https://www1.nseindia.com/archives/equities/mto/MTO_{ddmmyy}.DAT"

    equity_zip = os.path.join(folder, os.path.basename(equity_url))
    fo_zip = os.path.join(folder, os.path.basename(fo_url))
    mto_file = os.path.join(folder, os.path.basename(mto_url))

    if _download_file(equity_url, equity_zip):
        _extract_zip(equity_zip, folder)

    if _download_file(fo_url, fo_zip):
        _extract_zip(fo_zip, folder)

    _download_file(mto_url, mto_file)


if __name__ == "__main__":  # pragma: no cover - manual run
    download_nse_eod()

