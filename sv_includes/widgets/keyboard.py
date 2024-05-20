import logging
import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class Keyboard(Gtk.Box):
    langs = ["Deutsch - DE", "English - EN", "Français - FR", "Español - ES"]

    def __init__(self, screen, close_cb, entry=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.shift = []
        self.shift_active = False
        self.close_cb = close_cb
        self.keyboard = Gtk.Grid()
        self.keyboard.set_direction(Gtk.TextDirection.LTR)
        self.timeout = self.clear_timeout = None
        self.entry = entry

        language = screen._config.get_main_config().get("language", None)
        logging.info(f"Keyboard Lang: {language}")

        if language == "Deutsch - DE":
            self.keys = [
                [
                    ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä"],
                    ["↑", "y", "x", "c", "v", "b", "n", "m", "ẞ", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä"],
                    ["↑", "Y", "X", "C", "V", "B", "N", "M", "ß", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "#+=", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["[", "]", "{", "}", "#", "%", "^", "*", "+", "="],
                    ["_", "\\", "|", "~", "<", ">", "€", "£", "¥", "•"],
                    ["↑", ".", ",", "?", "!", "'", "º", "¨", "123", "⌫"],
                    ["ABC", " ", "↓"],
                ]
            ]
        elif language == "Français - FR":
            self.keys = [
                [
                    ["a", "z", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["q", "s", "d", "f", "g", "h", "j", "k", "l", "m"],
                    ["↑", "w", "x", "c", "v", "b", "n", "ç", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["Q", "S", "D", "F", "G", "H", "J", "K", "L", "M"],
                    ["↑", "W", "X", "C", "V", "B", "N", "Ç", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "ABC", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["[", "]", "{", "}", "#", "%", "^", "*", "+", "="],
                    ["_", "\\", "|", "~", "<", ">", "€", "£", "¥", "•"],
                    ["↑", ".", ",", "?", "!", "'", "º", "Æ", "æ", "⌫"],
                    ["ABC", " ", "↓"],
                ]
            ]
        elif language == "Русский - RU":
            self.keys = [
                [
                    ["й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з"],
                    ["ф", "ы", "в", "а", "п", "р", "о", "л", "д"],
                    ["↑", "я", "ч", "с", "м", "и", "т", "ь", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["Й", "Ц", "У", "К", "Е", "Н", "Г", "Ш", "Щ", "З"],
                    ["Ф", "Ы", "В", "А", "П", "Р", "О", "Л", "Д"],
                    ["↑", "Я", "Ч", "С", "М", "И", "Т", "Ь", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "ABC", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
                    ["K", "L", "M", "N", "O", "P", "Q", "R", "S"],
                    ["↑", "T", "U", "V", "W", "X", "Y", "Z", "⌫"],
                    ["123", " ", "↓"],
                ]
            ]
        elif language == "日本語 - JA":
            self.keys = [
                [
                    ["あ", "い", "う", "え", "お", "や", "ゆ", "よ", "わ", "を"],
                    ["か", "き", "く", "け", "こ", "た", "ち", "つ", "て", "と"],
                    ["↑", "さ", "し", "す", "せ", "そ", "な", "に", "ぬ", "ね", "の", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["ア", "イ", "ウ", "エ", "オ", "ヤ", "ユ", "ヨ", "ワ", "ヲ"],
                    ["カ", "キ", "ク", "ケ", "コ", "タ", "チ", "ツ", "テ", "ト"],
                    ["↑", "サ", "シ", "ス", "セ", "ソ", "ナ", "ニ", "ヌ", "ネ", "ノ", "⌫"],
                    ["123", " ", "↓"],
                ],
                [   
                    ["ア", "イ", "ウ", "エ", "オ", "ヤ", "ユ", "ヨ", "ワ", "ヲ"],
                    ["カ", "キ", "ク", "ケ", "コ", "タ", "チ", "ツ", "テ", "ト"],
                    ["↑", "サ", "シ", "ス", "セ", "ソ", "ナ", "ニ", "ヌ", "ネ", "ノ", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
                    ["K", "L", "M", "N", "O", "P", "Q", "R", "S"],
                    ["↑", "T", "U", "V", "W", "X", "Y", "Z", "⌫"],
                    ["123", " ", "↓"],
                ]
            ]
        elif language == "한국어 - KO":
            self.keys = [
                [
                    ["ㅂ", "ㅈ", "ㄷ", "ㄱ", "ㅅ", "ㅛ", "ㅕ", "ㅑ", "ㅐ", "ㅔ"],
                    ["ㅁ", "ㄴ", "ㅇ", "ㄹ", "ㅎ", "ㅗ", "ㅓ", "ㅏ", "ㅣ"],
                    ["↑", "ㅋ", "ㅌ", "ㅊ", "ㅍ", "ㅠ", "ㅜ", "ㅡ", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["ㅃ", "ㅉ", "ㄸ", "ㄲ", "ㅆ", "ㅛ", "ㅕ", "ㅑ", "ㅒ", "ㅖ"],
                    ["ㅁ", "ㄴ", "ㅇ", "ㄹ", "ㅎ", "ㅗ", "ㅓ", "ㅏ", "ㅣ"],
                    ["↑", "ㅋ", "ㅌ", "ㅊ", "ㅍ", "ㅠ", "ㅜ", "ㅡ", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "~", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
                    ["K", "L", "M", "N", "O", "P", "Q", "R", "S"],
                    ["↑", "T", "U", "V", "W", "X", "Y", "Z", "⌫"],
                    ["123", " ", "↓"],
                ]
            ]
        elif language == "简体中文 - ZH":
            self.keys = [
                [
                    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
                    ["↑", "z", "x", "c", "v", "b", "n", "m", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                    ["↑", "Z", "X", "C", "V", "B", "N", "M", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "¥", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["你", "好", "是", "的", "我", "们", "中", "国", "人", "大"],
                    ["地", "了", "和", "在", "他", "有", "这", "个", "上", "不"],
                    ["↑", "们", "说", "为", "子", "得", "去", "也", "#+=", "⌫"],
                    ["abc", " ", "↓"],
                ]
            ]
        else:
            self.keys = [
                [
                    ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
                    ["↑", "z", "x", "c", "v", "b", "n", "m", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                    ["↑", "Z", "X", "C", "V", "B", "N", "M", "#+=", "⌫"],
                    ["123", " ", "↓"],
                ],
                [
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                    ["@", "#", "$", "_", "&", "-", "+", "(", ")", "/"],
                    ["↑", "*", '"', "'", ":", ";", "!", "?", "Ç", "⌫"],
                    ["abc", " ", "↓"],
                ],
                [
                    ["[", "]", "{", "}", "#", "%", "^", "*", "+", "="],
                    ["_", "\\", "|", "~", "<", ">", "€", "£", "¥", "•"],
                    ["↑", ".", ",", "?", "!", "'", "º", "ç", "abc", "⌫"],
                    ["ABC", " ", "↓"],
                ]
            ]

            if language == "Español - ES":
                self.keys[0][1].append("ñ")
                self.keys[1][1].append("Ñ")

            if language == "Português - PT":
                self.keys[0][1].append("ç")
                self.keys[1][1].append("Ç")

        self.buttons = self.keys.copy()
        for p, pallet in enumerate(self.keys):
            for r, row in enumerate(pallet):
                for k, key in enumerate(row):
                    if key == "⌫":
                        self.buttons[p][r][k] = screen.gtk.Button("backspace", scale=.6)
                    elif key == "↑":
                        self.buttons[p][r][k] = screen.gtk.Button("arrow-up", scale=.6)
                        self.shift.append(self.buttons[p][r][k])
                    elif key == "↓":
                        self.buttons[p][r][k] = screen.gtk.Button("arrow-down", scale=.6)
                    else:
                        self.buttons[p][r][k] = screen.gtk.Button(label=key, lines=1)
                    self.buttons[p][r][k].set_hexpand(True)
                    self.buttons[p][r][k].set_vexpand(True)
                    self.buttons[p][r][k].connect('button-press-event', self.repeat, key)
                    self.buttons[p][r][k].connect('button-release-event', self.release)
                    self.buttons[p][r][k].get_style_context().add_class("keyboard_pad")

        self.pallet_nr = 0
        self.set_pallet(self.pallet_nr)
        self.add(self.keyboard)

    def detect_language(self, language):
        if language is None or language == "system_lang":
            for language in self.langs:
                if os.getenv('LANG').lower().startswith(language):
                    return language
        for _ in self.langs:
            if language.startswith(_):
                return _
        return "en"

    def set_pallet(self, p):
        for _ in range(len(self.keys[self.pallet_nr]) + 1):
            self.keyboard.remove_row(0)
        self.pallet_nr = p
        columns = 0
        for r, row in enumerate(self.keys[p][:-1]):
            for k, key in enumerate(row):
                x = k * 2 + 1 if r == 1 else k * 2
                self.keyboard.attach(self.buttons[p][r][k], x, r, 2, 1)
                if x > columns:
                    columns = x
        self.keyboard.attach(self.buttons[p][3][0], 0, 4, 3, 1)  # 123
        self.keyboard.attach(self.buttons[p][3][1], 3, 4, -4 + columns, 1)  # Space
        self.keyboard.attach(self.buttons[p][3][2], -1 + columns, 4, 3, 1)  # ↓
        self.show_all()

    def repeat(self, widget, event, key):
        # Button-press
        widget.get_style_context().add_class("active")
        self.update_entry(widget, key)
        if self.timeout is None and key == "⌫":
            # Hold for repeat, hold longer to clear the field
            self.clear_timeout = GLib.timeout_add_seconds(3, self.clear, widget)
            # This can be used to repeat all the keys,
            # but I don't find it useful on the console
            self.timeout = GLib.timeout_add(400, self.repeat, widget, None, key)
        return True

    def release(self, widget, event):
        # Button-release
        if self.timeout is not None:
            GLib.source_remove(self.timeout)
            self.timeout = None
        if self.clear_timeout is not None:
            GLib.source_remove(self.clear_timeout)
            self.clear_timeout = None
        if widget not in self.shift:
            widget.get_style_context().remove_class("active")

    def clear(self, widget=None):
        self.entry.set_text("")
        if self.clear_timeout is not None:
            GLib.source_remove(self.clear_timeout)
            self.clear_timeout = None

    def update_entry(self, widget, key):
        if key == "⌫":
            Gtk.Entry.do_backspace(self.entry)
        elif key == "↓":
            self.close_cb()
            return
        elif key == "↑":
            self.toggle_shift()
            if self.pallet_nr == 0:
                self.set_pallet(1)
            elif self.pallet_nr == 1:
                self.set_pallet(0)
            elif self.pallet_nr == 2:
                self.set_pallet(3)
            elif self.pallet_nr == 3:
                self.set_pallet(2)
            return
        elif key == "abc":
            if self.shift_active:
                self.toggle_shift()
            widget.get_style_context().remove_class("active")
            self.set_pallet(0)
        elif key == "ABC":
            if not self.shift_active:
                self.toggle_shift()
            widget.get_style_context().remove_class("active")
            self.set_pallet(1)
        elif key == "123":
            if self.shift_active:
                self.toggle_shift()
            widget.get_style_context().remove_class("active")
            self.set_pallet(2)
        elif key == "#+=":
            if not self.shift_active:
                self.toggle_shift()
            widget.get_style_context().remove_class("active")
            self.set_pallet(3)
        else:
            Gtk.Entry.do_insert_at_cursor(self.entry, key)

    def toggle_shift(self):
        self.shift_active = not self.shift_active
        if self.shift_active:
            for widget in self.shift:
                widget.get_style_context().add_class("active")
        else:
            for widget in self.shift:
                widget.get_style_context().remove_class("active")
