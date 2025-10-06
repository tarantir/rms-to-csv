
from typing import Dict
from .helpers import CRLF
import time, os

def _line(s: str) -> bytes:
    return (s + "\r\n").encode("utf-8")

def _auto_mid() -> str:
    return f"AUTO-{int(time.time())}-{os.getpid()}"

def build_address_header(meta: Dict, mbo: str = "") -> bytes:
    # Construct the Address Header block for B2 encapsulated messages.
    mid = meta.get("mid") or _auto_mid()
    body = meta.get("body_bytes", b"")
    if body is None:
        body = b""
    files = meta.get("attachments", [])

    out = bytearray()
    out += _line(f"Mid: {mid}")
    out += _line(f"Date: {meta.get('date','')}")
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
