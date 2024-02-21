import logging
import random

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['fix_panel']

        self.buttons = {
            'FIX_MAINSAIL': self._gtk.Button("monitor", _("Mainsail"), self.color()),
            'FIX_MOONRAKER': self._gtk.Button("moonraker", _("Moonraker"), self.color()),
            'FIX_CAMERA': self._gtk.Button("camera", _("Camera Driver"), self.color()),
            'FIX_LED': self._gtk.Button("light", _("LED Light Driver"), self.color())
        }

        self.buttons['FIX_MAINSAIL'].connect("clicked", self.set_fix_option_to, "MAINSAIL")
        self.buttons['FIX_MAINSAIL'].connect("clicked", self.menu_item_clicked, {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        self.buttons['FIX_MOONRAKER'].connect("clicked", self.set_fix_option_to, "MOONRAKER")
        self.buttons['FIX_MOONRAKER'].connect("clicked", self.menu_item_clicked, {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        self.buttons['FIX_CAMERA'].connect("clicked", self.set_fix_option_to, "CAMERA")
        self.buttons['FIX_CAMERA'].connect("clicked", self.menu_item_clicked, {
            "name": _("Fix"),
            "panel": "fix_steps"
        })
        
        self.buttons['FIX_LED'].connect("clicked", self.set_fix_option_to, "LIGHT")
        self.buttons['FIX_LED'].connect("clicked", self.menu_item_clicked, {
            "name": _("Fix"),
            "panel": "fix_steps"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['FIX_MAINSAIL'], 0, 0, 1, 1)
        grid.attach(self.buttons['FIX_MOONRAKER'], 0, 1, 1, 1)
        grid.attach(self.buttons['FIX_CAMERA'], 0, 2, 1, 1)
        grid.attach(self.buttons['FIX_LED'], 0, 3, 1, 1)

        self.labels['fix_panel'] = self._gtk.HomogeneousGrid()
        self.labels['fix_panel'].attach(grid, 0, 0, 2, 2)

        self.content.add(self.labels['fix_panel'])

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def color(self) -> str:
        return f"color{random.randint(1, 4)}"
