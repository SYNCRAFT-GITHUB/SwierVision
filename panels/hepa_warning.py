from datetime import datetime, timedelta
import logging
import os
import yaml
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['hepa_warning']

        self.page: int = 0

        self.texts = [
            _("It looks like your HEPA filter needs to be replaced!"),
            _("The Filter must be changed every 6 months."),
            _("Some materials are harmful if they are not filtered."),
            _("Last date the filter was replaced:"),
            _("Times the filter was replaced:")
        ]

        self.dates_str = [
            _("Year"),
            _("Month"),
            _("Day")
        ]

        self.image = self._gtk.Image("hepa-warning", self._gtk.content_width * 4, self._gtk.content_height * .6, universal=True)

        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        self.content.add(self.info)

        self.labels['text'] = Gtk.Label(f"\n{self.texts[self.page]}\n\n\n")
        self.labels['text'].set_line_wrap(True)
        self.labels['text'].set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)
        
        self.content.add(self.labels['text'])

        self.buttons = {
            'OK': self._gtk.Button("arrow-right", None, None),
        }
        self.buttons['OK'].connect("clicked", self.update_screen)

        grid = self._gtk.HomogeneousGrid()

        grid.attach(self.buttons['OK'], 1, 0, 1, 1)

        self.labels['hepa_warning'] = self._gtk.HomogeneousGrid()
        self.labels['hepa_warning'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['hepa_warning'])

    def prop_dir(self) -> str:
        return "/Users/rafael/Desktop/wb/git/syncraftcore-master/core/info.yaml"

    def hepa_prop(self, prop_name: str):
        with open(self.prop_dir(), 'r') as prop:
            prop = yaml.safe_load(prop)
            try:
                return prop.get(prop_name)
            except:
                return "0000-00-00"

    def last_time_replaced(self, date_format='%Y-%m-%d'):
        try:
            date = self.hepa_prop("hepa-start")
            hepa_start = datetime.strptime(date, "%Y-%m-%d")
            days_to_remove = self.hepa_count() * 132
            last_time_replaced_date = hepa_start - timedelta(days=days_to_remove)
            return last_time_replaced_date.strftime(date_format)
        except:
            return "?"

    def hepa_count(self) -> int:
        try:
            return int(self.hepa_prop("hepa-count"))
        except:
            return 0

    def date_in_text(self) -> str:
        return f"""{self.dates_str[0]}: {self.last_time_replaced(date_format='%Y')} \
        {self.dates_str[1]}: {self.last_time_replaced(date_format='%m')} \
        {self.dates_str[2]}: {self.last_time_replaced(date_format='%d')}
        """

    def update_screen(self, button):

        if (self.page < 4):

            self.page += 1

            if self.page == 3:
                self.labels['text'].set_label(f"\n{self.texts[self.page]}\n{self.date_in_text()}\n")
            elif self.page == 4:
                self.labels['text'].set_label(f"\n{self.texts[self.page]} {self.hepa_count()}\n\n\n")
            else:
                self.labels['text'].set_label(f"\n{self.texts[self.page]}\n\n\n")

        if (self.page == 4):

            self.buttons['OK'].connect("clicked", self.menu_item_clicked, {
                "name": _("Main Menu"),
                "panel": "main_menu"
                })