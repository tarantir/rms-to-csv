import os, sys, re, csv

HEADER_STOP_RE = re.compile(rb'(?im)^[ \t]*Body:[ \t]*\d+[ \t]*$', re.M)

def find_header_block(data: bytes) -> bytes:
    m = HEADER_STOP_RE.search(data)
    if not m:
        return data
    return data[:m.start()]

def decode_text(b: bytes) -> str:
    for enc in ("utf-8", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", errors="replace")

def extract_fields(header_text: str):
    text = header_text.replace("\r\n", "\n").replace("\r", "\n")
    def grab(key):
        m = re.search(rf'(?im)^[ \t]*{re.escape(key)}[ \t]*:[ \t]*(.+)$', text)
        return (m.group(1).strip() if m else "")
    return {
        "Date": grab("Date"),
        "Sender": grab("From"),
        "Subject": grab("Subject"),
    }

def scan_folder(folder: str):
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
                info = extract_fields(decode_text(header))
                rows.append(info)
            except Exception as e:
                rows.append({"Date":"", "Sender":"", "Subject":f"ERROR: {e}"})
    return rows

def main():
    if len(sys.argv) < 3:
        print("Usage: python b2f2csv.py <folder_with_b2f> <output_csv>")
        sys.exit(2)
    folder = sys.argv[1]
    out_csv = sys.argv[2]
    rows = scan_folder(folder)
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Date","Sender","Subject"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(out_csv)

if __name__ == "__main__":
    main()
