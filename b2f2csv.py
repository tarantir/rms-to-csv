
import os, sys, csv

def decode_bytes(b: bytes) -> str:
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('latin-1', errors='replace')

def parse_b2f_header(text: str):
    out = {"Date": "", "From": "", "Subject": ""}
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for line in lines:
        if not line:
            continue
        if line.startswith("Body:"):
            break
        if line.startswith("Date:"):
            out["Date"] = line[5:].strip()
        elif line.startswith("From:"):
            out["From"] = line[5:].strip()
        elif line.startswith("Subject:"):
            out["Subject"] = line[8:].strip()
    return out

def collect(folder: str):
    records = []
    for root, _, files in os.walk(folder):
        for name in files:
            if not name.lower().endswith(".b2f"):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "rb") as f:
                    data = f.read()
                text = decode_bytes(data)
                info = parse_b2f_header(text)
                records.append({
                    "Date": info.get("Date",""),
                    "Sender": info.get("From",""),
                    "Subject": info.get("Subject",""),
                    "File": path,
                })
            except Exception as e:
                records.append({
                    "Date": "",
                    "Sender": "",
                    "Subject": f"ERROR: {e}",
                    "File": path,
                })
    return records

def main():
    if len(sys.argv) < 3:
        print("Usage: python b2f_to_csv.py <folder_with_b2f> <output_csv>")
        sys.exit(2)
    folder = sys.argv[1]
    out_csv = sys.argv[2]
    rows = collect(folder)
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Date","Sender","Subject","File"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(out_csv)

if __name__ == "__main__":
    main()
