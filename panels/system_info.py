import subprocess
import logging
import platform
import getmac
import socket
import gi
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['system_info']

        self.image = self._gtk.Image("settings", self._gtk.content_width * .4, self._gtk.content_height * .4)
        self.core_path = os.path.join('/home', 'pi', 'SyncraftCore')
        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        self.about_btn = self._gtk.Button("info-bubble", _("About"), None, 1, Gtk.PositionType.LEFT)

        self.about_btn.connect("clicked", self.menu_item_clicked, {
            "name": _("About"),
            "panel": "about_tab"
        })

        self.content.add(self.info)

        self.text: str = f"""
        {_('Hostname')}: {socket.gethostname()}
        {_('Version')}: {platform.release()}
        {_('Mac')}: {getmac.get_mac_address()}
        {_('Birth')}: {self.getProp("birth", "?")}
        {_('HEPA Replacements')}: {self.getProp("hepa-count", "?")}
        {_('SyncraftCore')}: {os.path.exists(self.core_path)}
        """

        self.labels['text'] = Gtk.Label(f"{self.text}")
        self.labels['text'].set_halign(Gtk.Align.CENTER)
        self.labels['text'].set_valign(Gtk.Align.CENTER)

        self.content.add(self.labels['text'])
        self.content.add(self.about_btn)

        grid = self._gtk.HomogeneousGrid()

        self.labels['system_info'] = self._gtk.HomogeneousGrid()
        self.labels['system_info'].attach(grid, 0, 0, 2, 2)
        self.content.add(self.labels['system_info'])

    def getProp(self, prop_name, if_fail):
        try:
            with open(os.path.join(self.core_path, 'core', 'info.yaml'), 'r') as prop:
                prop = yaml.safe_load(prop)
                return prop.get(prop_name)
        except:
            return if_fail

    def get_mac_address(self, ip_address):
        arp_command = ['arp', '-n', ip_address]
        output = subprocess.check_output(arp_command).decode()
        mac_address = output.split()[3]
        return mac_address
