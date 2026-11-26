"""
utils.py - fungsi bantu untuk nomor telepon.
"""

import re


def normalisasi_nomor(no):
    """'0857-2341-2004' / '+62 857...' / '85723412004' -> '85723412004'
    (nomor tanpa kode negara/nol depan) atau '' jika tidak valid."""
    d = re.sub(r"\D", "", no or "")
    if d.startswith("62"):
        d = d[2:]
    elif d.startswith("0"):
        d = d[1:]
    return d if re.fullmatch(r"8\d{8,11}", d) else ""


def format_nomor(no_lokal):
    d = no_lokal
    return f"+62 {d[:3]}-{d[3:7]}-{d[7:]}"
