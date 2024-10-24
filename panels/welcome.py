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
        self.menu = ['syncraft_panel']

        image = self._gtk.Image("bed-level", self._gtk.content_width * .53, self._gtk.content_height * .3)

        info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        info.pack_start(image, True, True, 8)

        #self.content.add(info)

        self.texts = [
            f'{_("Welcome to Syncraft")}',
            f'{_("Here are some recommended steps to get started")}',
            f'{_("If you want, you can adjust all of this later")}',
        ]

        for i, content in enumerate(self.texts):
            text = Gtk.Label(content)
            text.set_line_wrap(True)
            text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            text.set_halign(Gtk.Align.CENTER)
            text.set_valign(Gtk.Align.CENTER)
            markup = '<span size="xx-large">{}</span>'.format(content) if (i == 0) else '<span size="large">{}</span>'.format(content)
            text.set_markup(markup)
            self.content.pack_start(text, expand=True, fill=True, padding=3)
            self.content.add(text)

        self.buttons = {
            'STEP_01': self._gtk.Button("network", _("Connect"), "color3"),
            'STEP_02': self._gtk.Button ("accessibility", _("Accessibility"), "color1"),
            'STEP_03': self._gtk.Button("bed-level", _("Calibrate"), "color2"),
            'FINISH': self._gtk.Button("complete", _("Finish"), None),
        }
        self.buttons['STEP_01'].connect("clicked", self.menu_item_clicked, {
            "name": _("Network"),
            "panel": "network"
        })
        self.buttons['STEP_02'].connect("clicked", self.menu_item_clicked, {
            "name":_("Accessibility"),
            "panel": "settings"
        })
        self.buttons['STEP_03'].connect("clicked", self.menu_item_clicked, {
            "name": _("Calibrate"),
            "panel": "calibrate"
        })
        self.buttons['FINISH'].connect("clicked", self.finish_all)

        grid = self._gtk.HomogeneousGrid()

        for i, button in enumerate(self.buttons):
            if i < len(self.buttons)-1:
                grid.attach((self._gtk.Button(f"extruder-{i+1}", None, None)), i, 0, 1, 1)
            grid.attach(self.buttons[button], i, 1, 1, 2)

        self.labels['syncraft_panel'] = self._gtk.HomogeneousGrid()
        self.labels['syncraft_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['syncraft_panel'])

    def finish_all(self, button):
        self.set_bool_config_option(section="hidden", option="welcome", boolean=False)
        
        syncraftcore_path = os.path.join("/home", "pi", "SyncraftCore")
        if os.path.exists(syncraftcore_path):
            os.system(f"cd {syncraftcore_path} && python3 -m core.hepa reset")

        self._screen.reload_panels()