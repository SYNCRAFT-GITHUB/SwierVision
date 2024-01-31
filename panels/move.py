import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel

SPEED = 23_350
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['move']

        grid = self._gtk.HomogeneousGrid()

        self.buttons = {
            "ext-up": self._gtk.Button("key-up", None, "color3"),
            "ext-down": self._gtk.Button("key-down", None, "color2"),
            "bed-up": self._gtk.Button("arrow-up", None, "color3"),
            "bed-down": self._gtk.Button("arrow-down", None, "color2"),
            "left": self._gtk.Button("key-left", None, "color1"),
            "right": self._gtk.Button("key-right", None, "color1"),
            "home": self._gtk.Button("home", _("Home All"), None),
            "off": self._gtk.Button("motor-off", _("Disable Motors"), None),
            "gear": self._gtk.Button("settings", _("Extras"), None)
        }

        grid.attach(self.buttons["ext-up"], 1, 0, 1, 1)
        grid.attach(self.buttons["ext-down"], 1, 1, 1, 1)
        grid.attach(self.buttons["left"], 0, 1, 1, 1)
        grid.attach(self.buttons["right"], 2, 1, 1, 1)

        grid.attach(self.buttons["bed-up"], 3, 0, 1, 1)
        grid.attach(self.buttons["bed-down"], 3, 1, 1, 1)

        grid.attach(self.buttons["home"], 2, 0, 1, 1)
        grid.attach(self.buttons["off"], 2, 2, 1, 1)
        grid.attach(self.buttons["gear"], 3, 2, 1, 1)

        self.ext_feeder = {
            'extruder1': '1',
            'extruder': '0'
        }

        for i, extruder in enumerate(self._printer.get_tools()):
            self.buttons[extruder] = self._gtk.Button(f"extruder-{i+1}", None, None, 1.35, Gtk.PositionType.TOP, 1)
            self.buttons[extruder].connect("clicked", self.change_extruder, extruder)
            if self.ext_feeder[extruder] != self.ext():
                self.buttons[extruder].set_property("opacity", 0.3)
            grid.attach(self.buttons[extruder], i, 2, 1, 1)

        self.buttons["home"].connect("clicked", self.home_all)
        self.buttons["gear"].connect("clicked", self.menu_item_clicked, {
                "name": _("Move"),
                "panel": "move_gear"
            })

        self.buttons["ext-up"].connect("clicked", self.move_extruder, UP)
        self.buttons["ext-down"].connect("clicked", self.move_extruder, DOWN)
        self.buttons["bed-up"].connect("clicked", self.move_bed, UP)
        self.buttons["bed-down"].connect("clicked", self.move_bed, DOWN)
        self.buttons["left"].connect("clicked", self.move_extruder, LEFT)
        self.buttons["right"].connect("clicked", self.move_extruder, RIGHT)
        self.buttons["off"].connect("clicked", self._screen._confirm_send_action,
                                           _("Are you sure you wish to disable motors?"),
                                           "printer.gcode.script", {"script": "M18"})

        self.labels['move'] = self._gtk.HomogeneousGrid()
        self.labels['move'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['move'])

    def home_all(self, button):
        self._screen._ws.klippy.gcode_script(KlippyGcodes.HOME_ALL)

    def ext(self):
        return self._config.variables_value_reveal('active_carriage', isString=False)

    def change_extruder(self, widget, extruder):
        logging.info(f"Changing extruder to {extruder}")
        self._screen._ws.klippy.gcode_script(f"T{self._printer.get_tool_number(extruder)}")

    def move_extruder(self, button, direction):
        if direction == UP:
            self._screen._ws.klippy.gcode_script(f"G1 Y300 F{SPEED}")
            logging.debug("Moving Extruder Up")
        elif direction == DOWN:
            self._screen._ws.klippy.gcode_script(f"G1 Y0 F{SPEED}")
            logging.debug("Moving Extruder Down")
            self._screen._ws.klippy.gcode_script(f"G1 X0 F{SPEED}")
            logging.debug("Moving Extruder to the Left")
        elif direction == RIGHT:
            if self.ext() == 0:
                self._screen._ws.klippy.gcode_script(f"G1 X280 F{SPEED}")
            else:
                self._screen._ws.klippy.gcode_script(f"G1 X320 F{SPEED}")
            logging.debug("Moving Extruder to the Right")
        elif direction == LEFT:
            if self.ext() == 0:
                self._screen._ws.klippy.gcode_script(f"G1 X-15 F{SPEED}")
            else:
                self._screen._ws.klippy.gcode_script(f"G1 X25 F{SPEED}")
            logging.debug("Moving Extruder to the Left")
        else:
            print("unknown direction")

    def move_bed(self, button, direction):
        if direction == UP:
            self._screen._ws.klippy.gcode_script(f"G1 Z0 F{SPEED}")
            logging.debug("Moving Bed Up")
        elif direction == DOWN:
            self._screen._ws.klippy.gcode_script(f"G1 Z340 F{SPEED}")
            logging.debug("Moving Bed Down")
        else:
            print("unknown direction")

    def process_busy(self, busy):
        for button in self.buttons:
            if button == "gear":
                continue
            else:
                self.buttons[button].set_sensitive(not busy)

    def process_update(self, action, data):

        if action == "notify_busy":
            self.process_busy(data)
            return
        if action != "notify_status_update":
            return

        for extruder in self._printer.get_tools():
            if self.ext_feeder[extruder] != self.ext():
                self.buttons[extruder].set_property("opacity", 0.3)
            else:
                self.buttons[extruder].set_property("opacity", 1.0)