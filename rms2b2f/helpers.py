
import re
from datetime import datetime, timezone

CRLF = b"\r\n"

def normalize_crlf(data: bytes) -> bytes:
    # Normalize any line endings to CRLF and ensure the payload uses CRLF consistently.
    text = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return b"\r\n".join(text.split(b"\n"))

def to_utc_datestr(dt_str: str) -> str:
    # Parse an RFC2822/5322 Date header into 'YYYY/MM/DD HH:MM' in UTC.
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y/%m/%d %H:%M")
    except Exception:
        # Fallbacks
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                dt = datetime.strptime(dt_str.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).strftime("%Y/%m/%d %H:%M")
            except Exception:
                continue
        return datetime.now(timezone.utc).strftime("%Y/%m/%d %H:%M")

def callsign_from_addr(addr: str) -> str:
    # Extract likely callsign mailbox from addr like 'N5RVT@winlink.org' -> 'N5RVT'.
    if not addr:
        return ""
    local = addr.split("@", 1)[0]
    local = local.split("+", 1)[0]
    return local.upper()

def split_addrs(header_val: str):
    if not header_val:
        return []
    parts = [p.strip() for p in header_val.replace("\n", " ").split(",")]
    return [p for p in parts if p]
