"""
sms.py - ENTITY SMS.
"""

from datetime import datetime


class SMS:
    def __init__(self, db, idSMS, nomorPengirim, nomorTujuan, isiPesan, waktu,
                 jenis="masuk", status="baru", idKategori=None):
        self._db = db
        self.idSMS = idSMS
        self.nomorPengirim = nomorPengirim
        self.nomorTujuan = nomorTujuan
        self.isiPesan = isiPesan
        self.waktu = waktu                  # datetime
        self.jenis = jenis                  # "masuk" | "keluar"
        self.status = status                # "baru" | "dibaca" | "terkirim" | "gagal"
        self.idKategori = idKategori        # int | None (belum dikategorikan)

    # --- (de)serialisasi ---
    def _ke_dict(self):
        return {"idSMS": self.idSMS, "nomorPengirim": self.nomorPengirim,
                "nomorTujuan": self.nomorTujuan, "isiPesan": self.isiPesan,
                "waktu": self.waktu.isoformat(), "jenis": self.jenis,
                "status": self.status, "idKategori": self.idKategori}

    @classmethod
    def _dari_dict(cls, db, d):
        return cls(db, d["idSMS"], d["nomorPengirim"], d["nomorTujuan"],
                   d["isiPesan"], datetime.fromisoformat(d["waktu"]),
                   d["jenis"], d["status"], d["idKategori"])

    # --- method pada Class Diagram ---
    def getDataSMS(self):
        return self._ke_dict()

    @classmethod
    def getDetail(cls, db, id):
        for d in db.data["sms"]:
            if d["idSMS"] == id:
                return cls._dari_dict(db, d)
        return None

    def getIsiSMS(self):
        return self.isiPesan

    def simpan(self):
        daftar = self._db.data["sms"]
        for i, d in enumerate(daftar):
            if d["idSMS"] == self.idSMS:
                daftar[i] = self._ke_dict()
                break
        else:
            daftar.append(self._ke_dict())
        self._db.simpan()

    def simpanLabel(self, label):
        self.idKategori = label
        self.simpan()

    def hapus(self):
        self._db.data["sms"] = [d for d in self._db.data["sms"]
                                if d["idSMS"] != self.idSMS]
        self._db.simpan()

    # --- bantuan tampilan ---
    @property
    def kontak(self):
        return self.nomorPengirim if self.jenis == "masuk" else self.nomorTujuan
