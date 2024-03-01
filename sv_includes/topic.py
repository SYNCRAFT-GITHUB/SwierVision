import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class Topic(Gtk.Window):
    def __init__(self, title, reference, images):
        self.title = title
        self.reference = reference
        self.images = images

topics = [
    Topic(
        title="Cutting the Filament Correctly",
        reference="cut-filament",
        images=[
            "cut-filament-1",
            "cut-filament-2",
            "cut-filament-3",
            "cut-filament-4"
            ]
    ),
    Topic(
        title="Connecting a Syncraft to the Mobile App",
        reference="obico",
        images=[
            "obico-1",
            "obico-2",
            "obico-3",
            "obico-4",
            "obico-5",              
            "obico-6",
            "obico-7",
            "obico-8",
            "obico-9"  
            ]
    ),
    Topic(
        title="Installing Cura Packages on MacOS",
        reference="cura-mac",
        images=[
            "cura-mac-1",
            "cura-mac-2",
            "cura-mac-3",
            "cura-mac-4",
            "cura-mac-5"
            ]
    ),
    Topic(
        title="Installing Cura Packages on Windows",
        reference="cura-win",
        images=[
            "cura-win-1",
            "cura-win-2",
            "cura-win-3"
            ]
    ),
]