import random
import re
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ColorProperty, NumericProperty,
                             StringProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex as C
from kivy.utils import platform

from logic import (BULAN, HARI, MAKS_KARAKTER_SMS, SMS_DEMO_MASUK, Kategori,
                   Sistem, format_nomor, sms_awal)

# ------------------------------------------------------------------ palet
BG = "#F5F8F4"
DARK = "#1B4D3E"
LIME = "#DCF77C"
INK = "#1E2B25"
MUTED = "#6B7A72"
SOFT = "#E6EDE7"
LINE = "#E1E9E3"
PURPLE_BG = "#E7E0F5"
PURPLE = "#6F4FB0"
RED = "#C0504D"

if platform not in ("android", "ios"):
    Window.size = (360, 780)          # pratinjau ukuran HP di desktop
else:
    Window.softinput_mode = "below_target"
Window.clearcolor = C(BG)


# ------------------------------------------------------------------ widget dasar
class Txt(Label):
    pass


class Card(BoxLayout):
    bg = ColorProperty([0, 0, 0, 0])
    border = ColorProperty([0, 0, 0, 0])
    radius = NumericProperty(dp(16))


class CardBtn(ButtonBehavior, Card):
    pass


class Btn(ButtonBehavior, Label):
    bg = ColorProperty(C(DARK))
    fg = ColorProperty([1, 1, 1, 1])
    border = ColorProperty([0, 0, 0, 0])
    radius = NumericProperty(dp(14))


class Chip(ButtonBehavior, Card):
    text = StringProperty("")
    fg = ColorProperty(C(DARK))


class Field(TextInput):
    pass


class Dot(BoxLayout):
    pass


class AreaField(TextInput):
    """Kolom teks multi-baris (isi pesan)."""


class Toggle(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)

    def on_release(self):
        self.active = not self.active


class SMSItem(ButtonBehavior, BoxLayout):
    sender = StringProperty("")
    preview = StringProperty("")
    waktu = StringProperty("")
    kategori = StringProperty("")
    unread = BooleanProperty(False)
    av_text = StringProperty("")
    av_bg = ColorProperty(C(SOFT))
    av_fg = ColorProperty(C(DARK))
    chip_bg = ColorProperty(C(SOFT))
    chip_fg = ColorProperty(C(DARK))


class CountCard(Card):
    label = StringProperty("")
    jumlah = StringProperty("00")
    fg = ColorProperty(C(DARK))


class Bubble(Card):
    text = StringProperty("")
    waktu = StringProperty("")
    maxw = NumericProperty(dp(260))
    fg = ColorProperty(C(INK))


