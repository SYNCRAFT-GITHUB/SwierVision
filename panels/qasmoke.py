import logging
import glob
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes as Gcode
from sv_includes.screen_panel import ScreenPanel

class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['qasmoke_room']

        self.buttons = {}

        grid = self._gtk.HomogeneousGrid()

        self.gridattach(gridvariable=grid)

        self.labels['qasmoke_room'] = self._gtk.HomogeneousGrid()
        self.labels['qasmoke_room'].attach(grid, 0, 0, 1, 3)

        self.content.remove(self.labels['qasmoke_room'])
        self.content.add(self.labels['qasmoke_room'])

        self.storegrid = grid
        

    def gridattach(self, gridvariable):

        repeat_three: int = 0
        i: int = 0

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(gridvariable)
        self.content.add(scroll)

        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        panel_list = sorted(glob.glob(os.path.join(current_script_dir, '*')))

        ignore_list = ["__init__", "__pycache__", "qasmoke"]

        for panel in panel_list:
            panel_name = os.path.basename(panel)
            panel_name = os.path.splitext(panel_name)[0]
            if panel_name in ignore_list:
                continue

            index_button = self._gtk.Button("door", panel_name, "color3")
            index_button.connect("clicked", self.teleport, panel_name)
            gridvariable.attach(index_button, repeat_three, i, 1, 1)
            
            if repeat_three == 3:
                repeat_three = 0
                i += 1
            else:
                repeat_three += 1
            
    def teleport(self, button, panel):
        try:
            self.menu_item_clicked(widget=panel, item={
                    "name": "QASMOKE",
                    "panel": panel
                })
        except:
            msg = _("An error has occurred")
            self._screen.show_popup_message(msg, level=2)