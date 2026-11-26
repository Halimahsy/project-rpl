"""
user.py - ENTITY/aktor User (meneruskan pekerjaan ke controller).
"""




class User:
    """Aktor. Method-nya meneruskan pekerjaan ke controller terkait."""

    def __init__(self, db, verifikasiCtrl, smsCtrl):
        self._db = db
        self._vc = verifikasiCtrl
        self._sc = smsCtrl

    @property
    def idUser(self):
        return self._db.data["user"]["idUser"]

    @property
    def nomorTelepon(self):
        return self._db.data["user"]["nomorTelepon"]

    @property
    def statusVerifikasi(self):
        return self._db.data["user"]["statusVerifikasi"]

    def verifikasiNomor(self, no):
        return self._vc.verifikasiNomor(no)

    def bacaSMS(self, id=None):
        return self._sc.getSMS() if id is None else self._sc.getDetailSMS(id)

    def kirimSMS(self, nomor, isi):
        return self._sc.kirimSMS(nomor, isi)

    def hapusSMS(self, id):
        return self._sc.hapusSMS(id)
