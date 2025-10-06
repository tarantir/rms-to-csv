
from typing import Dict
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
import base64, quopri, hashlib, time
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

def _gen_mid(raw: bytes) -> str:
    h = hashlib.sha1(raw).digest()
    # Use base32 (no padding) for filename-safe token
    token = base64.b32encode(h).decode('ascii').rstrip('=')
    return f"AUTO-{token}"

def parse_rms_mime(path: str) -> Dict:
    # Parse a Winlink RMS .mime file; tolerate malformed headers by falling back to plaintext.
    from .helpers import to_utc_datestr

    raw = b""
    with open(path, 'rb') as f:
        raw = f.read()

    msg: EmailMessage = None
    try:
        msg = BytesParser(policy=policy.default).parsebytes(raw)
    except Exception:
        # Try compat32 (more forgiving) before full salvage
        try:
            msg = BytesParser(policy=policy.compat32).parsebytes(raw)
        except Exception:
            msg = None

    if msg is None or (not msg.keys() and b":" not in raw.splitlines()[0]):
        # Salvage mode: treat the entire file as a plaintext body. Guess a subject if first line lacks colon.
        body_bytes = normalize_crlf(raw)
        # Guess subject from the first text line if it doesn't contain a colon and is short
        first_line = body_bytes.split(b"\r\n", 1)[0].strip()
        subj_guess = ""
        if b":" not in first_line and 0 < len(first_line) <= 80:
            try:
                subj_guess = first_line.decode('utf-8', errors='ignore')
            except Exception:
                subj_guess = "Recovered message"
        parsed = {
            "mid": _gen_mid(raw),
            "date": to_utc_datestr(""),
            "from": "",
            "to": [],
            "cc": [],
            "subject": subj_guess,
            "body_bytes": body_bytes,
            "attachments": [],
        }
        return parsed

    # Normal path
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
                # include unnamed attachments only if they have data
                if filename or data:
                    attachments.append({"filename": filename or "attachment.bin", "data": data})
    else:
        body_bytes = _decode_part_bytes(msg)

    body_bytes = normalize_crlf(body_bytes)
    for att in attachments:
        att["data"] = normalize_crlf(att["data"])

    # Fallback Mid if missing
    if not mid:
        mid = _gen_mid(raw)

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
