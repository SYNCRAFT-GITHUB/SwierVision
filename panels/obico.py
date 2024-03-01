import logging
import shutil
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['obico_panel']

        grid = self._gtk.HomogeneousGrid()

        textfield_label = self._gtk.Label(f"{_('Enter the 6-digit verification code:')}")
        textfield_label.set_hexpand(False)
        self.labels['6_digit_code'] = Gtk.Entry()
        self.labels['6_digit_code'].set_text('')
        self.labels['6_digit_code'].set_hexpand(True)
        self.labels['6_digit_code'].connect("activate", self.sync_app)
        self.labels['6_digit_code'].connect("focus-in-event", self._screen.show_keyboard)

        box = Gtk.Box()
        box.pack_start(self.labels['6_digit_code'], True, True, 5)

        self.labels['insert_code'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.labels['insert_code'].set_valign(Gtk.Align.CENTER)
        self.labels['insert_code'].set_hexpand(True)
        self.labels['insert_code'].set_vexpand(True)
        self.labels['insert_code'].pack_start(textfield_label, True, True, 5)
        self.labels['insert_code'].pack_start(box, True, True, 5)

        grid.attach(self.labels['insert_code'], 0, 0, 1, 1)
        self.labels['6_digit_code'].grab_focus_without_selecting()

        self.labels['help'] = self._gtk.Button("help", _("Need Help?"), "color1", 1)
        self.labels['continue'] =self._gtk.Button("arrow-right", _("Continue"), "color2", 1)

        self.labels['help'].connect("clicked", self.menu_item_clicked, {
                "name": _("Help"),
                "panel": "help"
            })

        self.labels['continue'].connect("clicked", self.sync_app)

        grid.attach(self.labels['help'], 0, 1, 1, 1)
        grid.attach(self.labels['continue'], 0, 2, 1, 2)

        self.content.add(grid)


    def sync_app(self, button):
        code = (self.labels['6_digit_code'].get_text()).lstrip()
        print(f"code: {code}")

        if not self._config.internet_connection():
            message: str = _("This procedure requires internet connection")
            self._screen.show_popup_message(message, level=3)
            return