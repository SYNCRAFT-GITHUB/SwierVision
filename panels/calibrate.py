import logging
import shutil
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['calibrate_panel']

        self.buttons = {
            'CALIB_IDEX': self._gtk.Button("idex", _("Calibrate IDEX"), "color4"),
            'CALIB_Z': self._gtk.Button ("bed-level", _("Z Calibrate"), "color2"),
        }
        self.buttons['CALIB_IDEX'].connect("clicked",self.calibrate_idex)

        self.buttons['CALIB_Z'].connect("clicked", self.menu_item_clicked, {
            "name":_("Z Calibrate"),
            "panel": "zcalibrate"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['CALIB_IDEX'], 0, 0, 1, 1)
        grid.attach(self.buttons['CALIB_Z'], 1, 0, 1, 1)

        self.labels['calibrate_panel'] = self._gtk.HomogeneousGrid()
        self.labels['calibrate_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['calibrate_panel'])

    def calibrate_idex(self, button):
        calib_file_path = os.path.join(os.path.dirname( __file__ ), '..', 'ks_includes', 'idex_calibrate.gcode')
        gcodes_path = os.path.join('/home', 'pi', 'printer_data', 'gcodes')
        calib_file_gcodes = (os.path.join(gcodes_path, '.idex_calibrate.gcode'))
        if os.path.exists(calib_file_path):
            try:
                shutil.copyfile(calib_file_path, calib_file_gcodes)
                params = {"filename": ".idex_calibrate.gcode"}
                self._screen._confirm_send_action(
                    None,
                    f"{_('This procedure will start printing a specific 3D model for calibration.')}" + "\n\n" +
                    f"{_('It is recommended to use materials of the same type with different colors.')}",
                    "printer.print.start",
                    params
                )
            except:
                message: str = _("An error has occurred")
                self._screen.show_popup_message(message, level=3)
                return None

    def set_fix_option_to(self, button, newfixoption):
        self._config.replace_fix_option(newvalue=newfixoption)