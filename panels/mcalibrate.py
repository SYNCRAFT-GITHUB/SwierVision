import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['mcalibrate']

        grid = self._gtk.HomogeneousGrid()

        self.running: bool = False
        self.hidden: bool = False

        self.above_text = Gtk.Label(f'\n{_("Adjust the screws of the secondary extruder, on the right side.")}')

        self.below_text = Gtk.Label(f'\n{_("After completing the procedure, press the button to finish.")}\n')

        self.content.add(self.above_text)
        self.content.add(self.below_text)

        self.hide_btn = self._gtk.Button("hidden", f'  {_("Prevent accidental presses by hiding buttons")}', "color1", .80, Gtk.PositionType.LEFT)
        self.start_btn = self._gtk.Button("screw-adjust", f'  {_("Start")}', "color2", 1, Gtk.PositionType.LEFT)
        self.finish_btn = self._gtk.Button("complete", f'  {_("Finish")}', "color3", 1, Gtk.PositionType.LEFT)
        self.hide_btn.connect("clicked", self.hide_buttons)
        self.start_btn.connect("clicked", self.start_calibration)
        self.finish_btn.connect("clicked", self.finish_calibration)
        self.transparent()
        grid.attach(self.hide_btn, 0, 0, 1, 1)
        grid.attach(self.start_btn, 0, 1, 1, 2)
        grid.attach(self.finish_btn, 0, 3, 1, 2)

        self.labels['mcalibrate'] = self._gtk.HomogeneousGrid()
        self.labels['mcalibrate'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['mcalibrate'])

    def hide_buttons(self, button):
        if self.hidden:
            self.hide_btn.set_label(f'  {_("Prevent accidental presses by hiding buttons")}')
            if self.running:
                self.start_btn.set_sensitive(True)
                self.finish_btn.set_sensitive(True)
            else:
                self.start_btn.set_sensitive(True)
                self.finish_btn.set_sensitive(False)
        else:
            self.hide_btn.set_label(f'  {_("Re-enable buttons")}')
            if self.running:
                self.start_btn.set_sensitive(False)
                self.finish_btn.set_sensitive(False)
            else:
                self.start_btn.set_sensitive(False)
                self.finish_btn.set_sensitive(False)
        self.hidden = not self.hidden

    def start_calibration(self, button):
        self._screen._ws.klippy.gcode_script("PROBE_CALIBRATE_AUTOMATIC")
        self.finish_btn.set_sensitive(True)
        self.above_text.set_property("opacity", 1.0)
        self.below_text.set_property("opacity", 1.0)
        self.start_btn.set_label(f'  {_("Restart")}')
        self.running = True

    def finish_calibration(self, button):
        self.transparent()
        self._screen._ws.klippy.gcode_script("IDEX_OFFSET Z=0")
        self._screen._ws.klippy.gcode_script("G28 Z")
        self._screen._ws.klippy.gcode_script("M84")
        self.start_btn.set_label(f'  {_("Start")}')
        self.running = False
        self._screen._menu_go_back()

    def transparent(self):
        self.above_text.set_property("opacity", 0.3)
        self.below_text.set_property("opacity", 0.3)
        self.finish_btn.set_sensitive(False)