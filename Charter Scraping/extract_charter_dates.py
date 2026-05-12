import json
import re

INPUT = "buffalo_charter_sections.json"
OUTPUT = "charter_compliance_dates.json"

DATE_PATTERNS = [
    r"\bon or before [A-Z][a-z]+ \d{1,2}\b",
    r"\bnot later than [A-Z][a-z]+ \d{1,2}\b",
    r"\bno later than [A-Z][a-z]+ \d{1,2}\b",
    r"\bon the first day of [A-Z][a-z]+\b",
    r"\bon or prior to [A-Z][a-z]+ \d{1,2}\b",
    r"\bwithin \d+ (?:days|business days|months|years)\b",
    r"\bannually\b",
    r"\bannual\b",
    r"\bmonthly\b",
    r"\bquarterly\b",
    r"\beach year\b",
    r"\bevery year\b",
    r"\bJanuary\b",
    r"\bFebruary\b",
    r"\bMarch\b",
    r"\bApril\b",
    r"\bJune\b",
    r"\bJuly\b",
    r"\bAugust\b",
    r"\bSeptember\b",
    r"\bOctober\b",
    r"\bNovember\b",
    r"\bDecember\b",
]

DUTY_PATTERNS = [
    "shall file",
    "shall submit",
    "shall report",
    "shall prepare",
    "shall publish",
    "shall transmit",
    "shall furnish",
    "shall present",
    "shall deliver",
    "shall certify",
    "shall cause",
]


def clean(text):
    return " ".join(text.replace("\n", " ").split())


def find_sentences(text):
    # rough legal sentence splitter
    return re.split(r"(?<=[.;])\s+(?=[A-Z§])", clean(text))


def detect_matches(sentence):
    hits = []

    for pattern in DATE_PATTERNS:
        for match in re.finditer(pattern, sentence, flags=re.I):
            hits.append(match.group(0))

    duty_hits = [
        duty for duty in DUTY_PATTERNS
        if duty in sentence.lower()
    ]

    return hits, duty_hits


def infer_frequency(sentence):
    s = sentence.lower()

    if "quarterly" in s:
        return "quarterly"
    if "monthly" in s:
        return "monthly"
    if "annually" in s or "annual" in s or "each year" in s or "every year" in s:
        return "annually"
    if "within" in s:
        return "triggered deadline"

    return None


def make_audit_question(section, sentence):
    return f"Did the City comply with Charter § {section} requirement: {sentence[:180]}..."


def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for sec in data["sections"]:
        text = sec.get("text", "")
        sentences = find_sentences(text)

        for sentence in sentences:
            date_hits, duty_hits = detect_matches(sentence)

            if date_hits or duty_hits:
                # avoid totally irrelevant generic sentences
                if not any(word in sentence.lower() for word in [
                    "shall", "annual", "annually", "monthly", "quarterly",
                    "within", "on or before", "not later than", "no later than"
                ]):
                    continue

                results.append({
                    "article": sec.get("article"),
                    "article_title": sec.get("article_title"),
                    "section": sec.get("section"),
                    "section_title": sec.get("section_title"),
                    "arcana": sec.get("arcana"),
                    "page_start": sec.get("page_start"),
                    "page_end": sec.get("page_end"),
                    "date_or_frequency_hits": date_hits,
                    "duty_hits": duty_hits,
                    "frequency": infer_frequency(sentence),
                    "source_sentence": sentence,
                    "audit_question": make_audit_question(sec.get("section"), sentence),
                    "review_status": "needs_review"
                })

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump({
            "source": INPUT,
            "record_count": len(results),
            "records": results
        }, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(results)} records to {OUTPUT}")


if __name__ == "__main__":
    main()