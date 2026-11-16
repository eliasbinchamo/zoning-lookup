# Finding the official zoning ordinance

## Search order

1. `"<city> <state> zoning ordinance"` and `"<city> <state> code of ordinances zoning"` — standard web search.
2. Site-restricted searches on the codifiers (use `allowed_domains`):
   - `library.municode.com` — largest; URLs look like `library.municode.com/<st>/<city>/codes/code_of_ordinances?nodeId=...`. Some cities have a separate product such as `/codes/unified_development_code` or `/codes/zoning`.
   - `codelibrary.amlegal.com/codes/<city><st>/latest/...`
   - `ecode360.com/<CODE>` (General Code) — common in the Northeast/Midwest.
   - `codepublishing.com/<ST>/<City>/` — common in the West.
   - `online.encodeplus.com/regs/<city>-<st>/` — enCodePlus, often used for newer UDOs.
   - `zoninghub.com`, Granicus, CivicPlus "Document Center" PDFs.
3. The jurisdiction's own site: Planning / Community Development / Development Services pages usually link the code and zoning map. Many small towns post only a PDF.
4. Check for a recent rewrite: search `"<city>" new zoning ordinance adopted`, `"<city>" UDO effective`, `"<city>" zoning code update`. Rewrite project sites (e.g. `framework.tuscaloosa.com`) often host drafts — **drafts are not law**; confirm adoption and use the codified version.

## Is it current?

- The codifier page usually shows "Current through Ord. ___ / Supplement ___ / date". Record it.
- Each section ends with history notes like `(Ord. No. 9572, § 2, 12-17-24; Ord. No. 9751, § 17, 3-10-26)`. The latest ordinance date is your "amended through" evidence for that section.
- Codifiers lag adoption by weeks to months. If the city's agenda/minutes show a recent zoning text amendment not yet codified, mention it as a caveat.
- If the code says "This ordinance shall become effective on <date>" and that date is in the future, the old code still governs today — report both.

## Third-party mirrors (use for navigation only)

Zoneomics, buildingclub.info, zoning-*.pages.dev, Gridics/LandVision marketing pages, Reonomy, and AI-written "zoning guides" are frequently stale or wrong (wrong district names, old numbers, invented tables). Use them to discover section numbers or district names, then verify every value on the official host. Never cite them as the source of a requirement.

## Zoning maps (address → district)

- Search `"<city>" zoning map GIS`, `"<county>" parcel viewer`, `"<city>" ArcGIS zoning`. Typical hosts: `*.maps.arcgis.com`, `*.hub.arcgis.com`, county assessor/GIS portals, Regrid-style viewers run by the county.
- Many ArcGIS maps expose a public FeatureServer. If you find one (look for `/arcgis/rest/services/.../FeatureServer/<n>` in network requests), query by point:
  `<layer-url>/query?geometry=<lon>,<lat>&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&f=json`
  using the coordinates from `scripts/resolve_jurisdiction.py`.
- The ordinance usually states the official map is the final authority and that online maps may not show recent rezonings. Say so in the caveats.
- If the map can't be queried, tell the user which viewer to check and proceed with the district they name.

## Extracting text from JavaScript code sites

`WebFetch` frequently returns only "Initializing application…" for Municode, eCode360 and American Legal. Use the built-in browser instead:

1. `preview_start` / `navigate` to the section URL (Municode `nodeId=` deep links work).
2. Wait for content, then pull the text with `javascript_tool`. Municode loads the whole article around the requested section, so slice to the section you want:

```js
await new Promise(r => setTimeout(r, 4000));
const t = document.body.innerText;
const s = t.lastIndexOf('Sec. 25-83. - ');          // section heading text; lastIndexOf skips the TOC entry
const e = t.indexOf('Sec. 25-84.', s + 20);         // next section
t.slice(s, e);
```

3. Use-table matrices are wide; pull only the district's column:

```js
const out = [];
for (const tb of document.querySelectorAll('table')) {
  const rows = [...tb.rows].map(r => [...r.cells].map(c => c.innerText.trim().replace(/\s+/g, ' ')));
  const h = rows.findIndex(r => r.includes('GC'));      // district abbreviation
  if (h < 0) continue;
  const gi = rows[h].indexOf('GC'), last = rows[h].length - 1;
  for (const r of rows.slice(h + 1))
    out.push(r.length === rows[h].length ? `${r[0]} => ${r[gi] || '(blank)'} ; std=${r[last]}` : `## ${r.join(' ')}`);
}
out.join('\n');
```

   Check that header and data rows have the same cell count — merged category rows are shorter and are printed as `##` headings. Blank cells usually mean "prohibited"; confirm in the legend.
4. Find the TOC / node IDs for a whole chapter by listing links on the chapter page:
   `[...document.querySelectorAll('a[href*="nodeId="]')].map(a => a.innerText.trim() + ' | ' + a.href)`.
5. **PDFs** (many counties publish only PDFs, e.g. Gwinnett County's UDO titles):
   - Download into a fresh scratch directory. File names often carry the amendment date (`...-amended-aug-2026.pdf`); prefer the link on the government's own UDO page over an old search hit, because old compiled versions get deleted (404) when a new one is posted.
   - If `pdftotext`/`pypdf` are missing, create a venv in the scratchpad and install pypdf: `python3 -m venv <scratch>/venv && PIP_USER=0 <scratch>/venv/bin/pip install --no-user pypdf`. Run scripts with `-I`.
   - `scripts/pdf_to_text.py <pdf> <out.txt>` dumps text with page markers, so you can `grep -n` for section numbers and cite PDF page numbers.
   - **Use tables:** plain text extraction loses column positions (a row of "P P P" doesn't tell you which districts). Use `scripts/pdf_use_table.py <pdf> <first> <last> <district> '<all column labels regex>'`. It uses pypdf layout mode and takes column positions from **each page's own header row**, because offsets shift between pages. Spot-check 3–4 rows by comparing token offsets to the header before trusting it.
   - Dimensional tables usually extract fine as text; still confirm the column order against the header.

## Planning department contact

Grab the planning/zoning office name, phone, and URL from the jurisdiction's site for the caveats section. Don't copy phone numbers from search-result summaries: they were wrong in both test runs (Tuscaloosa, Snellville). A city site often links its codified code from a "Quick Links → Municipal Code" item even when its UDO page lists only amendment drafts.
