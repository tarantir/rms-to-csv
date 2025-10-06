
from typing import List, Dict
from .helpers import CRLF

def _line(s: str) -> bytes:
    return (s + "\r\n").encode("utf-8")

def build_address_header(meta: Dict, mbo: str = "") -> bytes:
    # Construct the Address Header block for B2 encapsulated messages.
    if not meta.get("mid"):
        raise ValueError("Missing Message-ID (Mid)")
    if meta.get("body_bytes") is None:
        raise ValueError("Missing body_bytes")

    body = meta["body_bytes"]
    files = meta.get("attachments", [])

    out = bytearray()
    out += _line(f"Mid: {meta['mid']}")
    out += _line(f"Date: {meta['date']}")
    out += _line("Type: Private")
    out += _line(f"From: {meta.get('from','')}")

    to_list = meta.get("to", [])
    cc_list = meta.get("cc", [])
    for t in to_list:
        out += _line(f"To: {t}")
    for c in cc_list:
        out += _line(f"Cc: {c}")

    out += _line(f"Subject: {meta.get('subject','')}")
    if mbo:
        out += _line(f"Mbo: {mbo}")

    body_len = len(body)
    out += _line(f"Body:{body_len}")
    out += body + CRLF

    for att in files:
        name = att.get("filename") or "attachment.bin"
        data = att.get("data") or b""
        out += _line(f"File:{len(data)} {name}")
        out += data + CRLF

    return bytes(out)
