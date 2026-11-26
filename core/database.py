"""
database.py - penyimpanan JSON sederhana (pendukung, bukan bagian class diagram).
"""

import json
import os


class Database:
    def __init__(self, path):
        self.path = path
        self.data = {"user": {"idUser": 1, "nomorTelepon": "",
                              "statusVerifikasi": False},
                     "pengaturan": {"klasifikasiOtomatis": True},
                     "sms": [], "otp": [], "nextId": 1}
        self._muat()

    def _muat(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except (OSError, ValueError):
                pass  # file rusak -> mulai dari data kosong

    def simpan(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=1)
        except OSError:
            pass

    def id_baru(self):
        i = self.data["nextId"]
        self.data["nextId"] += 1
        return i
