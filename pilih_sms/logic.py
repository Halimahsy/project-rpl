"""
logic.py
Lapisan ENTITY dan CONTROL aplikasi "Pilah SMS"
(Sistem Klasifikasi Filtering dan Kategorisasi SMS OTP serta Notifikasi
Transaksi Berbasis Naive Bayes).

Nama class, atribut, dan method SENGAJA dibuat sama dengan Class Diagram
(camelCase) supaya mudah ditelusuri ke dokumen:

    ENTITY  : User, OTP, SMS, Kategori
    CONTROL : VerifikasiNomorController, SMSController,
              FilteringController, KategorisasiController, NaiveBayes

Lapisan BOUNDARY (VerifikasiNomorUI, MengelolaSMSUI, KirimSMSUI) ada di main.py.
File ini tidak mengimpor Kivy, jadi bisa diuji sendiri lewat terminal.
"""

import json
import math
import os
import re
import secrets
from collections import Counter
from datetime import datetime, timedelta

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

MASA_BERLAKU_OTP = timedelta(minutes=5)
MAKS_KARAKTER_SMS = 160


# =====================================================================
# DATABASE sederhana (JSON) - pendukung persistensi, bukan bagian diagram
# =====================================================================
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


# =====================================================================
# ENTITY
# =====================================================================
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


# =====================================================================
# CONTROL
# =====================================================================
def normalisasi_nomor(no):
    """'0857-2341-2004' / '+62 857...' / '85723412004' -> '85723412004'
    (nomor tanpa kode negara/nol depan) atau '' jika tidak valid."""
    d = re.sub(r"\D", "", no or "")
    if d.startswith("62"):
        d = d[2:]
    elif d.startswith("0"):
        d = d[1:]
    return d if re.fullmatch(r"8\d{8,11}", d) else ""


def format_nomor(no_lokal):
    d = no_lokal
    return f"+62 {d[:3]}-{d[3:7]}-{d[7:]}"


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


