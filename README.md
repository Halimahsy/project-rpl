# Pilah SMS

Struktur (satu class = satu file):

    main.py                      program utama (UI Kivy / boundary)
    entity/   kategori.py  sms.py  otp.py  user.py
    control/  login.py (VerifikasiNomorController)
              kelola_sms.py (SMSController)
              filtering_sms.py (FilteringController)
              kategorisasi_sms.py (KategorisasiController)
              naive_bayes.py (NaiveBayes)
    core/     sistem.py  database.py  utils.py  konstanta.py  data_demo.py

Contoh memanggil dari program utama / terminal:

    from core.sistem import Sistem
    s = Sistem("data.json")
    otp = s.verifikasiCtrl.kirimOTP("85723412004")      # control/login.py
    s.smsCtrl.terimaSMS({"nomorPengirim": "BCA", "isiPesan": "Transfer masuk Rp1.000"})
    s.smsCtrl.getSMS()                                  # control/kelola_sms.py

Jalankan: `python main.py`   |   APK: `buildozer android debug`
