
from typing import List, Dict, Tuple, Optional
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
import base64, quopri
from .helpers import normalize_crlf, callsign_from_addr, split_addrs

def _decode_part_bytes(part) -> bytes:
    cte = (part.get('Content-Transfer-Encoding') or "").lower()
    payload = part.get_payload(decode=False)
    if isinstance(payload, list):
        payload = "".join(p.get_payload(decode=False) for p in part.get_payload())
    if isinstance(payload, str):
        raw = payload.encode('utf-8', errors='ignore')
    else:
        raw = payload or b""

    if cte == "base64":
        try:
            import base64
            return base64.b64decode(raw, validate=False)
        except Exception:
            return base64.b64decode(raw + b"==")
    elif cte in ("quoted-printable", "quotedprintable"):
        return quopri.decodestring(raw)
    else:
        return raw

def parse_rms_mime(path: str) -> Dict:
    # Parse a Winlink RMS .mime source file into a structured dict.
    from .helpers import to_utc_datestr

    with open(path, 'rb') as f:
        msg: EmailMessage = BytesParser(policy=policy.default).parse(f)

    mid = (msg['Message-ID'] or msg['Message-Id'] or "").strip().strip("<>")
    date_hdr = msg['Date'] or ""
    subj = msg['Subject'] or ""
    from_addr = (msg['From'] or "").strip()
    to_hdr = msg['To'] or ""
    cc_hdr = msg['Cc'] or ""

    body_bytes = b""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            if part.is_multipart():
                continue
            ctype = (part.get_content_type() or "").lower()
            disp = (part.get('Content-Disposition') or "").lower()
            filename = part.get_filename()
            data = _decode_part_bytes(part)
            if ctype == "text/plain" and "attachment" not in disp and body_bytes == b"":
                body_bytes = data
            else:
                if filename:
                    attachments.append({"filename": filename, "data": data})
    else:
        body_bytes = _decode_part_bytes(msg)

    body_bytes = normalize_crlf(body_bytes)
    for att in attachments:
        att["data"] = normalize_crlf(att["data"])

    parsed = {
        "mid": mid,
        "date": to_utc_datestr(date_hdr),
        "from": callsign_from_addr(from_addr),
        "to": split_addrs(to_hdr),
        "cc": split_addrs(cc_hdr),
        "subject": subj,
        "body_bytes": body_bytes,
        "attachments": attachments,
    }
    return parsed
