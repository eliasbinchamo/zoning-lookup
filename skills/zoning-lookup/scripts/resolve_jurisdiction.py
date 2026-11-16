#!/usr/bin/env python3
"""Resolve a U.S. street address to its zoning-relevant jurisdictions.

Uses the free U.S. Census Bureau geocoder (no API key). Prints the matched
address, coordinates (lon/lat, for querying GIS zoning layers), incorporated
place (city/town/village) if any, county, and county subdivision (township /
CCD). If there is no incorporated place, the county or township is usually the
zoning authority.

Usage:
    python3 resolve_jurisdiction.py "2201 University Blvd, Tuscaloosa, AL 35401"
    python3 resolve_jurisdiction.py --json "<address>"
"""
import json
import sys
import urllib.parse
import urllib.request

ENDPOINT = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
LAYERS = "Incorporated Places,Census Designated Places,Counties,County Subdivisions,States"


def resolve(address: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": LAYERS,
        "format": "json",
    })
    req = urllib.request.Request(f"{ENDPOINT}?{params}", headers={"User-Agent": "zoning-lookup-skill"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.load(resp)

    results = []
    for m in data.get("result", {}).get("addressMatches", []):
        geos = m.get("geographies", {})
        first = lambda key: (geos.get(key) or [{}])[0]
        place = first("Incorporated Places")
        cdp = first("Census Designated Places")
        results.append({
            "matched_address": m.get("matchedAddress"),
            "lon": m["coordinates"]["x"],
            "lat": m["coordinates"]["y"],
            "incorporated_place": place.get("NAME"),
            "census_designated_place": cdp.get("NAME"),
            "county": first("Counties").get("NAME"),
            "county_subdivision": first("County Subdivisions").get("NAME"),
            "state": first("States").get("NAME"),
            "likely_zoning_authority": place.get("NAME")
            or f"{first('Counties').get('NAME')} (unincorporated; check county/township zoning)",
        })
    return results


def main() -> int:
    args = sys.argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if not args:
        print(__doc__)
        return 2
    try:
        results = resolve(" ".join(args))
    except Exception as exc:  # network or parse failure
        print(f"Geocoder request failed: {exc}", file=sys.stderr)
        return 1
    if not results:
        print("No match. Try a fuller address (street, city, state, ZIP), or look the parcel up on the county GIS.")
        return 1
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            for k, v in r.items():
                if v:
                    print(f"{k:26} {v}")
            print()
        if len(results) > 1:
            print("Multiple matches - confirm which one with the user.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
