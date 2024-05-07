from datetime import datetime, timedelta
from sv_includes import functions as sv_func
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
        self.menu = ['hepa_manage_panel']

        self.dates_str = [
            _("Year"),
            _("Month"),
            _("Day")
        ]

        grid = self._gtk.HomogeneousGrid()

        self.above_text = Gtk.Label(f'\n{_("The Filter must be changed every 6 months.")}\n')

        self.below_text = Gtk.Label(f'\n{_("Last date the filter was replaced:")} {self.date_in_text()}\n')

        self.content.add(self.above_text)
        self.content.add(self.below_text)

        self.confirm_replace_btn = self._gtk.Button("complete", _("I have already replaced the filter."), "color3")
        self.replace_later_btn = self._gtk.Button("clock", _("I will replace it later."), "color2")
        self.confirm_replace_btn.connect("clicked", self.confirm_replace)
        self.replace_later_btn.connect("clicked", self.replace_later)
        grid.attach(self.confirm_replace_btn, 0, 0, 1, 1)
        grid.attach(self.replace_later_btn, 0, 1, 1, 1)

        self.check_availability()

        self.labels['hepa_manage'] = self._gtk.HomogeneousGrid()
        self.labels['hepa_manage'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['hepa_manage'])


    def hepa_prop(self, prop: str):
        return sv_func.hepa_prop(prop_name=prop)

    def last_time_replaced(self, date_format='%Y-%m-%d'):
        try:
            date = self.hepa_prop("last-hepa-replacement")
            date = datetime.strptime(date, "%Y-%m-%d")
            return date.strftime(date_format)
        except:
            return "?"

    def date_in_text(self) -> str:
        return f"{self.date_fmt('%d')} {self.date_fmt('%m')} {self.date_fmt('%Y')}"

    def date_fmt(self, format) -> str:
        if format == '%d':
            r = 2
        elif format == '%m':
            r = 1
        else:
            r = 0
        return f"{self.dates_str[r][0]}: {self.last_time_replaced(date_format=format)}"

    def check_availability(self):
        if sv_func.valid_hepa():
            self.confirm_replace_btn.set_sensitive(False)

    def replace_later(self, button):
        for _ in range(0, 3):
            self._screen._menu_go_back()

    def confirm_replace(self, button):
        path = os.path.join("/home", "pi", "SyncraftCore")
        os.system(f"cd {path} && python3 -m core.hepa renew")
        self._screen.reload_panels()