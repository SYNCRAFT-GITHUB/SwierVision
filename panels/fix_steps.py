import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['fix_steps']

        self.page: int = 0

        self.texts = [
            _("Please follow the tutorial to ensure everything performs correctly."),
            _("Do not turn off Syncraft during the procedure, and keep a stable internet connection."),
            _("Interrupting this procedure can result in problems for the internal system."),
            _("If you are constantly using system fixes, please contact Syncraft and let them know."),
            _("At the end, Syncraft will restart.")
        ]

        self.image = self._gtk.Image("warning", self._gtk.content_width * 4, self._gtk.content_height * .6)

        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        self.content.add(self.info)

        self.labels['text'] = Gtk.Label(f"{self.texts[self.page]}")
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)
        
        self.content.add(self.labels['text'])

        self.buttons = {
            'OK': self._gtk.Button("arrow-right", _("I agree, continue"), "color2"),
        }
        self.buttons['OK'].connect("clicked", self.update_screen)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['OK'], 1, 0, 1, 1)

        self.labels['fix_steps'] = self._gtk.HomogeneousGrid()
        self.labels['fix_steps'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['fix_steps'])

    def update_screen(self, button):

        if (self.page < 4):

            self.page += 1
            self.labels['text'].set_label(f"{self.texts[self.page]}")

        if (self.page == 4):

            if not self._config.internet_connection():
                message: str = _("This procedure requires internet connection")
                self._screen.show_popup_message(message, level=3)
            else:
                self.buttons['OK'].connect("clicked", self.menu_item_clicked, {
                "name": _("Fix"),
                "panel": "script"
                })