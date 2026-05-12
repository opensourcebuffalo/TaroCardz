import re
import json
import argparse
from pathlib import Path

import fitz  # PyMuPDF


DEFAULT_SKIP_PAGES = 14


ARCANA_MAP = {
    "3": "THE COUNCIL",
    "4": "THE MAYOR",
    "7": "THE COMPTROLLER",
    "11": "THE CIVIL SERVICE",
    "12": "THE LAW",
    "13": "THE POLICE",
    "15": "THE WORKS",
    "18": "THE BOARDS",
    "20": "THE BUDGET",
    "22": "THE CONTRACT",
    "23": "THE REFERENDUM",
    "24": "THE APPOINTMENT",
    "27": "THE REAL ESTATE",
    "28": "THE ASSESSMENT",
    "30": "THE IMPROVEMENT",
    "32": "THE CHARTER",
}


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("￾", "-")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common footer noise
    text = re.sub(r"Downloaded from https://ecode360\.com/BU1237 on \d{4}-\d{2}-\d{2}", "", text)
    text = re.sub(r"City of Buffalo, NY", "", text)
    text = re.sub(r"BUFFALO CODE", "", text)
    text = re.sub(r"THE CHARTER", "", text)

    return text.strip()


def extract_pages(pdf_path: Path):
    doc = fitz.open(pdf_path)
    pages = []

    for i, page in enumerate(doc):
        page_number = i + 1
        raw_text = page.get_text("text")
        text = clean_text(raw_text)

        pages.append({
            "page_number": page_number,
            "char_count": len(text),
            "text": text
        })

        print(f"Extracted page {page_number}/{len(doc)}")

    return pages

def extract_title_amendment_from_lines(first_title: str, lines: list, start_idx: int):
    """
    Handles section titles like:

    Vacancies in the Common Council. [Amended 8-22-2002 by L.L. No. 12-2002, effective
    12-1-2002; 9-19-2006 by L.L. No. 17-2006, effective 12-6-2006 ]

    Returns:
    - clean section_title
    - full amendment text
    - number of extra lines consumed
    """

    first_title = first_title.strip()

    if "[" not in first_title:
        return first_title, None, 0

    before_bracket, after_bracket = first_title.split("[", 1)

    section_title = before_bracket.strip()
    amendment_parts = ["[" + after_bracket.strip()]

    consumed = 0

    # If amendment closes on same line, stop
    if "]" in amendment_parts[0]:
        amendment = " ".join(amendment_parts)
        return section_title, clean_text(amendment), consumed

    # Otherwise keep reading following lines until closing bracket
    for next_line in lines[start_idx + 1:]:
        consumed += 1
        amendment_parts.append(next_line.strip())

        if "]" in next_line:
            break

    amendment = clean_text(" ".join(amendment_parts))
    return section_title, amendment, consumed

def roman_article_to_number(line: str):
    match = re.match(r"ARTICLE\s+([0-9]+(?:-[A-Z])?)\b", line.strip(), re.I)
    if match:
        return match.group(1)
    return None


def is_article_heading(line: str):
    return bool(re.match(r"^ARTICLE\s+[0-9]+(?:-[A-Z])?\b", line.strip(), re.I))


def section_match(line: str):
    """
    Detects section headers like:
    § 20-1. Departmental Estimates.
    § 13-21.1. Protections for Officers.
    § 17-9. Commissioner of Parking.
    """
    return re.match(
        r"^§\s*(?P<section>[0-9]+(?:-[0-9A-Z]+)+(?:\.[0-9]+)?)\.\s*(?P<title>.*)",
        line.strip()
    )

def split_title_and_amendment(title: str):
    """
    Splits:
    Vacancies in the Common Council. [Amended 8-22-2002 by L.L. No. 12-2002, effective
    12-1-2002...]

    Into:
    section_title = Vacancies in the Common Council.
    amended = [Amended ...]
    """
    title = title.strip()

    if "[" not in title:
        return title, None

    raw_title, amendment = title.split("[", 1)

    section_title = raw_title.strip()
    amended = "[" + amendment.strip()

    return section_title, amended

