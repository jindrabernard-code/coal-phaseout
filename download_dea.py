"""
download_dea.py — Danish Energy Agency Technology Catalogue Excel data sheets
=============================================================================
Downloads the current DEA data sheets. The ens.dk media IDs change with each
catalogue release; the IDs below were resolved from the DEA pages in July 2026:

  - "Data sheet for Electricity and district heat production - Updated June 2026"
      from https://ens.dk/en/analyses-and-statistics/technology-data-generation-electricity-and-district-heating
  - "Datasheet for energy storage"
      from https://ens.dk/en/analyses-and-statistics/technology-data-energy-storage
  - "Samfundsokonomiske beregningsforudsaetninger ... Regneark med relevante tabeller"
      from https://ens.dk/analyser-og-statistik/samfundsoekonomiske-analysemetoder

Usage:  python download_dea.py
Output: data/danish_energy_agency/*.xlsx
"""

import sys
from pathlib import Path

import requests

OUT_DIR = Path(__file__).parent / "data" / "danish_energy_agency"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

FILES = [
    ("https://ens.dk/media/8615/download",
     "technology_data_electricity_generation.xlsx",
     "Electricity & district heating data sheet (June 2026)"),
    ("https://ens.dk/media/6589/download",
     "technology_data_energy_storage.xlsx",
     "Energy storage data sheet"),
    ("https://ens.dk/media/7844/download",
     "dea_socioeconomic_assumptions.xlsx",
     "Socio-economic assumptions spreadsheet (prices, CO2, discount rate)"),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = 0

    for url, out_name, label in FILES:
        print(f"{label}\n  {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=300)
            resp.raise_for_status()
            ctype = resp.headers.get("Content-Type", "")
            if "html" in ctype.lower():
                raise RuntimeError(f"Got HTML instead of a file "
                                   f"(Content-Type: {ctype}) — media ID may "
                                   f"have changed; re-resolve on the DEA page.")
            out_path = OUT_DIR / out_name
            out_path.write_bytes(resp.content)
            print(f"  Saved {len(resp.content)/1e6:.1f} MB -> {out_path.name}")
        except Exception as exc:
            print(f"  FAILED: {exc}")
            failures += 1

    return failures


if __name__ == "__main__":
    sys.exit(main())
