import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel



class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)

        self.content.add(Gtk.Label("\n"))

        self.image = self._gtk.Image("website", self._gtk.content_width * .8, self._gtk.content_height * .8, universal=True)

        self.content.add(self.image)