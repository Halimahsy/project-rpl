"""
data_demo.py - data contoh untuk demo (SMS awal & SMS simulasi masuk).
"""

from datetime import datetime, timedelta


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
