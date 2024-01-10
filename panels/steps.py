from ks_includes.questions import Question
from ks_includes.questions import questions
import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.page: int = 0

        grid = self._gtk.HomogeneousGrid()

        self.labels['text'] = Gtk.Label(f"\n{_('Click to navigate between Images')}\n")
        self.content.add(self.labels['text'])
        
        self.above = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.spacer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.spacer.set_vexpand(True)
        self.spacer.set_hexpand(True)
        self.spacer.set_halign(Gtk.Align.CENTER) 

        self.place_image()

        self.content.add(self.above)
        
    def create_image_button(self, image_path, box, universal=True):
        self.event_box = Gtk.EventBox()
        image = self._gtk.Image(image_path, self._gtk.content_width * 7, self._gtk.content_height * .7, universal=universal)
        self.event_box.add(image)
        self.event_box.connect("button-press-event", self.on_image_clicked)
        box.pack_start(self.event_box, True, True, 8)

    def place_image(self):

        images_amount: int = len(self._config.get_question().images)

        try:
            self.content.remove(self.above)
            self.above.remove(self.event_box)
        except:
            pass

        if self.page <= 0:
            self.create_image_button(self.image_name(), self.above)
            self.page += 1
        elif self.page in range(1, images_amount):
            self.create_image_button(self.image_name(), self.above)
            self.page += 1
        else:
            self.page = 0
            self.create_image_button("complete", self.above, universal=False)

        self.content.add(self.above)
        self.content.show_all()


    def on_image_clicked(self, widget, event):
        self.place_image()

    def image_name(self) -> str:
        return f"help-{(self._config.get_question()).images[self.page]}"
    