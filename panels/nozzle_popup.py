import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.extruder_option = self._config.get_extruder_option()

        grid = self._gtk.HomogeneousGrid()

        self.labels['text'] = Gtk.Label(f"\n")
        self.content.add(self.labels['text'])
        
        self.above = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.below = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.spacer.set_vexpand(True)
        self.spacer.set_hexpand(False)
        self.spacer.set_halign(Gtk.Align.CENTER) 

        self.create_image_button("nozzle-ST025", self.above, "Standard 0.25mm")
        self.create_image_button("nozzle-ST04", self.above, "Standard 0.4mm")
        self.create_image_button("nozzle-ST08", self.above, "Standard 0.8mm")
        self.create_image_button("nozzle-METAL04", self.below, "Metal 0.4mm")
        
        if 'two' in self._config.get_spool_option():
            self.create_image_button("extruder-2", self.below, None)
        else:
            self.create_image_button("extruder-1", self.below, None)

        self.create_image_button("nozzle-FIBER06", self.below, "Fiber 0.6mm")

        self.content.add(self.above)
        self.content.add(self.below)
        
    def create_image_button(self, image_path, box, nozzle):
        event_box = Gtk.EventBox()
        image = self._gtk.Image(image_path, self._gtk.content_width * 4, self._gtk.content_height * .4)
        event_box.add(image)
        if nozzle:
            event_box.connect("button-press-event", self.on_image_clicked, nozzle)
        box.pack_start(event_box, True, True, 8)

    def on_image_clicked(self, widget, event, nozzle):
        self.nozzlegcodescript(widget, nozzle)
        self._screen.delete_temporary_panels(exclude="nozzle_popup")
        self.menu_item_clicked(widget="material_popup", item={
                "name": _("Select the Material"),
                "panel": "material_popup"
            })

    def nozzlegcodescript(self, widget, nozzle: str):
        if 'two' in self._config.get_spool_option():
            self._screen._ws.klippy.gcode_script(f"NOZZLE_SET CARRIAGE=1 NZ='{nozzle}'")
        else:
            self._screen._ws.klippy.gcode_script(f"NOZZLE_SET CARRIAGE=0 NZ='{nozzle}'")

    def process_update(self, action, data):

        for x in self._printer.get_filament_sensors():
            try:
                if x in data:
                    if 'enabled' in data[x]:
                        self._printer.set_dev_stat(x, "enabled", data[x]['enabled'])
                    if 'filament_detected' in data[x]:
                        self._printer.set_dev_stat(x, "filament_detected", data[x]['filament_detected'])
                        if self._printer.get_stat(x, "enabled"):
                            if not data[x]['filament_detected'] and x == self._config.get_spool_option():
                                self._config.replace_filament_activity(x, "empty")
                                self._screen._menu_go_back()
            except:
                pass