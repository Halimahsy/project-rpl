"""
filtering_sms.py - CONTROL FilteringController.
"""

import re


class FilteringController:
    def __init__(self, kategorisasiCtrl):
        self._kc = kategorisasiCtrl
        self.kriteriaFilter = "isi tidak kosong; spasi berlebih dibersihkan"

    def filtering(self, sms):
        teks = re.sub(r"\s+", " ", sms.getIsiSMS() or "").strip()
        if not teks:
            self.tampilkanDataTidakDitemukan()
            return None
        return self.kirimHasilFiltering(sms, teks)

    def kirimHasilFiltering(self, sms, teks):
        return self._kc.hasilFiltering(sms, teks)

    def tampilkanDataTidakDitemukan(self):
        return "Isi SMS tidak dapat dibaca."
