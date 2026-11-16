# zoning-lookup

A [Claude Code](https://claude.com/claude-code) plugin that researches **U.S. commercial zoning** for a site. It finds the jurisdiction's **official, current** zoning ordinance, identifies the right district, and writes a sourced summary of the requirements that matter for commercial development:

- **Permitted uses**: by right, conditional/special use, and prohibited
- **Building height**
- **Setbacks** and residential buffers
- **Parking**: minimums, maximums, and reductions
- **Lot coverage**: FAR and open space

Every number in the report links back to the section of the official code it came from, along with the "amended through" date that was checked.

> **Not legal advice.** The output is a research summary to speed up due diligence. Confirm with the jurisdiction's planning department before you buy, design, or file anything.

## What you can ask

Start with anything that identifies a place:

| Input | Example prompt |
|---|---|
| District + city | `I have a site with General Commercial zoning in Tuscaloosa, AL.` |
| Street address | `What are the zoning requirements for 2201 University Blvd, Tuscaloosa, AL 35401?` |
| ZIP code | `/zoning-lookup 30078` |
| Parcel ID | `Zoning summary for Gwinnett County parcel <parcel ID>` |
| Municipality | `What commercial zoning districts does Snellville, GA have?` |

The skill loads automatically when you ask about zoning, setbacks, permitted uses, parking requirements, and similar topics. You can also call it directly with `/zoning-lookup <anything>`.

## Example output

These reports came from real runs, each checked against the official code:

- [Tuscaloosa, AL: General Commercial (GC)](skills/zoning-lookup/examples/tuscaloosa-al-general-commercial.md). The input was a single district. The code is hosted on Municode, and the run caught a third-party mirror showing a superseded setback.
- [ZIP 30078: Snellville BG vs. unincorporated Gwinnett County C-2, GA](skills/zoning-lookup/examples/30078-snellville-bg-vs-gwinnett-c2.md). The ZIP is split between a city and the unincorporated county. One code is on Municode and the other is published only as a PDF, and the report compares the two side by side.

Excerpt from the Tuscaloosa report:

| Requirement | Standard | Source |
|---|---|---|
| Max building height | 60 ft (reduced near single-family lots) | § 25-83, Table IV-47 |
| Front setback (min) | 20 ft, or the average alignment of existing buildings within 200 ft…, whichever is less | § 25-83, Table IV-47 |
| Parking (min) | Set by use: retail 3/1,000 sf, office 3/1,000 sf, restaurant 3.5/1,000 sf; no maximum | § 25-123 |
| Lot coverage | No maximum; minimum 5% open space | § 25-83; § 25-140 |

## Installation

### Option 1: Install as a plugin (recommended)

In Claude Code:

```
/plugin marketplace add eliasbinchamo/zoning-lookup
/plugin install zoning-lookup@zoning-lookup
```

Or from a terminal:

```bash
claude plugin marketplace add eliasbinchamo/zoning-lookup
```

```bash
claude plugin install zoning-lookup@zoning-lookup
```

Restart Claude Code (or start a new session) to load the skill. To update later:

```bash
claude plugin update zoning-lookup@zoning-lookup
```

### Option 2: Copy the skill folder

If you'd rather not use the plugin system, clone the repo and copy (or symlink) the skill into your personal skills folder:

```bash
git clone https://github.com/eliasbinchamo/zoning-lookup.git
```

```bash
mkdir -p ~/.claude/skills && cp -R zoning-lookup/skills/zoning-lookup ~/.claude/skills/
```

To make it available in a single project only, copy it into that project's `.claude/skills/` folder instead.

### Requirements

- **Claude Code** with web access. The skill uses web search and fetch, and the built-in browser when it's available.
- **Python 3.9+** for the helper scripts. The jurisdiction scripts use only the standard library.
- **[`pypdf`](https://pypi.org/project/pypdf/)**, needed only for jurisdictions that publish their code as PDF. Install it with `pip install -r requirements.txt`. If it's missing, the skill tells Claude to install it into a throwaway virtualenv.
- **No API keys.** The jurisdiction lookups use free U.S. Census Bureau services.

## How it works

The skill ([`SKILL.md`](skills/zoning-lookup/SKILL.md)) walks Claude through six steps:

1. **Resolve the jurisdiction.** Zoning is set by whichever city, county, or township has authority over the parcel.
   - For an address, `resolve_jurisdiction.py` geocodes it with the Census geocoder and returns the incorporated place and county.
   - For a ZIP code, `zip_jurisdictions.py` lists every city and county the ZIP overlaps, with each one's share of the land. ZIPs often cross city limits, so the skill asks for an address instead of guessing.
2. **Find the official, current ordinance** on the codifier: Municode, American Legal, eCode360, Code Publishing, enCodePlus, or the government's own PDF. It checks adoption and amendment dates. Third-party mirrors are used only to locate sections, never as a source.
3. **Map the district name.** "General Commercial" may be `GC`, `C-2`, `BG`, `B-2`, and so on, so the skill matches on the code's own purpose statements.
4. **Extract the requirements** from the district standards, use tables, parking chapter, open space and landscaping rules, and residential-adjacency rules.
5. **Verify.** Every value is re-read against the official text and recorded with its section and amendment history.
6. **Write the report** from the [template](skills/zoning-lookup/templates/report-template.md) and save it to `zoning-reports/` in your working directory.

### Helper scripts

| Script | Purpose | Dependencies |
|---|---|---|
| [`resolve_jurisdiction.py`](skills/zoning-lookup/scripts/resolve_jurisdiction.py) `"<address>"` | Address → coordinates, incorporated place, county, likely zoning authority | stdlib |
| [`zip_jurisdictions.py`](skills/zoning-lookup/scripts/zip_jurisdictions.py) `<zip>` | ZIP → counties and places it overlaps, with land-area shares | stdlib |
| [`pdf_to_text.py`](skills/zoning-lookup/scripts/pdf_to_text.py) `<pdf> <out.txt>` | PDF code → searchable text with page markers | pypdf |
| [`pdf_use_table.py`](skills/zoning-lookup/scripts/pdf_use_table.py) `<pdf> <first> <last> <district> [cols]` | Pull one district's column from a PDF use table, keeping column alignment | pypdf |

You can run them yourself:

```bash
python3 skills/zoning-lookup/scripts/resolve_jurisdiction.py "2201 University Blvd, Tuscaloosa, AL 35401"
```

```bash
python3 skills/zoning-lookup/scripts/zip_jurisdictions.py 30078
```

### Reference material

- [`references/source-finding.md`](skills/zoning-lookup/references/source-finding.md) covers where codes are hosted, how to confirm a code is current, how to pull text from JavaScript-heavy code sites and PDFs, and where to find zoning maps.
- [`references/extraction-checklist.md`](skills/zoning-lookup/references/extraction-checklist.md) covers where each requirement usually hides and the common traps, such as footnotes, contextual setbacks, use-specific standards, and overlays.
- [`references/district-crosswalk.md`](skills/zoning-lookup/references/district-crosswalk.md) maps plain-English district names to common code labels.

## Limitations

- **U.S. only.** It relies on U.S. Census geography and U.S. code publishers.
- **A summary, not a compliance determination.** Overlays, PUD/PD terms, conditional zoning, variances, covenants, building/fire codes, and stormwater rules are flagged but not fully analyzed.
- **Online zoning maps** can lag recent rezonings, and codifiers can lag adopted amendments. The report states the "as of" date it verified.
- **Some jurisdictions** publish only scanned PDFs or nothing online. The skill then says what it couldn't find instead of guessing.

## Roadmap

- **Feasibility checks:** given a proposed use and site numbers (lot size, building area, height, parking count), determine whether the project complies and what approvals it needs.
- More worked examples across code publishers and states.

## Contributing

Issues and pull requests are welcome, especially new worked examples, publisher-specific extraction tips, and fixes where the skill got a jurisdiction wrong. If you report a wrong result, include the jurisdiction, the district, and a link to the official section.

Before opening a PR, run:

```bash
claude plugin validate . --strict
```

```bash
python3 -m py_compile skills/zoning-lookup/scripts/*.py
```

## License

[MIT](LICENSE)
