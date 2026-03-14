"""
b2f2csv.py — Extract Date, Sender, and Subject from Winlink B2F message files
and write them to a CSV sorted chronologically.

Usage:
    python b2f2csv.py <folder_with_b2f_files> <output.csv>
"""

import csv
import os
import re
import sys
from datetime import datetime
from email.utils import parsedate_to_datetime

# Marks the boundary between the B2F header and the message body.
# The "Body: <n>" line signals the start of the body, so everything before
# it is the header we want to parse.
HEADER_STOP_RE = re.compile(rb'(?im)^[ \t]*Body:[ \t]*\d+[ \t]*$')

# Date formats produced by common Winlink clients (most specific first)
DATE_FORMATS = [
    "%Y/%m/%d %H:%M",
    "%Y-%m-%d %H:%M",
]

CSV_FIELDS = ["Date", "Sender", "Subject"]


def find_header_block(data: bytes) -> bytes:
    """Return only the header portion of a raw B2F file (before the Body line)."""
    m = HEADER_STOP_RE.search(data)
    return data[:m.start()] if m else data


def decode_text(b: bytes) -> str:
    """Decode bytes to str, trying UTF-8 then Latin-1 before falling back."""
    for enc in ("utf-8", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", errors="replace")


def extract_fields(header_text: str) -> dict:
    """Parse Date, From, and Subject out of a plain-text B2F header block."""
    # Normalise line endings so the regex works regardless of origin OS
    text = header_text.replace("\r\n", "\n").replace("\r", "\n")

    def grab(key: str) -> str:
        m = re.search(rf'(?im)^[ \t]*{re.escape(key)}[ \t]*:[ \t]*(.+)$', text)
        return m.group(1).strip() if m else ""

    return {
        "Date":    grab("Date"),
        "Sender":  grab("From"),
        "Subject": grab("Subject"),
    }


def parse_date(date_str: str) -> datetime:
    """
    Parse a date string from a B2F header into a naive datetime for sorting.
    Tries known Winlink formats first, then falls back to RFC 2822 parsing.
    Returns datetime.min for unparseable values so they sort to the top.
    """
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    try:
        # RFC 2822 dates are timezone-aware; strip tzinfo for uniform comparison
        return parsedate_to_datetime(date_str).replace(tzinfo=None)
    except Exception:
        return datetime.min


def scan_folder(folder: str) -> list[dict]:
    """Walk *folder* recursively and extract fields from every .b2f file found."""
    rows = []
    for root, _, files in os.walk(folder):
        for name in files:
            if not name.lower().endswith(".b2f"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "rb") as f:
                    data = f.read()
                header = find_header_block(data)
                rows.append(extract_fields(decode_text(header)))
            except Exception as e:
                rows.append({"Date": "", "Sender": "", "Subject": f"ERROR: {e}"})
    return rows


def write_csv(rows: list[dict], out_path: str) -> None:
    """Write *rows* to a CSV file at *out_path*, creating parent dirs as needed."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python b2f2csv.py <folder_with_b2f> <output_csv>")
        sys.exit(2)

    folder, out_csv = sys.argv[1], sys.argv[2]

    rows = scan_folder(folder)
    rows.sort(key=lambda r: parse_date(r["Date"]))
    write_csv(rows, out_csv)

    print(out_csv)


if __name__ == "__main__":
    main()
