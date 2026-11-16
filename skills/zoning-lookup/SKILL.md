---
name: zoning-lookup
description: Research and summarize the zoning regulations that apply to a commercial site in any U.S. jurisdiction. Use when the user gives a zoning district plus a place ("General Commercial in Tuscaloosa, AL"), a street address, a ZIP code, a parcel ID, or a municipality/county and wants to know what the zoning allows — permitted uses, building height, setbacks, parking, lot coverage, or other development standards — with links to the official ordinance. Triggers on "zoning", "zoned", "setbacks", "permitted uses", "what can I build", "parking requirements", "lot coverage", "zoning district", "zoning ordinance", "UDO", "land development code".
---

# Zoning Lookup

Find the **official, current** zoning ordinance for a site, pull the regulations for its zoning district, and deliver a sourced summary of the key development standards.

The output is a research summary, not a legal opinion. Every number must trace to a cited section of the official code.

**Paths:** `scripts/`, `references/`, `templates/` and `examples/` are relative to this skill's own directory (the base directory shown when the skill loads), not the user's working directory. The scripts need Python 3.10+. The two PDF scripts also need `pypdf`; if it's missing, install it into a virtualenv in your scratch space (see `references/source-finding.md`).

## Inputs the user may give

Any one of these is enough to start; combine them when given:

| Input | What it gives you | What it does NOT give you |
|---|---|---|
| District + city/county ("General Commercial, Tuscaloosa AL") | Jurisdiction + district | Overlays, site-specific conditions |
| Street address | Jurisdiction (via geocoding) + zoning (via GIS map) | — |
| ZIP code only | Candidate jurisdictions | A single jurisdiction — ZIPs cross city/county lines |
| Parcel ID / APN | Exact parcel → zoning via county/city GIS | — |
| Municipality only | Jurisdiction | Which district applies → ask, or summarize the commercial districts |

## Workflow

Follow these steps in order. Keep a running source list (URL + section number + "as amended through" date) as you go.

### 1. Resolve the jurisdiction (who regulates the land)

Zoning is set by whoever has land-use authority over the parcel — usually the incorporated city/town/village, otherwise the county (or township, in some states). Getting this wrong invalidates everything after it.