class NavItem(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    active = BooleanProperty(False)


class NavPlus(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)


class BottomNav(BoxLayout):
    active = StringProperty("home")


Builder.load_string("""
#:import dp kivy.metrics.dp
#:import sp kivy.metrics.sp
#:import C kivy.utils.get_color_from_hex
#:set BG '""" + BG + """'
#:set DARK '""" + DARK + """'
#:set LIME '""" + LIME + """'
#:set INK '""" + INK + """'
#:set MUTED '""" + MUTED + """'
#:set SOFT '""" + SOFT + """'
#:set LINE '""" + LINE + """'
#:set PURPLE '""" + PURPLE + """'
#:set RED '""" + RED + """'

<Txt>:
    color: C(INK)
    halign: 'left'
    valign: 'middle'
    font_size: sp(14)
    text_size: self.width, None
    size_hint_y: None
    height: self.texture_size[1]

<Card>:
    canvas.before:
        Color:
            rgba: self.bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius]
        Color:
            rgba: self.border
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, self.radius
            width: 1

<Btn>:
    size_hint_y: None
    height: dp(52)
    bold: True
    font_size: sp(15)
    opacity: .85 if self.state == 'down' else 1
    color: self.fg
    disabled_color: C(MUTED) if self.bg[3] == 0 else C('#8FA096')
    canvas.before:
        Color:
            rgba: self.bg if (not self.disabled or self.bg[3] == 0) else C('#DCE5DE')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius]
        Color:
            rgba: self.border
        Line:
            rounded_rectangle: self.x, self.y, self.width, self.height, self.radius
            width: 1

<Chip>:
    size_hint: None, None
    height: dp(24)
    width: lbl.texture_size[0] + dp(22)
    radius: dp(8)
    Label:
        id: lbl
        text: root.text
        color: root.fg
        font_size: sp(11)

<Field>:
    background_normal: ''
    background_active: ''
    background_color: 0, 0, 0, 0
    foreground_color: C(INK)
    hint_text_color: C(MUTED)
    cursor_color: C(DARK)
    font_size: sp(15)
    write_tab: False
    multiline: False
    padding: [dp(14), max(0, (self.height - self.line_height) / 2.0), dp(14), 0]

<AreaField>:
    background_normal: ''
    background_active: ''
    background_color: 0, 0, 0, 0
    foreground_color: C(INK)
    hint_text_color: C(MUTED)
    cursor_color: C(DARK)
    font_size: sp(15)
    write_tab: False
    multiline: True
    padding: dp(14), dp(14), dp(14), dp(6)

<Toggle>:
    size_hint: None, None
    size: dp(52), dp(30)
    canvas:
        Color:
            rgba: C(DARK) if self.active else C('#C9D3CC')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15)]
        Color:
            rgba: 1, 1, 1, 1
        Ellipse:
            pos: (self.right - dp(27), self.y + dp(3)) if self.active else (self.x + dp(3), self.y + dp(3))
            size: dp(24), dp(24)

<Dot>:
    size_hint: None, None
    size: dp(8), dp(8)
    canvas:
        Color:
            rgba: C(DARK)
        Ellipse:
            pos: self.pos
            size: self.size

<SMSItem>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(88) if root.kategori else dp(66)
    spacing: dp(12)
    padding: 0, dp(8)
    canvas.after:
        Color:
            rgba: C(LINE)
        Line:
            points: self.x, self.y, self.right, self.y
            width: 1
    Card:
        size_hint: None, None
        size: dp(42), dp(42)
        radius: dp(12)
        bg: root.av_bg
        Label:
            text: root.av_text
            color: root.av_fg
            bold: True
            font_size: sp(16)
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(2)
        BoxLayout:
            size_hint_y: None
            height: dp(22)
            Label:
                text: root.sender
                bold: True
                color: C(INK)
                font_size: sp(15)
                halign: 'left'
                text_size: self.size
                valign: 'middle'
                shorten: True
                shorten_from: 'right'
            Label:
                text: root.waktu
                color: C(MUTED)
                font_size: sp(11)
                size_hint_x: None
                width: dp(46)
                halign: 'right'
                valign: 'middle'
                text_size: self.size
        Label:
            text: root.preview
            color: C(MUTED)
            font_size: sp(13)
            size_hint_y: None
            height: dp(20)
            halign: 'left'
            valign: 'middle'
            text_size: self.size
            shorten: True
            shorten_from: 'right'
        BoxLayout:
            size_hint_y: None
            height: dp(26) if root.kategori else 0
            opacity: 1 if root.kategori else 0
            Chip:
                text: root.kategori
                bg: root.chip_bg
                fg: root.chip_fg
            Widget:
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: None
        width: dp(8)
        Widget:
        Dot:
            opacity: 1 if root.unread else 0
        Widget:
            size_hint_y: None
            height: dp(6)

<CountCard>:
    orientation: 'vertical'
    padding: dp(14)
    Label:
        text: root.jumlah
        color: root.fg
        bold: True
        font_size: sp(28)
        halign: 'right'
        valign: 'top'
        text_size: self.size
    Label:
        text: root.label
        color: root.fg
        bold: True
        font_size: sp(14)
        halign: 'left'
        valign: 'bottom'
        text_size: self.size

<Bubble>:
    size_hint: None, None
    orientation: 'vertical'
    spacing: dp(4)
    padding: dp(14), dp(10)
    radius: dp(16)
    width: max(msg.texture_size[0], dp(46)) + dp(28)
    height: msg.texture_size[1] + dp(14) + dp(24)
    Label:
        id: msg
        text: root.text
        color: root.fg
        font_size: sp(15)
        size_hint: None, None
        size: self.texture_size
        text_size: root.maxw - dp(28), None
        halign: 'left'
    Label:
        text: root.waktu
        color: C(MUTED)
        font_size: sp(10)
        size_hint_y: None
        height: dp(14)
        halign: 'right'
        text_size: self.size

<NavItem>:
    orientation: 'vertical'
    padding: 0, dp(8), 0, dp(6)
    Widget:
        size_hint: None, None
        size: dp(24), dp(3)
        pos_hint: {'center_x': .5}
        canvas:
            Color:
                rgba: C(DARK) if root.active else (0, 0, 0, 0)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(2)]
    Label:
        text: root.text
        bold: root.active
        font_size: sp(13)
        color: C(DARK) if root.active else C(MUTED)

<NavPlus>:
    orientation: 'vertical'
    padding: 0, dp(2), 0, dp(4)
    Card:
        size_hint: None, None
        size: dp(46), dp(46)
        pos_hint: {'center_x': .5}
        radius: dp(15)
        bg: C(DARK) if root.active else C(LIME)
        Label:
            text: '+'
            font_size: sp(30)
            color: C(LIME) if root.active else C(DARK)
    Label:
        text: 'Kirim SMS'
        font_size: sp(11)
        size_hint_y: None
        height: dp(16)
        bold: True
        color: C(DARK) if root.active else C(MUTED)

<BottomNav>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(80)
    padding: dp(8), 0
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: C(LINE)
        Line:
            points: self.x, self.top, self.right, self.top
            width: 1
    NavItem:
        text: 'Home'
        active: root.active == 'home'
        on_release: app.goto('beranda')
    NavPlus:
        active: root.active == 'kirim'
        on_release: app.goto('kirim')
    NavItem:
        text: 'Akun'
        active: root.active == 'akun'
        on_release: app.goto('akun')


# ====================================================== VERIFIKASI NOMOR
<VerifNomorScreen>:
    name: 'verif_nomor'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24), dp(36), dp(24), dp(20)
        spacing: dp(12)
        Txt:
            text: 'AKUN'
            color: C(MUTED)
            font_size: sp(11)
        Txt:
            text: 'Verifikasi nomor'
            font_size: sp(30)
            bold: True
            color: C(DARK)
        BoxLayout:
            size_hint_y: None
            height: dp(24)
            Chip:
                text: 'Belum terverifikasi'
                bg: C('#FCEBD0')
                fg: C('#B7791F')
            Widget:
        Card:
            orientation: 'vertical'
            padding: dp(20)
            bg: C(SOFT)
            radius: dp(22)
            Card:
                size_hint: None, None
                size: dp(56), dp(56)
                radius: dp(16)
                bg: C(LIME)
                Label:
                    text: 'SMS'
                    bold: True
                    color: C(DARK)
            Widget:
            Txt:
                text: 'Verifikasi dulu sebelum mulai ya..'
                font_size: sp(22)
                bold: True
                color: C(DARK)
        Txt:
            text: 'Verifikasi untuk mengaktifkan akun dan memastikan nomor ini milikmu.'
            color: C(MUTED)
            font_size: sp(13)
        Txt:
            text: 'Nomor handphone'
            bold: True
        Card:
            size_hint_y: None
            height: dp(52)
            bg: 1, 1, 1, 1
            border: C(LINE)
            radius: dp(14)
            Label:
                text: '+62'
                color: C(INK)
                size_hint_x: None
                width: dp(62)
            Field:
                id: no
                hint_text: '857-2341-2004'
                input_filter: lambda text, undo: ''.join(ch for ch in text if ch.isdigit() or ch == '-')
                input_type: 'number'
                padding: [dp(8), max(0, (self.height - self.line_height) / 2.0), dp(14), 0]
        Txt:
            text: 'Nomor hanya digunakan untuk verifikasi. Isi SMS tetap privat di perangkatmu.'
            color: C(MUTED)
            font_size: sp(12)
        Txt:
            text: 'Dengan melanjutkan, kamu menyetujui Syarat Layanan dan Kebijakan Privasi.'
            color: C(MUTED)
            font_size: sp(11)
        Btn:
            text: 'Kirim kode verifikasi'
            on_release: root.kirim()


<VerifOtpScreen>:
    name: 'verif_otp'
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24), dp(24), dp(24), dp(20)
        spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(36)
            Btn:
                text: '<'
                size_hint: None, None
                size: dp(36), dp(36)
                font_size: sp(22)
                bg: 0, 0, 0, 0
                fg: C(DARK)
                on_release: app.goto('verif_nomor')
            Txt:
                text: 'VERIFIKASI NOMOR'
                color: C(MUTED)
                font_size: sp(11)
                size_hint_y: 1
                padding: dp(8), 0
        Txt:
            text: 'Masukkan kode'
            font_size: sp(30)
            bold: True
            color: C(DARK)
        Txt:
            text: 'Kode 6 digit telah dikirim melalui SMS ke'
            color: C(MUTED)
            font_size: sp(13)
        BoxLayout:
            size_hint_y: None
            height: dp(28)
            Txt:
                id: lbl_no
                bold: True
                size_hint_y: 1
                valign: 'middle'
                text_size: self.size
            Btn:
                text: 'Ubah'
                size_hint: None, 1
                width: dp(56)
                font_size: sp(13)
                bg: 0, 0, 0, 0
                fg: C(DARK)
                on_release: app.goto('verif_nomor')
        BoxLayout:
            id: kotak
            size_hint_y: None
            height: dp(56)
            spacing: dp(10)
        BoxLayout:
            size_hint_y: None
            height: dp(26)
            Txt:
                text: 'Belum menerima kode?'
                color: C(MUTED)
                font_size: sp(12)
                size_hint_y: 1
                valign: 'middle'
                text_size: self.size
            Btn:
                id: btn_ulang
                text: 'Kirim ulang'
                size_hint: None, 1
                width: dp(130)
                font_size: sp(12)
                bg: 0, 0, 0, 0
                fg: C(DARK)
                on_release: root.kirim_ulang()
        Card:
            size_hint_y: None
            height: dp(40)
            bg: C(SOFT)
            radius: dp(10)
            padding: dp(12), 0
            Txt:
                text: 'Jangan bagikan kode ini kepada siapa pun.'
                font_size: sp(12)
                color: C(DARK)
                size_hint_y: 1
                valign: 'middle'
                text_size: self.size
        Txt:
            id: demo
            font_size: sp(12)
            bold: True
            color: C('#B7791F')
        GridLayout:
            id: keypad
            cols: 3
            spacing: dp(10)
        Btn:
            id: btn_ok
            text: 'Verifikasi nomor'
            disabled: True
            on_release: root.verifikasi()


# ====================================================== BERANDA (Mengelola SMS)
<BerandaScreen>:
    name: 'beranda'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(20), dp(28), dp(20), dp(6)
            spacing: dp(12)
            BoxLayout:
                size_hint_y: None
                height: dp(62)
                BoxLayout:
                    orientation: 'vertical'
                    Txt:
                        id: tgl
                        color: C(MUTED)
                        font_size: sp(11)
                    Txt:
                        text: 'Pesan masuk'
                        font_size: sp(30)
                        bold: True
                        color: C(DARK)
                Btn:
                    text: '...'
                    size_hint: None, None
                    size: dp(40), dp(40)
                    pos_hint: {'center_y': .5}
                    radius: dp(20)
                    bg: C(SOFT)
                    fg: C(DARK)
                    on_release: root.buka_menu()
            Card:
                size_hint_y: None
                height: dp(46)
                bg: C(SOFT)
                radius: dp(14)
                padding: dp(4)
                spacing: dp(4)
                Btn:
                    id: tab_semua
                    text: 'Semua SMS'
                    size_hint_y: 1
                    radius: dp(11)
                    on_release: root.set_tab('semua')
                Btn:
                    id: tab_kat
                    text: 'Kategori'
                    size_hint_y: 1
                    radius: dp(11)
                    on_release: root.set_tab('kategori')
            Card:
                size_hint_y: None
                height: dp(46)
                bg: 1, 1, 1, 1
                border: C(LINE)
                radius: dp(14)
                Field:
                    id: cari
                    hint_text: 'Cari pesan atau pengirim'
                    on_text: root.refresh()
        ScrollView:
            do_scroll_x: False
            bar_width: 0
            BoxLayout:
                id: daftar
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(20), dp(8), dp(20), dp(12)
                spacing: dp(0)
        BottomNav:
            active: 'home'


# ====================================================== DETAIL SMS
<DetailScreen>:
    name: 'detail'
    BoxLayout:
        orientation: 'vertical'
        Card:
            size_hint_y: None
            height: dp(64)
            bg: 1, 1, 1, 1
            radius: 0
            padding: dp(8), dp(8)
            spacing: dp(4)
            Btn:
                text: '<'
                size_hint: None, None
                size: dp(44), dp(48)
                font_size: sp(24)
                bg: 0, 0, 0, 0
                fg: C(DARK)
                on_release: root.kembali()
            BoxLayout:
                orientation: 'vertical'
                padding: dp(4), dp(4)
                Label:
                    id: judul
                    bold: True
                    font_size: sp(17)
                    color: C(INK)
                    halign: 'left'
                    valign: 'bottom'
                    text_size: self.size
                    shorten: True
                Label:
                    id: sub
                    font_size: sp(12)
                    color: C(MUTED)
                    halign: 'left'
                    valign: 'top'
                    text_size: self.size
            Btn:
                text: '...'
                size_hint: None, None
                size: dp(44), dp(48)
                bg: 0, 0, 0, 0
                fg: C(DARK)
                on_release: root.menu()
        ScrollView:
            id: sv
            do_scroll_x: False
            bar_width: 0
            BoxLayout:
                id: thread
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16), dp(16)
                spacing: dp(8)
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(16), dp(6), dp(16), dp(10)
            spacing: dp(8)
            Txt:
                text: 'Informasi klasifikasi'
                font_size: sp(11)
                color: C(MUTED)
            BoxLayout:
                size_hint_y: None
                height: dp(34)
                spacing: dp(8)
                Chip:
                    id: chip_salin
                    text: 'Salin kode OTP'
                    height: dp(34)
                    bg: 1, 1, 1, 1
                    border: C(LINE)
                    on_release: root.salin_kode()
                Chip:
                    text: 'Lihat kategori lainnya'
                    height: dp(34)
                    bg: 1, 1, 1, 1
                    border: C(LINE)
                    on_release: root.lihat_kategori()
                Widget:
            Card:
                size_hint_y: None
                height: dp(54)
                bg: 1, 1, 1, 1
                border: C(LINE)
                radius: dp(14)
                padding: 0, dp(7), dp(8), dp(7)
                Field:
                    id: balas
                    hint_text: 'Isi pesan SMS'
                Btn:
                    text: '>'
                    size_hint: None, 1
                    width: dp(42)
                    radius: dp(12)
                    font_size: sp(18)
                    on_release: root.balas()
            Txt:
                id: status
                font_size: sp(11)
                color: C(MUTED)
                halign: 'center'
        
        
# ====================================================== KIRIM SMS
<KirimScreen>:
    name: 'kirim'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'vertical'
            padding: dp(24), dp(36), dp(24), dp(14)
            spacing: dp(10)
            Txt:
                text: 'PESAN BARU'
                color: C(MUTED)
                font_size: sp(11)
            Txt:
                text: 'Kirim pesan'
                font_size: sp(30)
                bold: True
                color: C(DARK)
            Txt:
                text: 'Tulis SMS untuk orang yang kamu tuju.'
                color: C(MUTED)
                font_size: sp(13)
            Txt:
                text: 'Penerima'
                bold: True
            Card:
                size_hint_y: None
                height: dp(52)
                bg: 1, 1, 1, 1
                border: C(LINE)
                radius: dp(14)
                Field:
                    id: tujuan
                    hint_text: 'Nomor tujuan, mis. 0812-3456-7890'
                    input_type: 'number'
                    input_filter: lambda text, undo: ''.join(ch for ch in text if ch.isdigit() or ch in '+-')
            Txt:
                text: 'Masukkan nomor telepon tujuan.'
                color: C(MUTED)
                font_size: sp(11)
            Txt:
                text: 'Isi pesan'
                bold: True
            Card:
                orientation: 'vertical'
                bg: 1, 1, 1, 1
                border: C(LINE)
                radius: dp(14)
                AreaField:
                    id: isi
                    hint_text: 'Tuliskan pesan....'
                    on_text: root.hitung()
                BoxLayout:
                    size_hint_y: None
                    height: dp(34)
                    padding: dp(14), 0, dp(6), 0
                    Txt:
                        id: hitung
                        text: '0/160 karakter'
                        font_size: sp(11)
                        color: C(MUTED)
                        size_hint_y: 1
                        valign: 'middle'
                        text_size: self.size
                    Btn:
                        text: 'Hapus'
                        size_hint: None, 1
                        width: dp(60)
                        font_size: sp(12)
                        bg: 0, 0, 0, 0
                        fg: C(RED)
                        on_release: root.ids.isi.text = ''
            Btn:
                text: 'Kirim pesan'
                on_release: root.kirim()
            Txt:
                text: 'SMS  -  Tarif operator berlaku'
                font_size: sp(11)
                color: C(MUTED)
                halign: 'center'
        BottomNav:
            active: 'kirim'


# ====================================================== AKUN
<AkunScreen>:
    name: 'akun'
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            do_scroll_x: False
            bar_width: 0
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(24), dp(36), dp(24), dp(16)
                spacing: dp(14)
                Txt:
                    text: 'PENGATURAN'
                    color: C(MUTED)
                    font_size: sp(11)
                Txt:
                    text: 'Profil Pengguna'
                    font_size: sp(30)
                    bold: True
                    color: C(DARK)
                Card:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(156)
                    padding: dp(18)
                    spacing: dp(4)
                    bg: C(DARK)
                    radius: dp(22)
                    Txt:
                        text: 'Nomor terdaftar'
                        color: C('#A9C9B8')
                        font_size: sp(12)
                    Txt:
                        id: nomor
                        color: 1, 1, 1, 1
                        font_size: sp(24)
                        bold: True
                    Widget:
                    BoxLayout:
                        size_hint_y: None
                        height: dp(34)
                        Chip:
                            text: 'Akun aktif'
                            height: dp(28)
                            bg: C('#2F6B58')
                            fg: 1, 1, 1, 1
                            pos_hint: {'center_y': .5}
                        Widget:
                        Btn:
                            text: 'Ubah nomor'
                            size_hint: None, 1
                            width: dp(110)
                            font_size: sp(13)
                            bg: 0, 0, 0, 0
                            fg: 1, 1, 1, 1
                            on_release: root.ubah_nomor()
                Txt:
                    text: 'PENGATURAN SISTEM'
                    color: C(MUTED)
                    font_size: sp(11)
                Card:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(210)
                    padding: dp(16), dp(6)
                    bg: 1, 1, 1, 1
                    border: C(LINE)
                    radius: dp(18)
                    BoxLayout:
                        spacing: dp(8)
                        BoxLayout:
                            orientation: 'vertical'
                            padding: 0, dp(12)
                            spacing: dp(2)
                            Txt:
                                text: 'Klasifikasi otomatis'
                                bold: True
                            Txt:
                                text: 'OTP & NON-OTP'
                                font_size: sp(12)
                                color: C(MUTED)
                        Toggle:
                            id: sw
                            pos_hint: {'center_y': .5}
                            on_active: root.ubah_klasifikasi(self.active)
                    CardBtn:
                        padding: 0, dp(12)
                        on_release: app.toast('Fitur ini belum tersedia di versi simpel.')
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: dp(2)
                            Txt:
                                text: 'Notifikasi SMS'
                                bold: True
                            Txt:
                                text: 'Atur pemberitahuan'
                                font_size: sp(12)
                                color: C(MUTED)
                        Txt:
                            text: '>'
                            size_hint: None, 1
                            width: dp(16)
                            valign: 'middle'
                            text_size: self.size
                            color: C(MUTED)
                    CardBtn:
                        padding: 0, dp(12)
                        on_release: app.toast('Fitur ini belum tersedia di versi simpel.')
                        BoxLayout:
                            orientation: 'vertical'
                            spacing: dp(2)
                            Txt:
                                text: 'Privasi & keamanan'
                                bold: True
                            Txt:
                                text: 'Kelola akses SMS'
                                font_size: sp(12)
                                color: C(MUTED)
                        Txt:
                            text: '>'
                            size_hint: None, 1
                            width: dp(16)
                            valign: 'middle'
                            text_size: self.size
                            color: C(MUTED)
                CardBtn:
                    size_hint_y: None
                    height: dp(56)
                    padding: dp(16), 0
                    bg: 1, 1, 1, 1
                    border: C(LINE)
                    radius: dp(18)
                    on_release: app.toast('Fitur ini belum tersedia di versi simpel.')
                    Txt:
                        text: 'Bantuan dan panduan'
                        bold: True
                        size_hint_y: 1
                        valign: 'middle'
                        text_size: self.size
                    Txt:
                        text: '>'
                        size_hint: None, 1
                        width: dp(16)
                        valign: 'middle'
                        text_size: self.size
                        color: C(MUTED)
                Btn:
                    text: 'Keluar akun'
                    bg: C('#FBF1F0')
                    fg: C(RED)
                    border: C('#E4B3B1')
                    on_release: root.keluar()
                Txt:
                    text: 'Pilah SMS  -  Versi 1.0.0'
                    font_size: sp(11)
                    color: C(MUTED)
                    halign: 'center'
        BottomNav:
            active: 'akun'
""")


# ====================================================== helper umum
def app():
    return App.get_running_app()


def fmt_jam(dt):
    return dt.strftime("%H.%M")


def label_hari(dt):
    sel = (datetime.now().date() - dt.date()).days
    if sel == 0:
        return "HARI INI"
    if sel == 1:
        return "KEMARIN"
    return f"{dt.day} {BULAN[dt.month - 1].upper()}"


def cari_kode(teks):
    m = re.search(r"(?<!\d)\d{4,8}(?!\d)", teks or "")
    return m.group(0) if m else ""


def gaya_kategori(idk):
    """-> (nama chip, bg chip, fg chip, bg avatar, fg avatar)"""
    if idk == Kategori.OTP:
        return "OTP", C(PURPLE_BG), C(PURPLE), C(PURPLE_BG), C(PURPLE)
    if idk == Kategori.TRANSAKSI:
        return "Transaksi bank", C(SOFT), C(DARK), C(SOFT), C(DARK)
    return "", C(SOFT), C(MUTED), C("#EAEFEB"), C(MUTED)


# ====================================================== SCREENS
class VerifNomorScreen(Screen):                      # VerifikasiNomorUI (1/2)
    def kirim(self):
        a = app()
        otp = a.sistem.user.verifikasiNomor(self.ids.no.text)   # masukkanNomor / mintaInputOTP
        if otp is None:                                        # A1: format salah
            a.toast("Format nomor tidak sesuai. Contoh: 857-2341-2004")
            return
        a.goto("verif_otp")


class VerifOtpScreen(Screen):                        # VerifikasiNomorUI (2/2)
    kode = StringProperty("")
    detik = NumericProperty(0)

    def on_kv_post(self, base):
        self.kotak = []
        for _ in range(6):
            c = Card(bg=[1, 1, 1, 1], border=C(LINE), radius=dp(12))
            c.add_widget(Label(text="", font_size="24sp", bold=True, color=C(DARK)))
            self.ids.kotak.add_widget(c)
            self.kotak.append(c)
        for k in "123456789C0<":
            self.ids.keypad.add_widget(Btn(
                text="Del" if k == "<" else k, size_hint_y=1, bold=False,
                font_size="22sp", radius=dp(12), bg=C("#EDF2EE"), fg=C(DARK),
                on_release=lambda b, k=k: self.tekan(k)))
        self._timer = None

    def on_pre_enter(self, *a):
        v = app().sistem.verifikasiCtrl
        self.ids.lbl_no.text = format_nomor(v.nomorTelepon)
        self.kode = ""
        self._tampilkan_demo()
        self._mulai_timer()
        self._gambar()

    def on_leave(self, *a):
        if self._timer:
            self._timer.cancel()

    def _tampilkan_demo(self):
        otp = app().sistem.verifikasiCtrl.otpAktif
        # MODE DEMO: tidak ada gateway SMS, jadi kode ditampilkan di layar.
        self.ids.demo.text = f"MODE DEMO - kode OTP Anda: {otp.kodeOTP}"

    def _mulai_timer(self):
        if self._timer:
            self._timer.cancel()
        self.detik = 30
        self._timer = Clock.schedule_interval(self._tick, 1)
        self._label_ulang()

    def _tick(self, dt):
        self.detik = max(0, self.detik - 1)
        self._label_ulang()
        if self.detik == 0:
            self._timer.cancel()

    def _label_ulang(self):
        b = self.ids.btn_ulang
        if self.detik > 0:
            b.text = f"Kirim ulang (00:{self.detik:02d})"
            b.disabled = True
        else:
            b.text = "Kirim ulang"
            b.disabled = False

    def kirim_ulang(self):
        app().sistem.verifikasiCtrl.mintaKirimUlangOTP()
        self.kode = ""
        self._tampilkan_demo()
        self._mulai_timer()
        self._gambar()
        app().toast("Kode verifikasi baru telah dikirim.")

    def tekan(self, k):
        if k == "C":
            self.kode = ""
        elif k == "<":
            self.kode = self.kode[:-1]
        elif len(self.kode) < 6:
            self.kode += k
        self._gambar()

    def _gambar(self):
        for i, c in enumerate(self.kotak):
            c.children[0].text = self.kode[i] if i < len(self.kode) else ""
            c.border = C(DARK) if i == len(self.kode) else C(LINE)
        self.ids.btn_ok.disabled = len(self.kode) != 6

    def verifikasi(self):
        a = app()
        hasil = a.sistem.verifikasiCtrl.verifikasiOTP(self.kode)
        if hasil == "berhasil":
            if not a.sistem.db.data["sms"]:                    # data contoh pertama kali
                for d in sms_awal():
                    a.sistem.smsCtrl.terimaSMS(d)
            a.toast("Nomor berhasil diverifikasi.")
            a.goto("beranda")
            return
        if hasil == "kedaluwarsa":                             # A3
            a.toast("Kode sudah tidak berlaku. Silakan kirim ulang.")
        else:                                                  # A2
            a.toast("Kode yang dimasukkan salah.")
        self.kode = ""
        self._gambar()


class BerandaScreen(Screen):                         # MengelolaSMSUI
    tab = StringProperty("semua")
    filter_kat = StringProperty("Semua")

    def on_pre_enter(self, *a):
        self.refresh()

    def set_tab(self, t):
        self.tab = t
        self.refresh()

    def buka_menu(self):
        app().dialog(
            "Mode demo",
            "Tambahkan satu SMS masuk simulasi untuk mencoba filtering dan "
            "kategorisasi otomatis.",
            "Simulasikan", self._simulasi, "Tutup")

    def _simulasi(self):
        a = app()
        pengirim, isi = random.choice(SMS_DEMO_MASUK)
        sms = a.sistem.smsCtrl.terimaSMS({"nomorPengirim": pengirim, "isiPesan": isi})
        kat = Kategori(sms.idKategori).getNama() if sms.idKategori else "belum dikategorikan"
        a.toast(f"SMS dari {pengirim} diterima: {kat}")
        self.refresh()

    # ---- pembangunan daftar
    def refresh(self, *a):
        ap = app()
        semua = ap.sistem.user.bacaSMS()
        now = datetime.now()
        self.ids.tgl.text = f"{HARI[now.weekday()].upper()}, {now.day} {BULAN[now.month - 1].upper()}"
        aktif = {"semua": self.ids.tab_semua, "kategori": self.ids.tab_kat}
        for nama, b in aktif.items():
            on = nama == self.tab
            b.bg = [1, 1, 1, 1] if on else [0, 0, 0, 0]
            b.fg = C(DARK) if on else C(MUTED)

        data = semua
        q = self.ids.cari.text.strip().lower()
        if q:
            data = [s for s in data if q in s.isiPesan.lower() or q in s.kontak.lower()]

        box = self.ids.daftar
        box.clear_widgets()
        if self.tab == "semua":
            self._isi_semua(box, data, semua)
        else:
            self._isi_kategori(box, data, semua)
        if not data:                                           # A1: daftar kosong
            box.add_widget(Txt(text="Daftar SMS kosong.", color=C(MUTED),
                               halign="center", padding=(0, dp(24))))

    def _banner(self, box):
        b = CardBtn(size_hint_y=None, height=dp(66), bg=C(DARK), radius=dp(18),
                    padding=(dp(16), 0), on_release=lambda *_: self.set_tab("kategori"))
        kol = BoxLayout(orientation="vertical", padding=(0, dp(12)), spacing=dp(2))
        kol.add_widget(Txt(text="Lebih rapi, otomatis.", bold=True, color=[1, 1, 1, 1],
                           font_size="15sp"))
        kol.add_widget(Txt(text="OTP & transaksi sudah dipisahkan.", color=C("#B9D5C6"),
                           font_size="12sp"))
        b.add_widget(kol)
        b.add_widget(Label(text=">", size_hint=(None, 1), width=dp(16), color=[1, 1, 1, 1],
                           bold=True))
        box.add_widget(b)
        box.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))

    def _header(self, box, kiri, kanan=""):
        r = BoxLayout(size_hint_y=None, height=dp(28))
        r.add_widget(Txt(text=kiri, color=C(MUTED), font_size="11sp", size_hint_y=1,
                         valign="middle", text_size=(None, None), bold=True))
        if kanan:
            r.add_widget(Txt(text=kanan, color=C(DARK), font_size="11sp", size_hint_y=1,
                             halign="right", valign="middle"))
        box.add_widget(r)

    def _isi_semua(self, box, data, semua):
        self._banner(box)
        belum = sum(1 for s in semua if s.jenis == "masuk" and s.status == "baru")
        terakhir = None
        for s in data:
            h = label_hari(s.waktu)
            if h != terakhir:
                kanan = f"{belum} belum dibaca" if terakhir is None and belum else ""
                self._header(box, h, kanan)
                terakhir = h
            box.add_widget(self._item(s))

    def _isi_kategori(self, box, data, semua):
        masuk = [s for s in semua if s.jenis == "masuk"]
        n_otp = sum(1 for s in masuk if s.idKategori == Kategori.OTP)
        n_bank = sum(1 for s in masuk if s.idKategori == Kategori.TRANSAKSI)
        kartu = BoxLayout(size_hint_y=None, height=dp(98), spacing=dp(12))
        kartu.add_widget(CountCard(label="Kode OTP", jumlah=f"{n_otp:02d}", bg=C(PURPLE_BG),
                                   fg=C(PURPLE), radius=dp(18)))
        kartu.add_widget(CountCard(label="Transaksi bank", jumlah=f"{n_bank:02d}", bg=C(DARK),
                                   fg=[1, 1, 1, 1], radius=dp(18)))
        box.add_widget(kartu)
        box.add_widget(BoxLayout(size_hint_y=None, height=dp(12)))

        chips = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(8))
        for nama in ("Semua", "OTP", "Transaksi bank", "Lainnya"):
            on = nama == self.filter_kat
            chips.add_widget(Chip(text=nama, height=dp(30), radius=dp(15),
                                  bg=C(DARK) if on else [1, 1, 1, 1],
                                  fg=[1, 1, 1, 1] if on else C(INK),
                                  border=C(DARK) if on else C(LINE),
                                  on_release=lambda c, n=nama: self._set_filter(n)))
        chips.add_widget(Widget_())
        box.add_widget(chips)
        self._header(box, "TERBARU")

        peta = {"OTP": Kategori.OTP, "Transaksi bank": Kategori.TRANSAKSI}
        for s in data:
            if s.jenis != "masuk":
                continue
            if self.filter_kat == "Lainnya" and s.idKategori in (Kategori.OTP, Kategori.TRANSAKSI):
                continue
            if self.filter_kat in peta and s.idKategori != peta[self.filter_kat]:
                continue
            box.add_widget(self._item(s))

    def _set_filter(self, nama):
        self.filter_kat = nama
        self.refresh()

    def _item(self, s):
        nama, cbg, cfg, abg, afg = gaya_kategori(s.idKategori)
        keluar = s.jenis == "keluar"
        pengirim = f"Ke: {s.nomorTujuan}" if keluar else s.nomorPengirim
        huruf = ">" if keluar else (next((c for c in s.nomorPengirim if c.isalnum() or c == "+"), "?")).upper()
        return SMSItem(
            sender=pengirim,
            preview=("Anda: " if keluar else "") + s.isiPesan,
            waktu=fmt_jam(s.waktu), kategori=nama if not keluar else "",
            unread=(s.jenis == "masuk" and s.status == "baru"),
            av_text=huruf, av_bg=abg, av_fg=afg, chip_bg=cbg, chip_fg=cfg,
            on_release=lambda *_, i=s.idSMS: app().buka_detail(i))


