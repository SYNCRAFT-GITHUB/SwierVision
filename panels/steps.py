from sv_includes.topic import Topic
from sv_includes.topic import topics
import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.page: int = 0

        grid = self._gtk.HomogeneousGrid()

        self.labels['text'] = Gtk.Label(f"\n{_('Click to navigate between Images')}\n")
        self.content.add(self.labels['text'])
        
        self.container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.spacer.set_vexpand(True)
        self.spacer.set_hexpand(True)
        self.spacer.set_halign(Gtk.Align.CENTER) 

        self.place_image()

        self.content.add(self.container)
        
    def create_image_button(self, image_path, box, univ=True):
        self.event_box = Gtk.EventBox()
        image = self._gtk.Image(image_path, self._gtk.content_width * 7, self._gtk.content_height * .7, universal=univ)
        self.event_box.add(image)
        self.event_box.connect("button-press-event", self.on_image_clicked)
        box.pack_start(self.event_box, True, True, 8)

    def place_image(self):

        images_amount: int = len(self._config.get_topic().images)

        try:
            self.content.remove(self.container)
            self.container.remove(self.event_box)
        except:
            pass

        if self.page <= 0:
            self.create_image_button(self.image_name(), self.container)
            self.page += 1
        elif self.page in range(1, images_amount):
            self.create_image_button(self.image_name(), self.container)
            self.page += 1
        else:
            self.page = 0
            self.create_image_button("complete", self.container, univ=False)

        self.content.add(self.container)
        self.content.show_all()


    def on_image_clicked(self, widget, event):
        self.place_image()

    def image_name(self) -> str:
        return f"help-{(self._config.get_topic()).images[self.page]}"
    