import re
import csv
import json
import argparse
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://buffalony.iqm2.com/Citizens/"
DEFAULT_URL = "https://buffalony.iqm2.com/Citizens/Detail_Meeting.aspx?ID=3347"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())


def get_value(soup, selector):
    el = soup.select_one(selector)
    return clean(el.get_text()) if el else None


def get_input_value(soup, selector):
    el = soup.select_one(selector)
    return el.get("value") if el else None


def parse_item_text(text):
    """
    Parses:
    26-671 : Mayor Out of Town Travel 5/5-5/6/2026
    """
    match = re.match(r"(?P<file_number>\d{2}-\d+)\s*:\s*(?P<title>.*)", text)
    if not match:
        return None, clean(text)

    return match.group("file_number"), clean(match.group("title"))


def classify_attachment(href):
    if "Type=30" in href:
        return "agenda_item_printout"
    if "Type=4" in href:
        return "item_attachment"
    if "Type=14" in href:
        return "agenda"
    if "Type=1" in href:
        return "agenda_packet"
    return "unknown"


def scrape_meeting(url):
    res = requests.get(url, headers=HEADERS, timeout=30)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    meeting = {
        "source_url": url,
        "meeting_id": get_input_value(soup, "#ContentPlaceholder1_txtMeetingID"),
        "agenda_id": get_input_value(soup, "#ContentPlaceholder1_txtAgendaID"),
        "group": get_value(soup, "#ContentPlaceholder1_lblMeetingGroup"),
        "meeting_type": get_value(soup, "#ContentPlaceholder1_lblMeetingType"),
        "meeting_date": get_value(soup, "#ContentPlaceholder1_lblMeetingDate"),
        "downloads": [],
        "items": []
    }

    downloads = soup.select_one("#ContentPlaceholder1_pnlDownloads")
    if downloads:
        for a in downloads.find_all("a", href=True):
            href = a["href"]
            meeting["downloads"].append({
                "label": clean(a.get_text()),
                "type": a.get("data-type") or classify_attachment(href),
                "url": urljoin(BASE_URL, href)
            })

    table = soup.select_one("table#MeetingDetail")
    if not table:
        raise RuntimeError("Could not find table#MeetingDetail")

    current_section = None
    current_item = None

    for tr in table.find_all("tr"):
        row_text = clean(tr.get_text(" ", strip=True))
        if not row_text:
            continue

        strong = tr.find("strong")
        if strong:
            section = clean(strong.get_text())
            if section:
                current_section = section
                current_item = None
            continue

        links = tr.find_all("a", href=True)
        num_cells = tr.select("td.Num")
        num_values = [clean(td.get_text()) for td in num_cells if clean(td.get_text())]

        agenda_order = None
        for val in num_values:
            if re.match(r"^\d+\.$", val):
                agenda_order = val.replace(".", "")
                break

        # Main agenda item row
        if agenda_order and links:
            item_link = links[0]
            item_text = clean(item_link.get_text())
            file_number, title = parse_item_text(item_text)

            current_item = {
                "meeting_id": meeting["meeting_id"],
                "agenda_id": meeting["agenda_id"],
                "section": current_section,
                "agenda_order": agenda_order,
                "file_number": file_number,
                "title": title,
                "raw_item_text": item_text,
                "item_url": urljoin(BASE_URL, item_link["href"]),
                "attachments": []
            }

            meeting["items"].append(current_item)
            continue

        # Attachment rows under the current agenda item
        if current_item and links:
            for a in links:
                href = a["href"]
                current_item["attachments"].append({
                    "label": clean(a.get_text()),
                    "type": classify_attachment(href),
                    "url": urljoin(BASE_URL, href)
                })

    return meeting


def write_json(meeting, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meeting, f, indent=2, ensure_ascii=False)


def write_items_csv(meeting, path):
    fields = [
        "meeting_id",
        "agenda_id",
        "meeting_date",
        "section",
        "agenda_order",
        "file_number",
        "title",
        "item_url",
        "attachment_count"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for item in meeting["items"]:
            writer.writerow({
                "meeting_id": meeting["meeting_id"],
                "agenda_id": meeting["agenda_id"],
                "meeting_date": meeting["meeting_date"],
                "section": item["section"],
                "agenda_order": item["agenda_order"],
                "file_number": item["file_number"],
                "title": item["title"],
                "item_url": item["item_url"],
                "attachment_count": len(item["attachments"])
            })


def write_attachments_csv(meeting, path):
    fields = [
        "file_number",
        "agenda_order",
        "section",
        "item_title",
        "attachment_label",
        "attachment_type",
        "attachment_url"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for item in meeting["items"]:
            for att in item["attachments"]:
                writer.writerow({
                    "file_number": item["file_number"],
                    "agenda_order": item["agenda_order"],
                    "section": item["section"],
                    "item_title": item["title"],
                    "attachment_label": att["label"],
                    "attachment_type": att["type"],
                    "attachment_url": att["url"]
                })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--prefix", default="meeting_3347")
    args = parser.parse_args()

    meeting = scrape_meeting(args.url)

    write_json(meeting, f"{args.prefix}.json")
    write_items_csv(meeting, f"{args.prefix}_items.csv")
    write_attachments_csv(meeting, f"{args.prefix}_attachments.csv")

    print(f"Meeting: {meeting['group']} — {meeting['meeting_date']}")
    print(f"Scraped {len(meeting['items'])} agenda items")
    print(f"Saved {args.prefix}.json")
    print(f"Saved {args.prefix}_items.csv")
    print(f"Saved {args.prefix}_attachments.csv")


if __name__ == "__main__":
    main()