def parse_sections(pages, skip_pages=DEFAULT_SKIP_PAGES):
    sections = []

    current_article = None
    current_article_title = None
    pending_article_number = None

    current_section = None

    for page in pages:
        page_number = page["page_number"]

        if page_number <= skip_pages:
            continue

        lines = [l.strip() for l in page["text"].splitlines() if l.strip()]

        idx = 0

        while idx < len(lines):
            line = lines[idx]

            # ARTICLE heading
            if is_article_heading(line):
                pending_article_number = roman_article_to_number(line)
                current_article = pending_article_number
                current_article_title = None

                idx += 1
                continue

            # Article title
            if pending_article_number and current_article_title is None:
                if not line.startswith("§") and not is_article_heading(line):
                    current_article_title = line
                    pending_article_number = None

                idx += 1
                continue

            # Section heading
            sm = section_match(line)

            if sm:
                # Save previous section
                if current_section:
                    current_section["text"] = clean_text(
                        "\n".join(current_section["text_parts"])
                    )

                    current_section["char_count"] = len(current_section["text"])

                    del current_section["text_parts"]

                    sections.append(current_section)

                section_number = sm.group("section")

                raw_section_title = sm.group("title").strip()

                section_title, amended, consumed_lines = (
                    extract_title_amendment_from_lines(
                        raw_section_title,
                        lines,
                        idx
                    )
                )

                article_number = section_number.split("-")[0]

                if not current_article:
                    current_article = article_number

                current_section = {
                    "source": "Buffalo Charter",
                    "article": current_article,
                    "article_title": current_article_title,
                    "section": section_number,
                    "raw_section_title": raw_section_title,
                    "section_title": section_title,
                    "amended": amended,
                    "arcana": ARCANA_MAP.get(
                        str(current_article),
                        "THE CHARTER"
                    ),
                    "page_start": page_number,
                    "page_end": page_number,
                    "text_parts": [line]
                }

                idx += consumed_lines + 1
                continue

            # Append normal text
            if current_section:
                current_section["text_parts"].append(line)
                current_section["page_end"] = page_number

            idx += 1

    # Save final section
    if current_section:
        current_section["text"] = clean_text(
            "\n".join(current_section["text_parts"])
        )

        current_section["char_count"] = len(current_section["text"])

        del current_section["text_parts"]

        sections.append(current_section)

    return sections


def make_chunks(sections, max_chars=2500):
    chunks = []

    for sec in sections:
        text = sec["text"]

        if len(text) <= max_chars:
            chunks.append({
                "source": sec["source"],
                "article": sec["article"],
                "article_title": sec["article_title"],
                "section": sec["section"],
                "section_title": sec["section_title"],
                "arcana": sec["arcana"],
                "page_start": sec["page_start"],
                "page_end": sec["page_end"],
                "chunk_index": 1,
                "text": text
            })
            continue

        parts = []
        paragraphs = re.split(r"\n\s*\n", text)

        current = ""
        for p in paragraphs:
            if len(current) + len(p) + 2 <= max_chars:
                current += "\n\n" + p if current else p
            else:
                if current:
                    parts.append(current)
                current = p

        if current:
            parts.append(current)

        for i, part in enumerate(parts, start=1):
            chunks.append({
                "source": sec["source"],
                "article": sec["article"],
                "article_title": sec["article_title"],
                "section": sec["section"],
                "section_title": sec["section_title"],
                "arcana": sec["arcana"],
                "page_start": sec["page_start"],
                "page_end": sec["page_end"],
                "chunk_index": i,
                "text": part
            })

    return chunks


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", help="Path to Buffalo Charter PDF")
    parser.add_argument("--skip-pages", type=int, default=DEFAULT_SKIP_PAGES)
    parser.add_argument("--prefix", default="buffalo_charter")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)

    pages = extract_pages(pdf_path)
    sections = parse_sections(pages, skip_pages=args.skip_pages)
    chunks = make_chunks(sections)

    page_output = {
        "source_file": pdf_path.name,
        "page_count": len(pages),
        "pages": pages
    }

    section_output = {
        "source_file": pdf_path.name,
        "section_count": len(sections),
        "sections": sections
    }

    chunk_output = {
        "source_file": pdf_path.name,
        "chunk_count": len(chunks),
        "chunks": chunks
    }

    write_json(f"{args.prefix}_pages.json", page_output)
    write_json(f"{args.prefix}_sections.json", section_output)
    write_json(f"{args.prefix}_chunks.json", chunk_output)

    print("\nDone.")
    print(f"Pages: {len(pages)}")
    print(f"Sections: {len(sections)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Saved {args.prefix}_pages.json")
    print(f"Saved {args.prefix}_sections.json")
    print(f"Saved {args.prefix}_chunks.json")


if __name__ == "__main__":
    main()