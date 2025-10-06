📦 B2F Conversion & Extraction Toolkit
This toolkit provides utilities for working with Winlink / RMS Express message files (.mime) and converting them into B2F encapsulated message format, as well as extracting summary metadata from B2F files into a CSV report.

🧩 Components
1. rms2b2f – RMS to B2F Converter
Converts RMS Express / Winlink .mime message files into compliant B2F encapsulated message files that can be used by FBB, Winlink Gateway, or similar systems.
🔧 Features
    • Parses .mime messages and attachments (Base64, Quoted-Printable, 7/8-bit, etc.)
    • Builds a valid B2F header block with correct field order:
      Mid:
      Date:
      Type:
      From:
      To:
      Cc:
      Subject:
      Mbo:
      Body:<len>
      <CRLF>
      <body data>
      File:<len> <filename>
      <file data>
    • Automatically adds a blank line between Body:<len> and the body content.
    • Handles malformed MIME headers (e.g., “ICS 213” without a colon).
    • Automatically generates Mid if missing.
    • Normalizes all line endings to CRLF (\r\n).
    • Preserves attachments in their original order.
    • Supports batch conversion and optional mailbox tagging (Mbo: field).

2. b2f2csv.py – B2F Metadata Extractor
Extracts key metadata (Date, Sender, Subject) from a folder of .b2f files and writes a concise CSV summary.
🧠 How It Works
    • Scans each .b2f file.
    • Reads everything before the first Body:<len> line (case-insensitive).
    • Uses flexible regex matching for Date:, From:, and Subject: fields.
    • Writes results into a CSV with only these columns:
      Date,Sender,Subject
    • Ignores filenames and attachments.
    • Robust to extra spaces, casing differences, or missing fields.

🚀 Installation
    1. Copy both directories and scripts into your workspace:
       rms2b2f/
       rms2b2f_runner.py
       b2f2csv.py
    2. Requires Python 3.8+ (no external libraries required except standard library).

⚙️ Usage
🧭 Convert .mime Files to .b2f
python rms2b2f_runner.py /path/to/mime_folder -o /path/to/output_b2f --mbo N5RVT
Example Output Structure
Mid: HIPFF2TDRRF8
Date: 2025/10/05 13:24
Type: Private
From: N5RVT
To: W0XYZ
Subject: ICS Form 213 Test
Mbo: N5RVT
Body:421
<blank line>
<message body>
File:232 ICS213.xml
<attachment data>
Notes:
    • The converter ensures exactly one blank line after the Body:<len> header.
    • Attachments are placed after the message body, each followed by a CRLF.
    • Type: Private is used by default unless otherwise specified.

📊 Extract Summary from .b2f Files
python b2f2csv.py /path/to/b2f_folder /path/to/output.csv
Example Output CSV:
Date,Sender,Subject
2025/10/05 13:24,N5RVT,ICS Form 213 Test
2025/10/04 19:10,K5ABC,Daily Check-In
2025/10/04 18:45,N5RVT,GENERAL MESSAGE (ICS 213)

🧱 File Structure Overview
rms2b2f/
├── __init__.py
├── helpers.py           # Line normalization, date parsing, callsign extraction
├── rms_parser.py        # MIME parser (robust fallback)
├── b2f_builder.py       # Builds encapsulated B2F structure
└── cli.py               # CLI entrypoint for batch conversion

rms2b2f_runner.py        # Simple executable wrapper

b2f2csv.py  # CSV metadata extractor

🛠️ Implementation Notes
📤 MIME Parsing Logic
    • Uses Python’s built-in email module.
    • Extracts:
        ◦ Message headers: Message-ID, Date, From, To, Cc, Subject
        ◦ Body: first text/plain part
        ◦ Attachments: other parts with filenames
    • Falls back to plaintext salvage mode if malformed headers are detected.
🧱 B2F Construction
    • Header block lines end with CRLF.
    • Length values (Body:<len> and File:<len>) count only the data bytes, excluding CRLF terminators.
    • Automatically ensures one CRLF between Body:<len> and body data.
🧩 Extraction Regex
    • Stops parsing header at first Body:<len> (case-insensitive).
    • Regex is forgiving of variations like:
        ◦ Date : 2025/10/05
        ◦ FROM : N5RVT
        ◦ subject: ICS 213

🧪 Example End-to-End Workflow
    1. Convert your RMS messages:
       python rms2b2f_runner.py /inbox/*.mime -o /outbox_b2f --mbo N5RVT
    2. Verify .b2f structure (first 20 lines):
       head -20 /outbox_b2f/HIPFF2TDRRF8.b2f
    3. Generate a summary report:
       python b2f2csv.py /outbox_b2f /reports/summary.csv
    4. Open /reports/summary.csv in Excel or import into analysis tools.

🪪 License
This toolkit is provided for amateur radio and emergency communications use (e.g., ARES, RACES, SHARES).
Open use is permitted under the MIT License, with attribution encouraged.
