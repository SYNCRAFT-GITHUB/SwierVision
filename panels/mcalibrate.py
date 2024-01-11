import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['mcalibrate']

        grid = self._gtk.HomogeneousGrid()

        self.above_text = Gtk.Label(f'\n{_("Adjust the screws of the secondary extruder, on the right side.")}\n')
        self.above_text.set_property("opacity", 0.3)

        self.below_text = Gtk.Label(f'\n{_("After completing the procedure, press the button to finish.")}\n')
        self.below_text.set_property("opacity", 0.3)

        self.content.add(self.above_text)
        self.content.add(self.below_text)

        self.start_btn = self._gtk.Button("screw-adjust", _("Start"), "color2")
        self.finish_btn = self._gtk.Button("home", _("Home All"), "color3")
        self.finish_btn.set_sensitive(False)
        self.start_btn.connect("clicked", self.start_calibration)
        self.finish_btn.connect("clicked", self.finish_calibration)
        grid.attach(self.start_btn, 0, 0, 1, 1)
        grid.attach(self.finish_btn, 0, 1, 1, 1)

        self.labels['mcalibrate'] = self._gtk.HomogeneousGrid()
        self.labels['mcalibrate'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['mcalibrate'])

    def start_calibration(self, button):
        self._screen._ws.klippy.gcode_script("PROBE_CALIBRATE_AUTOMATIC")
        self.finish_btn.set_sensitive(True)
        self.above_text.set_property("opacity", 1.0)
        self.below_text.set_property("opacity", 1.0)

    def finish_calibration(self, button):
        self._screen._ws.klippy.gcode_script("G28")