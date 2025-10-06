
#!/usr/bin/env python3
import argparse, pathlib, sys, os
from .rms_parser import parse_rms_mime
from .b2f_builder import build_address_header

def convert_one(src_path: str, out_dir: str, mbo: str = "") -> str:
    meta = parse_rms_mime(src_path)
    b2f_bytes = build_address_header(meta, mbo=mbo)

    mid_safe = meta['mid'] or pathlib.Path(src_path).stem
    # Sanitize filename characters
    mid_safe = "".join(ch for ch in mid_safe if ch.isalnum() or ch in ("-", "_"))
    out_name = f"{mid_safe}.b2f"
    out_path = os.path.join(out_dir, out_name)
    with open(out_path, "wb") as f:
        f.write(b2f_bytes)
    return out_path

def main():
    ap = argparse.ArgumentParser(
        description="Convert Winlink RMS .mime source files to B2F encapsulated message files."
    )
    ap.add_argument("inputs", nargs="+", help="Input .mime file(s) or directory/directories.")
    ap.add_argument("-o", "--out-dir", default=".", help="Output directory for .b2f files.")
    ap.add_argument("--mbo", default="", help="Optional mailbox (Mbo:) to include.")
    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    produced = []
    for inp in args.inputs:
        p = pathlib.Path(inp)
        if p.is_dir():
            for child in p.glob("*.mime"):
                produced.append(convert_one(str(child), out_dir, mbo=args.mbo))
        else:
            produced.append(convert_one(str(p), out_dir, mbo=args.mbo))

    for path in produced:
        print(path)

if __name__ == "__main__":
    main()
