"""
kategorisasi_sms.py - CONTROL KategorisasiController.
"""

from entity.kategori import Kategori


class KategorisasiController:
    def __init__(self, naiveBayes):
        self._nb = naiveBayes
        self.statusProses = "idle"
        self._antrian = []          # SMS yang ditunda karena model belum siap

    def hasilFiltering(self, sms, teks):
        self.statusProses = "memproses"
        return self.kategorisasi(sms, teks)

    def kategorisasi(self, sms, teks):
        if not self._nb.cekModelTersedia():
            self.tundaKategorisasi(sms, teks)
            return None
        try:
            self._nb.klasifikasi(teks)
            kat = self._nb.kategori()
        except Exception:
            self.statusProses = "gagal"
            self.tampilkanGagalProsesDataSMS()
            return None
        self.simpanLabel(sms, kat)
        self.statusProses = "selesai"
        return kat

    def simpanLabel(self, sms, kat):
        sms.simpanLabel(kat.idKategori)

    def tampilkanKategori(self, sms):
        return Kategori(sms.idKategori) if sms.idKategori else None

    def tampilkanGagalProsesDataSMS(self):
        return "Kategorisasi gagal: data SMS tidak dapat diproses."

    def tundaKategorisasi(self, sms, teks):
        self.statusProses = "ditunda"
        self._antrian.append((sms, teks))

    def periksaUlangModel(self):
        """Dipanggil berkala/saat app dibuka: lanjutkan antrian jika model siap."""
        if not self._nb.cekModelTersedia():
            self._nb.latih()
        if self._nb.cekModelTersedia():
            antrian, self._antrian = self._antrian, []
            for sms, teks in antrian:
                self.kategorisasi(sms, teks)
        return self._nb.cekModelTersedia()