class NaiveBayes:
    """Multinomial Naive Bayes + Laplace smoothing, ditulis manual (tanpa library)."""

    # Data latih kecil (demo). Tambah contoh baru di sini untuk memperbaiki akurasi.
    DATA_LATIH = [
        # --- OTP ---
        ("Kode OTP Anda adalah 583921. Berlaku 5 menit. Jangan berikan kepada siapapun.", "OTP"),
        ("Gunakan kode verifikasi 731842 untuk masuk ke akun Tokopedia Anda.", "OTP"),
        ("JANGAN BAGIKAN kode ini. Kode login Gojek Anda 4471.", "OTP"),
        ("Kode verifikasi Shopee Anda 902716. Demi keamanan jangan beritahu siapa pun.", "OTP"),
        ("Masukkan OTP 318827 untuk konfirmasi transaksi di aplikasi. Berlaku 3 menit.", "OTP"),
        ("Telegram code: 55621. Do not give this code to anyone.", "OTP"),
        ("Your verification code is 620481. Never share this code.", "OTP"),
        ("Kode rahasia untuk reset password akun Anda adalah 774019.", "OTP"),
        ("Gunakan kode 128394 untuk verifikasi nomor handphone Anda di Traveloka.", "OTP"),
        ("PIN sementara Anda 259031, rahasia dan hanya berlaku satu kali.", "OTP"),
        ("Kode autentikasi Instagram 3380 59. Jangan sebarkan kode ini.", "OTP"),
        ("OTP untuk login Dana adalah 847201. Waspada penipuan, jangan bagikan.", "OTP"),
        # --- Transaksi Bank ---
        ("Transfer masuk Rp500.000 dari BUDI S ke rekening Anda. Saldo Rp2.350.000.", "Transaksi Bank"),
        ("Pembayaran Rp125.000 di Alfamart berhasil. Sisa saldo Rp1.874.000.", "Transaksi Bank"),
        ("Debit Rp75.000 kartu 1234 di Tokopedia tanggal 12/11. Saldo Anda berkurang.", "Transaksi Bank"),
        ("Anda menerima dana Rp2.000.000 dari PT Maju Jaya. Cek mutasi rekening.", "Transaksi Bank"),
        ("Transfer keluar Rp350.000 ke rekening 8800123 berhasil dilakukan.", "Transaksi Bank"),
        ("Penarikan tunai ATM Rp1.000.000 berhasil. Saldo akhir Rp4.200.000.", "Transaksi Bank"),
        ("Top up e-wallet Rp100.000 berhasil. Saldo rekening Anda berkurang.", "Transaksi Bank"),
        ("Info mutasi: kredit Rp3.500.000 gaji bulan ini telah masuk rekening.", "Transaksi Bank"),
        ("Pembelian pulsa Rp50.000 melalui mobile banking berhasil, saldo Rp900.000.", "Transaksi Bank"),
        ("Tagihan kartu kredit Rp1.450.000 jatuh tempo 20/11. Segera lakukan pembayaran.", "Transaksi Bank"),
        ("Dana masuk Rp80.000 ke rekening tabungan Anda dari transfer antar bank.", "Transaksi Bank"),
        ("Transaksi QRIS Rp32.000 di Kopi Kenangan sukses. Saldo debit berkurang.", "Transaksi Bank"),
        # --- Lainnya ---
        ("Halo, besok jadi ketemu di kampus jam 10 ya?", "Lainnya"),
        ("Jangan lupa kumpulkan tugas RPL sebelum hari Jumat.", "Lainnya"),
        ("Selamat ulang tahun! Semoga panjang umur dan sehat selalu.", "Lainnya"),
        ("Promo akhir pekan diskon 50 persen semua menu, berlaku sampai Minggu!", "Lainnya"),
        ("Kamu lagi di mana? Aku udah di depan lobi nih.", "Lainnya"),
        ("Rapat kelompok dipindah ke ruang 302 pukul 13.00, mohon hadir.", "Lainnya"),
        ("Paket Anda sedang dalam perjalanan dan akan tiba besok pagi.", "Lainnya"),
        ("Kuota internet Anda tinggal 2 GB. Beli paket tambahan sekarang.", "Lainnya"),
        ("Makasih ya udah bantu kemarin, nanti aku traktir makan.", "Lainnya"),
        ("Jadwal kuliah pengganti hari Rabu jam 8 pagi di gedung B.", "Lainnya"),
        ("Kurs hari ini 1 dolar sama dengan sekitar enam belas ribu rupiah.", "Lainnya"),
        ("Pengingat: servis motor Anda dijadwalkan Sabtu pukul 09.00.", "Lainnya"),
        ("Kurs dolar hari ini Rp16.100 per 1 USD, info nilai tukar terbaru.", "Lainnya"),
        ("Harga emas hari ini Rp1.350.000 per gram, naik dari kemarin.", "Lainnya"),
        ("1 dollar per hari ini adalah Rp15.980,50 menurut kurs tengah.", "Lainnya"),
    ]

    STOPWORD = {"yang", "dan", "di", "ke", "ini", "itu", "dengan", "dari",
                "untuk", "atau", "pada", "ya", "nih", "sih", "the", "to",
                "is", "your", "a", "of"}

    def __init__(self):
        self.modelTersedia = False
        self.dataLatih = list(NaiveBayes.DATA_LATIH)
        self._prior = {}
        self._kata = {}
        self._total_kata = {}
        self._vocab = set()
        self._label_terakhir = "Lainnya"
        self.latih()

    @staticmethod
    def praproses(teks):
        t = teks.lower()
        t = re.sub(r"rp\.?\s?[\d.,]+", " tokrupiah ", t)
        t = re.sub(r"\b\d[\d ]{3,7}\d\b|\b\d{4,8}\b", " tokkode ", t)
        t = re.sub(r"\d+", " tokangka ", t)
        t = re.sub(r"[^a-z\s]", " ", t)
        return [w for w in t.split() if w not in NaiveBayes.STOPWORD and len(w) > 1]

    def latih(self):
        if not self.dataLatih:
            self.modelTersedia = False
            return
        jumlah = Counter(label for _, label in self.dataLatih)
        self._prior = {l: n / len(self.dataLatih) for l, n in jumlah.items()}
        self._kata = {l: Counter() for l in jumlah}
        for teks, label in self.dataLatih:
            self._kata[label].update(self.praproses(teks))
        self._vocab = {w for c in self._kata.values() for w in c}
        self._total_kata = {l: sum(c.values()) for l, c in self._kata.items()}
        self.modelTersedia = True

    def cekModelTersedia(self):
        return self.modelTersedia

    def klasifikasi(self, isiSMS):
        """Return nama kategori dengan log-posterior tertinggi."""
        token = self.praproses(isiSMS)
        V = len(self._vocab)
        skor = {}
        for label, prior in self._prior.items():
            s = math.log(prior)
            for w in token:
                s += math.log((self._kata[label][w] + 1) / (self._total_kata[label] + V))
            skor[label] = s
        self._label_terakhir = max(skor, key=skor.get)
        return self._label_terakhir

    def kategori(self):
        return Kategori.dariNama(self._label_terakhir)


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


# =====================================================================
# Pembungkus: merangkai semua objek (dipakai oleh UI)
# =====================================================================
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


# ---------------------------------------------------------------------
# Data demo
# ---------------------------------------------------------------------
def sms_awal(sekarang=None):
    n = sekarang or datetime.now()
    h = lambda **k: n - timedelta(**k)
    return [
        {"nomorPengirim": "Andi Galon", "isiPesan": "Kamu selingkuh ya!", "waktu": h(days=1, hours=1)},
        {"nomorPengirim": "+62 812-9090-2211", "isiPesan": "$1 per hari ini adalah Rp18.254,85", "waktu": h(minutes=40)},
        {"nomorPengirim": "WhatsApp", "isiPesan": "Kode verifikasi WhatsApp Anda: 482901. Jangan bagikan kode ini kepada siapa pun.", "waktu": h(minutes=22)},
        {"nomorPengirim": "BCA", "isiPesan": "Transfer masuk Rp1.250.000 dari ANDI P. ke rekening Anda. Saldo tersedia.", "waktu": h(minutes=10)},
    ]


SMS_DEMO_MASUK = [
    ("Mandiri", "Pembayaran Rp85.000 di Indomaret berhasil. Saldo Anda berkurang."),
    ("Gojek", "Kode OTP Gojek Anda 6120. Jangan berikan kode ini ke siapa pun."),
    ("BNI", "Transfer masuk Rp300.000 dari SITI R. Cek mutasi rekening Anda."),
    ("Tokopedia", "Gunakan kode verifikasi 905431 untuk login. Berlaku 5 menit."),
    ("Rina", "Besok kita belajar bareng di perpus jam 3 ya"),
    ("BRI", "Debit Rp42.500 di Starbucks berhasil. Sisa saldo Rp1.120.000."),
    ("Telkomsel", "Kuota Anda hampir habis, beli paket data tambahan sekarang."),
]
