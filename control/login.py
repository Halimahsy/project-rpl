"""
login.py - CONTROL VerifikasiNomorController (verifikasi nomor & OTP).
"""

from core.utils import normalisasi_nomor
from entity.otp import OTP


class VerifikasiNomorController:
    def __init__(self, db):
        self._db = db
        self.nomorTelepon = ""
        self.otpAktif = None

    def validasiFormat(self, no):
        return normalisasi_nomor(no) != ""

    def verifikasiNomor(self, no):
        """Validasi format lalu kirim OTP. Return OTP atau None bila format salah."""
        if not self.validasiFormat(no):
            return None
        self.nomorTelepon = normalisasi_nomor(no)
        return self.kirimOTP(self.nomorTelepon)

    def kirimOTP(self, no):
        otp = OTP()
        otp.generateKode()
        self.otpAktif = otp
        self._db.data["otp"].append({"kodeOTP": otp.kodeOTP,
                                     "waktuDibuat": otp.waktuDibuat.isoformat(),
                                     "status": otp.status})
        self._db.simpan()
        # Produksi: kirim otp.kodeOTP lewat gateway SMS ke `no`.
        # Di versi simpel ini kodenya ditampilkan di layar (mode demo).
        return otp

    def verifikasiOTP(self, kode):
        """Return 'berhasil' | 'salah' | 'kedaluwarsa' | 'tidak_ada'."""
        otp = self.otpAktif
        if otp is None:
            return "tidak_ada"
        if otp.cekKedaluwarsa():
            return "kedaluwarsa"
        if not otp.cocokkanKode(kode):
            return "salah"
        otp.status = "terpakai"
        self.simpanStatusVerifikasi()
        return "berhasil"

    def mintaKirimUlangOTP(self):
        return self.kirimOTP(self.nomorTelepon)

    def simpanStatusVerifikasi(self):
        u = self._db.data["user"]
        u["nomorTelepon"] = self.nomorTelepon
        u["statusVerifikasi"] = True
        self._db.simpan()