def Widget_():
    from kivy.uix.widget import Widget
    return Widget()


class DetailScreen(Screen):                          # MengelolaSMSUI (detail)
    sms_id = NumericProperty(0)

    def on_pre_enter(self, *a):
        ap = app()
        sms = ap.sistem.user.bacaSMS(self.sms_id)             # tampilkanDetailSMS
        if sms is None:
            ap.goto("beranda")
            return
        self.sms = sms
        kat = Kategori(sms.idKategori).getNama() if sms.idKategori else "Belum dikategorikan"
        self.ids.judul.text = sms.kontak
        self.ids.sub.text = f"Kategori: {kat}"
        self.ids.balas.text = ""

        thread = self.ids.thread
        thread.clear_widgets()
        utas = sorted((s for s in ap.sistem.user.bacaSMS() if s.kontak == sms.kontak),
                      key=lambda s: s.waktu)
        for s in utas:
            self._bubble(thread, s)

        ada_kode = sms.idKategori == Kategori.OTP and cari_kode(sms.isiPesan)
        self.ids.chip_salin.opacity = 1 if ada_kode else 0
        self.ids.chip_salin.disabled = not ada_kode
        self.ids.status.text = ("Status: Terklasifikasi otomatis" if sms.idKategori
                                else "Status: Belum dikategorikan")
        Clock.schedule_once(lambda dt: setattr(self.ids.sv, "scroll_y", 0), .1)

    def _bubble(self, thread, s):
        keluar = s.jenis == "keluar"
        b = Bubble(text=s.isiPesan, waktu=fmt_jam(s.waktu), maxw=Window.width * .76,
                   bg=C(DARK) if keluar else C("#E3EBE5"),
                   fg=[1, 1, 1, 1] if keluar else C(INK))
        row = BoxLayout(size_hint_y=None, height=dp(60))
        if keluar:
            row.add_widget(Widget_())
        row.add_widget(b)
        if not keluar:
            row.add_widget(Widget_())
        b.bind(height=lambda inst, v, r=row: setattr(r, "height", v))
        Clock.schedule_once(lambda dt, r=row, bb=b: setattr(r, "height", bb.height))
        thread.add_widget(row)

    def kembali(self):
        app().goto("beranda")

    def salin_kode(self):
        kode = cari_kode(self.sms.isiPesan)
        Clipboard.copy(kode)
        app().toast(f"Kode {kode} disalin.")

    def lihat_kategori(self):
        app().goto("beranda")
        app().root.get_screen("beranda").set_tab("kategori")

    def balas(self):                                          # Mengirim SMS (balas)
        a = app()
        ok, pesan = a.sistem.user.kirimSMS(self.sms.kontak, self.ids.balas.text)
        if not ok and not re.search(r"\d{8}", self.sms.kontak):
            pesan = "Tidak bisa membalas: pengirim ini bukan nomor telepon."
        a.toast(pesan)
        if ok:
            self.on_pre_enter()

    def menu(self):
        app().dialog("Hapus SMS?", "Pesan yang dipilih akan dihapus dari perangkat.",
                     "Hapus", self._hapus, "Batal", ok_bg=C(RED))

    def _hapus(self):                                         # Menghapus SMS
        a = app()
        if a.sistem.user.hapusSMS(self.sms.idSMS):
            a.toast("SMS dihapus.")
        else:
            a.toast("Gagal menghapus SMS.")                   # A2
        a.goto("beranda")


