"""
kategori.py - ENTITY Kategori.
"""




class Kategori:
    OTP = 1
    TRANSAKSI = 2
    LAINNYA = 3
    _NAMA = {OTP: "OTP", TRANSAKSI: "Transaksi Bank", LAINNYA: "Lainnya"}

    def __init__(self, idKategori, namaKategori=None):
        self.idKategori = idKategori
        self.namaKategori = namaKategori or Kategori._NAMA.get(idKategori, "Lainnya")

    def getNama(self):
        return self.namaKategori

    @staticmethod
    def dariNama(nama):
        for i, n in Kategori._NAMA.items():
            if n == nama:
                return Kategori(i, n)
        return Kategori(Kategori.LAINNYA)
