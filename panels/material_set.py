import logging
import json
import os
import re

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes as Gcode
from sv_includes.screen_panel import ScreenPanel
from panels.material_load import PrinterMaterial
from panels.material_load import CustomPrinterMaterial

def read_materials_from_json(file_path: str, custom: bool = False):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return_array = []
            for item in data:
                if custom:
                    material = CustomPrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        compatible=item['compatible'],
                        temp=item['temp'],
                    )
                    return_array.append(material)
                else:
                    material = PrinterMaterial(
                        name=item['name'],
                        code=item['code'],
                        m_id=item['id'],
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
        self.menu = ['material_set_menu']

        if self._config.get_extruder_option() == "extruder":
            self.nozzle = self._config.variables_value_reveal('nozzle0')
        else:
            self.nozzle = self._config.variables_value_reveal('nozzle1')

        self.materials_json_path = self._config.materials_path(custom=False)
        self.custom_json_path = self._config.materials_path(custom=True)

        self.materials = read_materials_from_json(self.materials_json_path)
        self.custom_materials = read_materials_from_json(self.custom_json_path, custom=True)

        self.buttons = {}

        self.texts = [
            _("This material is considered experimental for the selected Extruder."),
            _("Using an untested material may lead to inaccurate print results.")
            ]

        grid = self._gtk.HomogeneousGrid()

        self.gridattach(gridvariable=grid)

        self.labels['material_set_menu'] = self._gtk.HomogeneousGrid()
        self.labels['material_set_menu'].attach(grid, 0, 0, 1, 3)

        self.content.remove(self.labels['material_set_menu'])
        self.content.add(self.labels['material_set_menu'])

        self.storegrid = grid
        

    def gridattach(self, gridvariable):

        repeat_three: int = 0
        i: int = 0

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(gridvariable)
        self.content.add(scroll)

        try:
            iter(self.materials)
        except:
            self.materials = []

        for material in self.materials:

            if self.nozzle in material.compatible:
                index_button = self._gtk.Button("circle-green", material.name, "color3")
                index_button.connect("clicked", self.confirm_set_default, material.code, material.m_id)
                gridvariable.attach(index_button, repeat_three, i, 1, 1)
                
                if repeat_three == 4:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1

        try:
            iter(self.custom_materials)
        except:
            self.custom_materials = []

        for material in self.custom_materials:
        
            if self.nozzle in material.compatible:
                allow = self.allow_custom(material)

                if allow:
                    index_button = self._gtk.Button("circle-purple", material.name, "color2")
                    index_button.connect("clicked", self.confirm_set_custom)
                else:
                    index_button = self._gtk.Button("invalid", _('Invalid'), "color2")
                    index_button.connect("clicked", self.set_invalid_material)

                gridvariable.attach(index_button, repeat_three, i, 1, 1)

                if repeat_three == 4:
                    repeat_three = 0
                    i += 1
                else:
                    repeat_three += 1
                

        for material in self.materials:

            show_experimental = self._config.get_main_config().getboolean('show_experimental_material', False)
            allowed_for_experimental = ["Standard 0.25mm", "Standard 0.4mm", "Standard 0.8mm"]
            
            if self.nozzle in material.experimental and self.nozzle in allowed_for_experimental:
                index_button = self._gtk.Button("circle-orange", material.name, "color1")
                index_button.connect("clicked", self.confirm_set_experimental, material.code, material.m_id)
                if show_experimental:
                    gridvariable.attach(index_button, repeat_three, i, 1, 1)
                    if repeat_three == 4:
                        repeat_three = 0
                        i += 1
                    else:
                        repeat_three += 1

            if material.m_id == self.materials[-1].m_id:
                size: int = 1
                index: int = repeat_three
                while index != 4:
                    size += 1
                    index += 1
                index_button = self._gtk.Button("circle-white", _("Empty"), "color3")
                index_button.connect("clicked", self.confirm_set_empty)
                gridvariable.attach(index_button, repeat_three, i, size, 1)

    def allow_custom(self, material: CustomPrinterMaterial) -> bool:
        pattern = r'[!@#$%^&*()_+{}\[\]:;<>,.?~\\-]'
        name = material.name
        code = material.code
        if not len(name) in range(3, 8):
            return False
        if re.search(pattern, name):
            return False
        if re.search(pattern, code):
            return False
        if not material.temp in range(5, 351):
            return False
        return True

    def ext(self) -> int:
        return 0 if self._config.get_extruder_option() == "extruder" else 1

    def confirm_set_default(self, widget, code, m_id):
        self._screen._ws.klippy.gcode_script(Gcode.change_material(m=code, ext=self.ext(), m_id=m_id))
        self._screen._menu_go_back()

    def confirm_set_empty(self, widget):
        self._screen._ws.klippy.gcode_script(Gcode.change_material(m='empty', ext=self.ext(), m_id='empty'))
        self._screen._menu_go_back()

    def confirm_set_experimental(self, widget, code, m_id):
        script = Gcode.change_material(m=code, ext=self.ext(), m_id=m_id)
        params = {"script": script}
        self._screen._confirm_send_action(
            None,
            self.texts[0] + "\n\n" + self.texts[1] + "\n\n",
            "printer.gcode.script",
            params
        )
        self._screen._menu_go_back()

    def confirm_set_custom(self, widget):
        script = Gcode.change_material(m='GENERIC', ext=self.ext(), m_id='basic')
        params = {"script": script}
        self._screen._confirm_send_action(
            None,
            self.texts[1] + "\n\n",
            "printer.gcode.script",
            params
        )
        self._screen._menu_go_back()

    def set_invalid_material(self, widget=None):
        message: str = _("Incompatible Material")
        self._screen.show_popup_message(message, level=3)
        return None