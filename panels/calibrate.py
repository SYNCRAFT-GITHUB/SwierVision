import logging
import zipfile
import shutil
import json
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel

from panels.material_load import PrinterMaterial, read_materials_from_json


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['calibrate_panel']

        self.buttons = {
            'BED_CALIBRATION': self._gtk.Button ("bed-level", "   " + _("Bed Calibration"), "color2", 1, Gtk.PositionType.LEFT, 1),
            'PROBE_CALIBRATION': self._gtk.Button("idex-height-check", "   " + _("Probe Calibration"), "color2", 1, Gtk.PositionType.LEFT, 1),
            'HEIGHT_CHECK': self._gtk.Button("idex-height-check", "   " + _("Check height"), "color2", 1, Gtk.PositionType.LEFT, 1),
            'CALIB_MEC': self._gtk.Button("screw-adjust", "   " + _("IDEX Calibration for Z Axis"), "color3", 1, Gtk.PositionType.LEFT, 1),
            'CALIB_IDEX': self._gtk.Button("resume", "   " + _("Print IDEX Calibration File for XY Axes"), "color4", 1, Gtk.PositionType.LEFT, 1),
            'IDEX_OFFSET': self._gtk.Button("idex", _("Adjust"), "color4"),
        }

        self.buttons['BED_CALIBRATION'].connect("clicked", self.menu_item_clicked, {
            "name":_("Bed Calibration"),
            "panel": "screws_adjust"
        })

        self.buttons['PROBE_CALIBRATION'].connect("clicked", self.menu_item_clicked, {
            "name":_("Probe Calibration"),
            "panel": "zcalibrate"
        })

        self.buttons['HEIGHT_CHECK'].connect("clicked",self.check_height)

        self.buttons['CALIB_MEC'].connect("clicked", self.menu_item_clicked, {
            "name":_("Mechanical Calibration"),
            "panel": "mcalibrate"
        })

        self.buttons['CALIB_IDEX'].connect("clicked",self.calibrate_idex)
        
        self.buttons['IDEX_OFFSET'].connect("clicked", self.menu_item_clicked, {
            "name":_("Calibrar IDEX"),
            "panel": "idex_offset"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['BED_CALIBRATION'], 0, 0, 6, 1)
        grid.attach(self.buttons['PROBE_CALIBRATION'], 0, 1, 6, 1)
        grid.attach(self.buttons['HEIGHT_CHECK'], 0, 2, 3, 1)
        grid.attach(self.buttons['CALIB_MEC'], 3, 2, 3, 1)
        grid.attach(self.buttons['CALIB_IDEX'], 0, 3, 5, 1)
        grid.attach(self.buttons['IDEX_OFFSET'], 5, 3, 1, 1)

        self.labels['calibrate_panel'] = self._gtk.HomogeneousGrid()
        self.labels['calibrate_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['calibrate_panel'])

    def check_height(self, button):
        self._screen._ws.klippy.gcode_script("IDEX_NOZZLE_CHECK")
        message: str = _("Nozzle height will be checked.") + "\n\n" \
        + _("If not properly leveled, perform a mechanical calibration.")
        self._screen.show_popup_message(message, level=4)

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)

    def calibrate_idex(self, button):
        self._screen._ws.klippy.gcode_script("print_calibration")