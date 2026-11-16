#!/usr/bin/env python3
"""List the jurisdictions a ZIP code overlaps, with land-area shares.

Uses the Census 2020 ZCTA-to-place and ZCTA-to-county relationship files
(no API key; streams ~10 MB each). ZCTAs approximate USPS ZIP codes.
Any land not inside an incorporated place is unincorporated county
(or township) territory, so its zoning authority is the county/township.

Usage:
    python3 zip_jurisdictions.py 30078
"""
import csv
import io
import sys
import urllib.request

BASE = "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/"
PLACE_FILE = BASE + "tab20_zcta520_place20_natl.txt"
COUNTY_FILE = BASE + "tab20_zcta520_county20_natl.txt"


def rows_for(url: str, zcta: str):
    req = urllib.request.Request(url, headers={"User-Agent": "zoning-lookup-skill"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        reader = csv.DictReader(io.TextIOWrapper(resp, encoding="utf-8-sig"), delimiter="|")
        for row in reader:
            if row.get("GEOID_ZCTA5_20") == zcta:
                yield row


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or len(sys.argv[1]) != 5:
        print(__doc__)
        return 2
    zcta = sys.argv[1]

    counties = list(rows_for(COUNTY_FILE, zcta))
    if not counties:
        print(f"ZIP {zcta}: no matching ZCTA (may be a PO-box-only or unique ZIP). Ask for a street address.")
        return 1
    total = int(counties[0]["AREALAND_ZCTA5_20"]) or 1

    print(f"ZIP {zcta}  (land area {total / 2.59e6:.1f} sq mi)\n\nCounties:")
    for c in counties:
        print(f"  {c['NAMELSAD_COUNTY_20']:40} {100 * int(c['AREALAND_PART']) / total:5.1f}% of ZIP land")

    print("\nIncorporated / designated places:")
    for p in rows_for(PLACE_FILE, zcta):
        part = 100 * int(p["AREALAND_PART"] or 0) / total
        name = p["NAMELSAD_PLACE_20"] or "(outside any place = unincorporated county/township)"
        cls = p["CLASSFP_PLACE_20"]
        kind = "" if not cls else (" [CDP - unincorporated, county zoning]" if cls.startswith("U") else " [incorporated]")
        print(f"  {name + kind:70} {part:5.1f}% of ZIP land")

    print("\nMore than one zoning authority is possible: ask for a street address or parcel ID.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