class KirimScreen(Screen):                           # KirimSMSUI
    def on_pre_enter(self, *a):
        self.hitung()

    def hitung(self):
        isi = self.ids.isi
        if len(isi.text) > MAKS_KARAKTER_SMS:
            isi.text = isi.text[:MAKS_KARAKTER_SMS]
        self.ids.hitung.text = f"{len(isi.text)}/{MAKS_KARAKTER_SMS} karakter"

    def kirim(self):                                          # tekanKirim
        a = app()
        ok, pesan = a.sistem.user.kirimSMS(self.ids.tujuan.text, self.ids.isi.text)
        a.toast(pesan)                                        # tampilkanErrorPesan / StatusTerkirim
        if ok:
            self.ids.tujuan.text = ""
            self.ids.isi.text = ""
            a.goto("beranda")


class AkunScreen(Screen):
    def on_pre_enter(self, *a):
        s = app().sistem
        no = s.db.data["user"]["nomorTelepon"].replace("+62", "")
        self.ids.nomor.text = format_nomor(no) if no else "-"
        self.ids.sw.active = s.db.data["pengaturan"]["klasifikasiOtomatis"]

    def ubah_klasifikasi(self, aktif):
        s = app().sistem
        s.db.data["pengaturan"]["klasifikasiOtomatis"] = bool(aktif)
        s.db.simpan()

    def ubah_nomor(self):
        app().goto("verif_nomor")

    def keluar(self):
        app().dialog("Keluar akun?", "Data SMS di aplikasi ini akan dihapus dan nomor "
                     "harus diverifikasi ulang.", "Keluar", self._keluar, "Batal", ok_bg=C(RED))

    def _keluar(self):
        a = app()
        a.sistem.logout()
        a.root.get_screen("verif_nomor").ids.no.text = ""
        a.goto("verif_nomor")


