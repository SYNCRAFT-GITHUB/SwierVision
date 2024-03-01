import logging
import random
import gi
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel

UNKNOWN = 2
TRUE = 1
FALSE = 0

class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['sensors_verif_panel']

        self.process_index = 0
        self.verification = UNKNOWN

        grid = self._gtk.HomogeneousGrid()

        self.labels["text_01"] = Gtk.Label(_("Before starting a print, it will be checked if the materials are inserted."))
        self.labels["text_02"] = Gtk.Label(_("This verification is done with sensors to prevents errors."))
        self.labels["text_03"] = Gtk.Label(_("However, you can disable this verification."))

        self.labels["info"] = Gtk.Label("...")

        toggle = self._gtk.Button("check_sensor", "Apply", "color1")
        toggle.connect("clicked", self.set_verification)

        grid.attach(self.labels["text_01"], 0, 0, 1, 1)
        grid.attach(self.labels["text_02"], 0, 1, 1, 1)
        grid.attach(self.labels["text_03"], 0, 2, 1, 1)
        grid.attach(self.labels["info"], 0, 3, 1, 1)
        grid.attach(toggle, 0, 4, 1, 2)
        
        self.content.add(grid)

    def set_verification(self, button):
        if self.verification == UNKNOWN:
            message: str = _("Please wait")
            self._screen.show_popup_message(message, level=2)
            return
        if self.verification == TRUE:
            self.verification = FALSE
            self._screen._ws.klippy.gcode_script("SET_SENSORS_VERIFICATION S0")
            return
        if self.verification == FALSE:
            self.verification = TRUE
            self._screen._ws.klippy.gcode_script("SET_SENSORS_VERIFICATION S1")
            return

    def verify(self):
        self._screen._ws.klippy.gcode_script("SET_SENSORS_VERIFICATION")

    def update_label(self):
        if self.verification == TRUE:
            self.labels["info"].set_label(_("Verification is enabled"))
        elif self.verification == FALSE:
            self.labels["info"].set_label(_("Verification is disabled"))
        else:
            self.labels["info"].set_label("...")

    def process_update(self, action, data):

        self.process_index += 1
        if self.process_index % 16 == 0:
            self.verify()
            self.process_index = 0

        self.update_label()

        if action == "notify_gcode_response":

            if 'sensors_verification:' in data:
                if 'sensors_verification:1' in data:
                    self.verification = TRUE
                if 'sensors_verification:0' in data:
                    self.verification = FALSE