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
        self.menu = ['obico_sync_panel']

        digits = {
            '1': None,
            '2': None,
            '3': None,
            '4': None,
            '5': None,
            '6': None,
        }

        for key, value in digits.items():
            self.labels[key] = Gtk.Label(" ") if not value else Gtk.Label(f"{value}")
            self.labels['obico_sync_panel'].attach(self.labels[key], int(key)-1, 0, 1, 1)



        self.content.add(self.labels['obico_sync_panel'])