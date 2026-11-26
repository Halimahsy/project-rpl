[app]
title = Pilah SMS
package.name = pilahsms
package.domain = org.rpl.kelompok6
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy==2.3.0,plyer,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = SEND_SMS,READ_SMS,RECEIVE_SMS
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
