"""
sistem.py - merangkai semua objek entity & control agar mudah dipanggil dari main.py.
"""

from control.filtering_sms import FilteringController
from control.kategorisasi_sms import KategorisasiController
from control.kelola_sms import SMSController
from control.login import VerifikasiNomorController
from control.naive_bayes import NaiveBayes
from core.database import Database
from entity.user import User


class Sistem:
    def __init__(self, path_db):
        self.db = Database(path_db)
        self.naiveBayes = NaiveBayes()
        self.kategorisasi = KategorisasiController(self.naiveBayes)
        self.filtering = FilteringController(self.kategorisasi)
        self.smsCtrl = SMSController(self.db, self.filtering)
        self.verifikasiCtrl = VerifikasiNomorController(self.db)
        self.user = User(self.db, self.verifikasiCtrl, self.smsCtrl)

    def logout(self):
        self.db.data["user"].update(nomorTelepon="", statusVerifikasi=False)
        self.db.data["sms"] = []
        self.db.simpan()
        self.smsCtrl.perbaruiDaftarSMS()
