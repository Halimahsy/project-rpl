"""
otp.py - ENTITY OTP.
"""

import secrets
from datetime import datetime

from core.konstanta import MASA_BERLAKU_OTP


class OTP:
    def __init__(self, kodeOTP="", waktuDibuat=None, waktuKedaluwarsa=None,
                 status="aktif"):
        self.kodeOTP = kodeOTP
        self.waktuDibuat = waktuDibuat
        self.waktuKedaluwarsa = waktuKedaluwarsa
        self.status = status                # "aktif" | "terpakai" | "kedaluwarsa"

    def generateKode(self):
        self.kodeOTP = "".join(str(secrets.randbelow(10)) for _ in range(6))
        self.waktuDibuat = datetime.now()
        self.waktuKedaluwarsa = self.waktuDibuat + MASA_BERLAKU_OTP
        self.status = "aktif"
        return self.kodeOTP

    def cekKedaluwarsa(self):
        if self.waktuKedaluwarsa is None or datetime.now() > self.waktuKedaluwarsa:
            self.status = "kedaluwarsa"
            return True
        return False

    def cocokkanKode(self, kode):
        return self.status == "aktif" and secrets.compare_digest(self.kodeOTP, kode)