# ====================================================== APP
class PilahSMSApp(App):
    title = "Pilah SMS"

    def build(self):
        import os
        self.sistem = Sistem(os.path.join(self.user_data_dir, "pilah_sms.json"))
        self.sistem.kategorisasi.periksaUlangModel()
        sm = ScreenManager(transition=NoTransition())
        for cls in (VerifNomorScreen, VerifOtpScreen, BerandaScreen, DetailScreen,
                    KirimScreen, AkunScreen):
            sm.add_widget(cls())
        sm.current = "beranda" if self.sistem.user.statusVerifikasi else "verif_nomor"
        Window.bind(on_keyboard=self._tombol)
        self._toast = None
        return sm

    def on_start(self):
        if platform == "android":            # izin SMS saat runtime (Android 6+)
            try:
                from android.permissions import Permission, request_permissions
                request_permissions([Permission.SEND_SMS])
            except ImportError:
                pass

    def goto(self, nama):
        self.root.current = nama

    def buka_detail(self, id):
        d = self.root.get_screen("detail")
        d.sms_id = id
        self.goto("detail")

    # tombol Back Android / tombol Esc di desktop
    def _tombol(self, window, key, *args):
        if key != 27:
            return False
        cur = self.root.current
        tujuan = {"detail": "beranda", "kirim": "beranda", "akun": "beranda",
                  "verif_otp": "verif_nomor"}.get(cur)
        if tujuan:
            self.goto(tujuan)
            return True
        return False

    # ---- toast
    def toast(self, pesan):
        if self._toast is not None:
            Window.remove_widget(self._toast)
        lebar = Window.width - dp(48)
        t = Card(size_hint=(None, None), size=(lebar, dp(52)), bg=C(INK), radius=dp(14),
                 padding=(dp(16), 0))
        t.add_widget(Label(text=pesan, color=[1, 1, 1, 1], font_size="13sp",
                           halign="left", valign="middle", text_size=(lebar - dp(32), dp(52))))
        t.pos = (dp(24), dp(96))
        Window.add_widget(t)
        self._toast = t
        Clock.schedule_once(lambda dt: self._tutup_toast(t), 2.4)

    def _tutup_toast(self, t):
        if t.parent:
            Window.remove_widget(t)
        if self._toast is t:
            self._toast = None

    # ---- dialog konfirmasi
    def dialog(self, judul, pesan, ok_teks, on_ok, batal_teks="Batal", ok_bg=None):
        mv = ModalView(size_hint=(None, None), size=(Window.width - dp(48), dp(210)),
                       background="", background_color=[0, 0, 0, 0],
                       overlay_color=[0, 0, 0, .45])
        kartu = Card(orientation="vertical", bg=[1, 1, 1, 1], radius=dp(20),
                     padding=dp(20), spacing=dp(8))
        kartu.add_widget(Txt(text=judul, bold=True, font_size="18sp", color=C(DARK)))
        kartu.add_widget(Txt(text=pesan, color=C(MUTED), font_size="13sp",
                             size_hint_y=1, valign="top", text_size=(Window.width - dp(88), None)))
        baris = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(10))
        baris.add_widget(Btn(text=batal_teks, height=dp(46), bg=C(SOFT), fg=C(DARK),
                             on_release=lambda *_: mv.dismiss()))

        def _ok(*_):
            mv.dismiss()
            on_ok()
        baris.add_widget(Btn(text=ok_teks, height=dp(46), bg=ok_bg or C(DARK), on_release=_ok))
        kartu.add_widget(baris)
        mv.add_widget(kartu)
        mv.open()


if __name__ == "__main__":
    PilahSMSApp().run()
