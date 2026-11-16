#!/usr/bin/env python3
"""Pull one district's column out of a use table in a PDF zoning code (needs pypdf).

Usage:
    python3 pdf_use_table.py <pdf> <first_page> <last_page> <district> ['<regex of ALL column labels>']
Example (Gwinnett County UDO Title 2):
    python3 pdf_use_table.py title2.pdf 22 30 C-2 'O-I|C-1|C-2|C-3|M-1|M-2'

Uses pypdf layout mode so column positions survive, then assigns each P / S / C / L / A / S/C
token to the nearest header column. Column centers come from the header row on the SAME page
(header offsets shift from page to page; reusing one page's header put values in the wrong
column during testing). A blank cell prints as '--'. Lines with no tokens print as '## ...'
(category headings or wrapped text). Spot-check a few rows against the PDF before relying on it.
"""
import re
import sys

TOKEN_RE = re.compile(r"(?<!\S)(S/C|P|S|C|L|A)(?!\S)")
DEFAULT_COLUMNS = r"O-I|C-1|C-2|C-3|M-1|M-2"


def is_header(line, col_re):
    return len(re.findall(col_re, line)) >= 3


def column_centers(line, col_re):
    return {m.group(): m.start() + len(m.group()) / 2 for m in re.finditer(col_re, line)}


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    try:
        import pypdf
    except ImportError:
        print("pypdf is required: pip install pypdf", file=sys.stderr)
        return 1

    pdf, first_page, last_page, want = argv[1], int(argv[2]), int(argv[3]), argv[4]
    col_re = argv[5] if len(argv) > 5 else DEFAULT_COLUMNS
    reader = pypdf.PdfReader(pdf)
    cols = None

    for page_no in range(first_page, last_page + 1):
        lines = reader.pages[page_no - 1].extract_text(extraction_mode="layout").splitlines()
        page_header = next((ln for ln in lines if is_header(ln, col_re)), None)
        if page_header:
            cols = column_centers(page_header, col_re)
        if not cols:
            continue
        left_edge = min(cols.values()) - 6

        for line in lines:
            if not line.strip() or is_header(line, col_re):
                continue
            tokens = [(m.start() + len(m.group()) / 2, m.group())
                      for m in TOKEN_RE.finditer(line) if m.start() >= left_edge]
            name = line[:int(left_edge)].strip()
            if not tokens:
                if name:
                    print("## " + name)
                continue
            values = {}
            for x, value in tokens:
                values[min(cols, key=lambda k: abs(cols[k] - x))] = value
            row = " ".join("{}:{}".format(k, values.get(k, "-")) for k in cols)
            print("p{} {} => {}={}   [{}]".format(page_no, name, want, values.get(want, "--"), row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
