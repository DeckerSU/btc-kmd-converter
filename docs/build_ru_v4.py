#!/usr/bin/env python3
"""
build_ru_v4.py
--------------
Generate a compact ru-v4.bin (and ru-v4.bin.gz) from IP2LOCATION-LITE-DB1.CSV.

• Requires Python 3.8+ and only standard libraries.
• CSV format: "ip_from","ip_to","country_code","country_name"
  where ip_from / ip_to are either dotted IPv4 or decimal integers.

curl -L https://download.ip2location.com/lite/IP2LOCATION-LITE-DB1.CSV.ZIP \
     -o IP2LOCATION-LITE-DB1.CSV.ZIP
unzip IP2LOCATION-LITE-DB1.CSV.ZIP
"""

import csv
import gzip
import ipaddress
import pathlib
import struct
import sys

CSV_FILE   = sys.argv[1] if len(sys.argv) > 1 else 'IP2LOCATION-LITE-DB1.CSV'
OUT_BIN    = 'ru-v4.bin'
COUNTRY_CC = 'RU'              # ISO-3166 code to filter

def ip_to_int(value: str) -> int:
    """Convert '1.2.3.4' or '16777216' to 32-bit unsigned int."""
    return int(ipaddress.IPv4Address(value)) if '.' in value else int(value)

pairs = []
with open(CSV_FILE, newline='') as f:
    for row in csv.reader(f):
        if len(row) < 3:
            continue
        ip_from, ip_to, cc = row[0], row[1], row[2].upper()
        if cc == COUNTRY_CC:
            pairs.append((ip_to_int(ip_from), ip_to_int(ip_to)))

if not pairs:
    sys.exit(f'No ranges for {COUNTRY_CC} found in {CSV_FILE}')

pairs.sort()
buf = bytearray(len(pairs) * 8)
for i, (start, end) in enumerate(pairs):
    struct.pack_into('>II', buf, i * 8, start, end)   # big-endian

pathlib.Path(OUT_BIN).write_bytes(buf)
size_kib = len(buf) // 1024
print(f'Wrote {len(pairs):,} ranges → {size_kib} KiB → {OUT_BIN}')

with gzip.open(OUT_BIN + '.gz', 'wb', compresslevel=9) as g:
    g.write(buf)
print(f'Also created {OUT_BIN}.gz')
