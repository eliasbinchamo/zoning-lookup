#!/usr/bin/env python3
"""Dump every page of a PDF to a text file with =====PAGE n===== markers (needs pypdf).

Usage:
    python3 pdf_to_text.py <in.pdf> <out.txt>

Then `grep -n` the text for section numbers and cite the PDF page numbers from the markers.
"""
import sys


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        import pypdf
    except ImportError:
        print("pypdf is required: pip install pypdf", file=sys.stderr)
        return 1
    reader = pypdf.PdfReader(argv[1])
    with open(argv[2], "w", encoding="utf-8") as out:
        for page_no, page in enumerate(reader.pages, 1):
            out.write("\n=====PAGE {}=====\n".format(page_no))
            out.write(page.extract_text() or "")
    print("{} pages -> {}".format(len(reader.pages), argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
