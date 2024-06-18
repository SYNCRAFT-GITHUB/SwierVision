import logging
import shutil
import json
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel
from panels.material_load import PrinterMaterial

def read_materials_from_json(file_path: str):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return_array = []
            for item in data:
                    material = PrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        id=item['id'],
                        brand=item['brand'],
                        color=item['color'],
                        compatible=item['compatible'],
                        experimental=item['experimental'],
                        temp=item['temp'],
                        print_temp=item['print_temp'],
                    )
                    return_array.append(material)
            return return_array
    except FileNotFoundError:
        print(f"Not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON: {file_path}")


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['calibrate_panel']

        self.buttons = {
            'CALIB_MEC': self._gtk.Button("screw-adjust", "   " + _("IDEX Calibration for Z Axis"), "color3", 1, Gtk.PositionType.LEFT, 1),
            'CALIB_IDEX': self._gtk.Button("resume", "   " + _("Print IDEX Calibration File for XY Axes"), "color4", 1, Gtk.PositionType.LEFT, 1),
            'IDEX_OFFSET': self._gtk.Button("idex", _("Adjust"), "color4"),
            'HEIGHT_CHECK': self._gtk.Button("idex-height-check", "   " + _("Check Nozzle Height"), "color2", 1, Gtk.PositionType.LEFT, 1),
            'CALIB_Z': self._gtk.Button ("bed-level", "   " + _("Bed Calibration"), "color2", 1, Gtk.PositionType.LEFT, 1),
        }

        self.buttons['CALIB_IDEX'].connect("clicked",self.calibrate_idex)

        self.buttons['HEIGHT_CHECK'].connect("clicked",self.check_height)
        
        self.buttons['IDEX_OFFSET'].connect("clicked", self.menu_item_clicked, {
            "name":_("Calibrar IDEX"),
            "panel": "idex_offset"
        })

        self.buttons['CALIB_MEC'].connect("clicked", self.menu_item_clicked, {
            "name":_("Mechanical Calibration"),
            "panel": "mcalibrate"
        })

        self.buttons['CALIB_Z'].connect("clicked", self.menu_item_clicked, {
            "name":_("Z Calibrate"),
            "panel": "zcalibrate"
        })

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['CALIB_MEC'], 0, 1, 5, 1)
        grid.attach(self.buttons['CALIB_Z'], 0, 2, 5, 1)
        grid.attach(self.buttons['CALIB_IDEX'], 0, 3, 4, 1)
        grid.attach(self.buttons['IDEX_OFFSET'], 4, 3, 1, 1)
        grid.attach(self.buttons['HEIGHT_CHECK'], 0, 0, 5, 1)

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

        mat0 = self._config.variables_value_reveal('material_ext0')
        mat1 = self._config.variables_value_reveal('material_ext1')

        nozzle0 = self._config.variables_value_reveal('nozzle0')
        nozzle1 = self._config.variables_value_reveal('nozzle1')

        materials = read_materials_from_json(self._config.materials_path(custom=False))

        try:
            iter(materials)
        except:
            materials = []

        ext0_temp = ext1_temp = 0

        for material in materials:
            if material.name == mat0:
                ext0_temp = material.print_temp
            if material.name == mat1:
                ext1_temp = material.print_temp

        if ext0_temp == 0 or ext1_temp == 0:
            msg = f"{_('An error has occurred')}\n{_('Try selecting a material for each of the extruders again.')}"
            return self._screen.show_popup_message(msg, level=3)

        compatibles = {
            'Standard 0.25mm':  ['Standard 0.25mm', 'Standard 0.4mm', 'Standard 0.8mm'],
            'Standard 0.4mm':   ['Standard 0.25mm', 'Standard 0.4mm', 'Standard 0.8mm', 'Fiber 0.6mm'],
            'Standard 0.8mm':   ['Standard 0.25mm', 'Standard 0.4mm', 'Standard 0.8mm', 'Fiber 0.6mm'],
            'Fiber 0.6mm':      ['Standard 0.4mm', 'Standard 0.8mm']
        }

        shorts = {
            'Standard 0.25mm': 'STD25',
            'Standard 0.4mm': 'STD04',
            'Standard 0.8mm': 'STD08',
            'Fiber 0.6mm': 'FIB06'
        }

        try:
            compatibles[nozzle0]
            compatibles[nozzle1]
        except:
            msg = _("Insert and select a compatible nozzle for calibration.")
            return self._screen.show_popup_message(msg, level=3)

        if nozzle1 not in compatibles[nozzle0]:
            msg = _("Your nozzle combination is not compatible with this calibration method.")
            return self._screen.show_popup_message(msg, level=3)

        calib_file_path = os.path.join(os.path.dirname( __file__ ), '..', 'sv_includes', 'idex_calibrate', \
            shorts[nozzle0], f'idex_calibrate_{shorts[nozzle0]}_{shorts[nozzle1]}.gcode')

        calib_new_file_path = os.path.join(os.path.dirname( __file__ ), '..', 'sv_includes', 'idex_calibrate', 'idex_calibrate.gcode')
        
        if os.path.exists(calib_new_file_path):
            os.remove(calib_new_file_path)

        try:
            with open(calib_file_path, 'r', encoding='utf-8') as gcode_file:
                content = gcode_file.read()

            content = content.replace('<TEMPERATURE_LAYER_ZERO_VALUE>', str(ext0_temp))
            content = content.replace('<TEMPERATURE_LAYER_ONE_VALUE>', str(ext1_temp))
            
            with open(calib_new_file_path, 'w', encoding='utf-8') as new_gcode_file:
                new_gcode_file.write(content)
        except Exception as e:
            print(f"Error: {e}")
            return self._screen.show_popup_message(_('An error has occurred'), level=3)

        gcodes_path = os.path.join('/home', 'pi', 'printer_data', 'gcodes')
        calib_file_gcodes = (os.path.join(gcodes_path, '.idex_calibrate.gcode'))
        if os.path.exists(calib_file_gcodes):
            os.remove(calib_file_gcodes)
        if os.path.exists(calib_new_file_path):
            try:
                shutil.copyfile(calib_new_file_path, calib_file_gcodes)
                params = {"filename": ".idex_calibrate.gcode"}
                self._screen._confirm_send_action(
                    None,
                    f"{_('This procedure will start printing a specific 3D model for calibration.')}" + "\n" +
                    f"{_('It is recommended to use materials of the same type with different colors.')}" + "\n\n" +
                    f"{_('Check the calibration details carefully:')}" + "\n\n" +
                    f"1: {nozzle0}\n{_('Temp (°C)')}: {str(ext0_temp)}\n{_('Material')}: {mat0}" + "\n\n" +
                    f"2: {nozzle1}\n{_('Temp (°C)')}: {str(ext1_temp)}\n{_('Material')}: {mat1}" + "\n",
                    "printer.print.start",
                    params
                )
            except Exception as e:
                print(f"Error: {e}")
                return self._screen.show_popup_message(_("An error has occurred"), level=3)