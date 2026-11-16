# Changelog

## 0.1.0 — 2026-11-16

First public release.

- `zoning-lookup` skill: resolves the jurisdiction, finds the official current ordinance, maps the district name, and extracts permitted uses, height, setbacks, parking, and lot coverage into a sourced Markdown report.
- Helper scripts:
  - `resolve_jurisdiction.py`: address → jurisdiction, via the Census geocoder.
  - `zip_jurisdictions.py`: ZIP → overlapping jurisdictions, via Census relationship files.
  - `pdf_to_text.py`: PDF code → text with page markers.
  - `pdf_use_table.py`: column-aware extraction from PDF use tables.
- Worked examples: Tuscaloosa, AL (GC), and ZIP 30078 (Snellville BG vs. Gwinnett County C-2).
- Packaged as a Claude Code plugin with a single-plugin marketplace.
