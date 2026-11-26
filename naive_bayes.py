"""
naive_bayes.py - CONTROL NaiveBayes (multinomial + Laplace smoothing).
"""

import math
import re
from collections import Counter

from entity.kategori import Kategori


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
