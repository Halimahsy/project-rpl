"""
kelola_sms.py - CONTROL SMSController (terima, kirim, baca, hapus SMS).
"""

from datetime import datetime

from core.konstanta import MAKS_KARAKTER_SMS
from core.utils import normalisasi_nomor
from entity.sms import SMS


class SMSController:
    def __init__(self, db, filteringCtrl):
        self._db = db
        self._fc = filteringCtrl
        self.daftarSMS = []
        self.perbaruiDaftarSMS()

    def perbaruiDaftarSMS(self):
        self.daftarSMS = sorted(
            (SMS._dari_dict(self._db, d) for d in self._db.data["sms"]),
            key=lambda s: s.waktu, reverse=True)
        return self.daftarSMS

    def getSMS(self):
        return self.perbaruiDaftarSMS()

    def getDetailSMS(self, id):
        sms = SMS.getDetail(self._db, id)
        if sms and sms.jenis == "masuk" and sms.status == "baru":
            sms.status = "dibaca"
            sms.simpan()
        return sms

    def terimaSMS(self, data):
        """data: {'nomorPengirim', 'isiPesan', 'waktu'(opsional)}"""
        sms = SMS(self._db, self._db.id_baru(), data["nomorPengirim"],
                  self._db.data["user"]["nomorTelepon"], data["isiPesan"],
                  data.get("waktu") or datetime.now(), "masuk", "baru", None)
        sms.simpan()
        if self._db.data["pengaturan"]["klasifikasiOtomatis"]:
            self._fc.filtering(sms)          # -> kategorisasi -> NaiveBayes
        self.perbaruiDaftarSMS()
        return SMS.getDetail(self._db, sms.idSMS)

    def validasiPesan(self, isi):
        isi = (isi or "").strip()
        return 0 < len(isi) <= MAKS_KARAKTER_SMS

    def kirimSMS(self, nomor, isi):
        """Return (berhasil: bool, pesan: str)."""
        tujuan = normalisasi_nomor(nomor)
        if not tujuan:
            return False, "Nomor tujuan tidak valid."
        if not self.validasiPesan(isi):
            return False, f"Isi pesan harus 1-{MAKS_KARAKTER_SMS} karakter."
        tujuan_fmt = "+62" + tujuan
        status = "terkirim"
        try:
            self._kirim_via_perangkat(tujuan_fmt, isi.strip())
        except Exception:
            status = "gagal"
        sms = SMS(self._db, self._db.id_baru(),
                  self._db.data["user"]["nomorTelepon"], tujuan_fmt,
                  isi.strip(), datetime.now(), "keluar", status, None)
        sms.simpan()
        self.perbaruiDaftarSMS()
        if status == "gagal":
            return False, "SMS gagal dikirim. Coba lagi."
        return True, "SMS berhasil dikirim."

    @staticmethod
    def _kirim_via_perangkat(nomor, isi):
        """Android: kirim SMS sungguhan lewat plyer. Desktop: disimulasikan."""
        try:
            from kivy.utils import platform
        except ImportError:
            return
        if platform == "android":
            from plyer import sms           # butuh izin SEND_SMS
            sms.send(recipient=nomor, message=isi)

    def hapusSMS(self, id):
        sms = SMS.getDetail(self._db, id)
        if sms is None:
            return False
        sms.hapus()
        self.perbaruiDaftarSMS()
        return True