- **Address given:** run `scripts/resolve_jurisdiction.py "<address>"` (U.S. Census geocoder, no API key). It returns the incorporated place (if any) and county. No incorporated place → the county (or township) is the zoning authority. Then look up the parcel's district on the jurisdiction's zoning map / parcel GIS (see `references/source-finding.md` § Zoning maps).
- **ZIP only:** a ZIP is a postal route, not a jurisdiction. Run `scripts/zip_jurisdictions.py <zip>` (Census relationship files, ~30 s) to list the counties and incorporated places it overlaps with land-area shares, then ask the user for an address, parcel ID, or which jurisdiction + district. Don't guess. If the ZIP falls entirely in one incorporated place, proceed with that jurisdiction but still ask for the district.
- **City name only:** confirm the site is inside city limits if the user isn't sure. Name collisions are common (Tuscaloosa city vs. Tuscaloosa County vs. neighboring Northport all have separate codes).
- Watch for: extraterritorial jurisdiction (ETJ) areas, consolidated city-counties, unzoned counties (common in rural AL, TX, and others — say so plainly if there's no zoning).

### 2. Find the official, current ordinance

Read `references/source-finding.md` for the full playbook. Short version:

1. Search for the jurisdiction's code on the official codification hosts: **Municode** (library.municode.com), **American Legal** (codelibrary.amlegal.com), **eCode360** (ecode360.com), **Code Publishing** (codepublishing.com), **enCodePlus**, **Granicus/ZoningHub**, or a PDF on the government's own `.gov`/`.com` site.
2. Confirm it's the **current** ordinance: look for the adoption/effective date and the most recent amending ordinance shown in the section history notes. Search for "zoning ordinance rewrite", "new UDO adopted", or "effective" + year — many cities replaced their codes recently.
3. **Never rely on third-party mirrors** (Zoneomics, buildingclub, Gridics marketing pages, AI-generated "zoning guides") for numbers. Use them only to find section numbers, then verify on the official host. Mirrors lag amendments — in the Tuscaloosa test case, the mirror showed a superseded front setback that had been amended months earlier.
4. Municode/eCode360/American Legal are JavaScript apps — `WebFetch` often returns an empty shell. Use the built-in browser (load its skill first if one is listed) and extract text with JavaScript (snippets in `references/source-finding.md` § Extracting text). Municode returns the whole article around a section, so one page load usually covers the district table, or the full use table set, or the full parking division.
5. Contact details and map links: take them from the jurisdiction's own page, not search-result snippets (snippets gave a wrong phone number in testing).

### 3. Map the user's district name to the code's district

Users say "General Commercial"; codes say `GC`, `C-2`, `B-2`, `CG`, `C-G`, `CB`, `BG`, etc. Find the code's district list (usually "Zoning Districts Established") and match on the **district name and purpose statement**, not just the abbreviation. If two districts plausibly match, report both and say which one fits better and why. See `references/district-crosswalk.md`.

### 4. Extract the key requirements

For each item, record the value, the governing section, and any footnotes/conditions. Read `references/extraction-checklist.md` for where each item usually hides and the traps (footnotes, use-specific standards, overlays, adjacency triggers).

Efficient order: district section (dimensional table + cross-reference table) → use-table legend → every principal/accessory/temporary use table filtered to the district column → parking minimum table + maximums + alternatives → open space / landscaping → neighborhood-compatibility or transition rules (these often override height and setbacks next to residential).

Required items:

1. **Permitted uses** — from the use table/matrix. Separate: by-right (P), conditional/special-use (C/S/SUP/CUP), accessory, temporary, and notably prohibited commercial uses. Include the legend definitions. Flag uses with use-specific standards.
2. **Building height** — max feet and/or stories; note how height is measured and any step-back near residential.
3. **Setbacks** — front, side, rear, corner/street-side; increases when abutting residential; build-to lines; buffer yards that act as setbacks.
4. **Parking** — minimum ratios for the common commercial uses (retail, office, restaurant, medical, hotel), any maximums, reductions/shared parking/parking studies, EV/ADA/bicycle/stacking requirements.
5. **Lot coverage** — maximum building coverage, impervious coverage, FAR, or minimum open space/landscaped area. If the district has **no** coverage limit, say so explicitly and report the controls that act in its place (open space %, landscaping %, FAR, buffers).

Also capture when present (one line each): minimum lot area/width, FAR/density, design/material standards, landscaping and buffers, signage section, overlays, and recent amendments.

### 5. Verify before reporting

- Re-read every number against the official text. Copy values exactly, including units and "whichever is less/greater" logic.
- Record the **amendment history note** on each section you cite (e.g. "Ord. 9572, 12-17-24; Ord. 9751, 3-10-26") — that is the "current as of" evidence.
- If the official code and a mirror disagree, the official code wins; mention the discrepancy only if the user might have seen the mirror.
- If the code was rewritten recently, warn that older listings/surveys may carry obsolete district names.
- Link only to URLs you actually loaded (deep section links you saw in the TOC or address bar). Don't construct node IDs by guessing; cite the section number in plain text instead.
- If something can't be found or is ambiguous, say so — never fill gaps with "typical" values.

### 6. Write the summary

Use `templates/report-template.md`. Lead with a one-paragraph answer, then the key-requirements table, then detail sections, then sources and caveats. Link every section to its official URL (deep links to the section, not just the code homepage).

Save the report as a Markdown file in the user's working directory (e.g. `zoning-reports/<city>-<district>.md`) unless they ask otherwise, and give them the short version in chat.

**More than one jurisdiction** (e.g. a ZIP split between a city and the unincorporated county, and the user says "summarize both"): research each jurisdiction's general-commercial district fully and write **one comparison report**. Lead with a side-by-side key-requirements table, then one section per jurisdiction, then a short list of each jurisdiction's other commercial districts. Point out where the two codes diverge in ways that change what can be built, such as height, buffers, parking maximums and prohibited uses. Note cross-boundary rules too; Snellville, for example, requires buffers next to residential land in the county.

Worked examples:
- `examples/tuscaloosa-al-general-commercial.md`: single district, Municode HTML code.
- `examples/30078-snellville-bg-vs-gwinnett-c2.md`: ZIP split across two jurisdictions, one on Municode and one PDF-only, with min/max parking.

## Standing caveats (always include, briefly)

- Research summary, not legal advice; confirm with the jurisdiction's planning department before purchase or design decisions. Include their phone/URL when found.
- Zoning maps and codes change; note the "as amended through" date you verified.
- Site-specific conditions not covered: overlays, conditional zoning/proffers, PUD terms, variances, recorded covenants/deed restrictions, nonconforming status, building/fire code, stormwater, and state/federal rules.

## Out of scope for now (future expansion)

The skill currently retrieves and summarizes. A later version can add **feasibility checks** — given a proposed use and site plan numbers (lot size, building SF, height, parking count), determine whether the project complies and what approvals it needs. Keep the extracted data structured (the table in the template) so that step can reuse it.
