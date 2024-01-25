import logging
import socket
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['idex_offset_panel']
        self.distances = ['.01', '.02', '.05', '0.1', '0.2', '0.5']
        self.distance = self.distances[-2]

        self.x = self.y = 0.0

        grid = self._gtk.HomogeneousGrid()
        
        self.labels['idex_offset_panel'] = self._gtk.HomogeneousGrid()

        self.labels['xy'] = Gtk.Label(self.label_format())

        self.labels['reset'] = self._gtk.Button("refresh", None, None)
        self.labels['reset'].set_property("opacity", 0.5)
        self.labels['reset'].connect("clicked", self.reset_values)

        self.labels['ok'] = self._gtk.Button("complete", None, "color3")
        self.labels['ok'].connect("clicked", self.apply)

        self.labels['x+'] = self._gtk.Button("x-increase", None, "color1")
        self.labels['x-'] = self._gtk.Button("x-decrease", None, "color2")
        self.labels['x+'].connect("clicked", self.increment, True, False, False)
        self.labels['x-'].connect("clicked", self.decrease, True, False, False)

        self.labels['y+'] = self._gtk.Button("y-increase", None, "color1")
        self.labels['y-'] = self._gtk.Button("y-decrease", None, "color2")
        self.labels['y+'].connect("clicked", self.increment, False, True, False)
        self.labels['y-'].connect("clicked", self.decrease, False, True, False)

        grid.attach(self.labels['xy'], 1, 0, 1, 1)
        grid.attach(self.labels['reset'], 2, 0, 1, 1)
        grid.attach(self.labels['ok'], 2, 1, 1, 2)

        grid.attach(self.labels['x+'], 0, 1, 1, 1)
        grid.attach(self.labels['x-'], 0, 2, 1, 1)

        grid.attach(self.labels['y+'], 1, 1, 1, 1)
        grid.attach(self.labels['y-'], 1, 2, 1, 1)

        distgrid = Gtk.Grid()
        for j, i in enumerate(self.distances):
            self.labels[i] = self._gtk.Button(label=f"{i}{_('mm')}")
            self.labels[i].connect("clicked", self.change_distance, i)
            ctx = self.labels[i].get_style_context()
            if j == 0:
                ctx.add_class("distbutton_top")
            elif j == len(self.distances) - 1:
                ctx.add_class("distbutton_bottom")
            else:
                ctx.add_class("distbutton")
            if i == self.distance:
                ctx.add_class("distbutton_active")
            distgrid.attach(self.labels[i], j, 0, 1, 1)

            grid.attach(distgrid, 0, 3, 3, 1)

        self.labels['idex_offset_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['idex_offset_panel'])

    def change_distance(self, widget, distance):
        logging.info(f"### Distance {distance}")
        self.labels[f"{self.distance}"].get_style_context().remove_class("distbutton_active")
        self.labels[f"{distance}"].get_style_context().add_class("distbutton_active")
        self.distance = distance

    def label_format(self) -> str:
        return f"X: {self.x}\nY: {self.y}"

    def reset_values(self, widget):
        self.x = self.y = 0
        self.labels['xy'].set_label(self.label_format())

    def increment(self, widget, x=False, y=False):
        if x != False:
            self.x = round(self.x + float(self.distance), 3)
        if y != False:
            self.y = round(self.y + float(self.distance), 3)
        self.labels['xy'].set_label(self.label_format())

    def decrease(self, widget, x=False, y=False):
        if x != False:
            self.x = round(self.x - float(self.distance), 3)
        if y != False:
            self.y = round(self.y - float(self.distance), 3)
        self.labels['xy'].set_label(self.label_format())

    def apply(self, widget):
        self._screen._ws.klippy.gcode_script(KlippyGcodes.idex_offset(x=self.x, y=self.y))
        self.reset_values(widget=widget)
        self._screen._menu_go_back()