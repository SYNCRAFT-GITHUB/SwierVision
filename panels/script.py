import logging
import gi
import subprocess
import socket
import os
import shutil
import datetime
import time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):
        
        self.fix_option: str = self._config.get_fix_option()

        super().__init__(screen, title)
        self.menu = ['execute_script_panel']
        
        self.buttons = {
            'CONFIRM': self._gtk.Button("complete", _("Confirm"), "color1"),
            'EXECUTE': self._gtk.Button("resume", _("Start"), "color2"),
        }
        self.buttons['CONFIRM'].connect("clicked", self.confirm)
        self.buttons['EXECUTE'].connect("clicked", self.execute)

        text = Gtk.Label()
        text.set_markup(f"<b>{_('Please confirm before proceeding')}</b>\n")
        text.set_hexpand(True)
        text.set_halign(Gtk.Align.CENTER)
        text.set_vexpand(True)
        text.set_valign(Gtk.Align.CENTER)
        text.set_line_wrap(True)
        text.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

        self.buttons['EXECUTE'].set_sensitive(False)

        grid = self._gtk.HomogeneousGrid()

        self.image = self._gtk.Image("gear", self._gtk.content_width * .4, self._gtk.content_height * .4)
        self.info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.info.pack_start(self.image, True, True, 8)

        grid.attach(text, 0, 0, 3, 1)
        grid.attach(self.buttons['CONFIRM'], 0, 1, 1, 3)
        grid.attach(self.buttons['EXECUTE'], 1, 1, 2, 3)

        self.labels['execute_script_panel'] = self._gtk.HomogeneousGrid()
        self.labels['execute_script_panel'].attach(grid, 0, 0, 1, 2)
        self.content.add(self.labels['execute_script_panel'])

    
    def confirm(self, button):
        self.buttons['EXECUTE'].set_sensitive(True)
        self.buttons['CONFIRM'].set_sensitive(False)

    def execute(self, button):

        fix_option = self._config.get_fix_option()

        self.buttons['EXECUTE'].set_sensitive(False)
        self.buttons['CONFIRM'].set_sensitive(True)

        def core_script(core_script_dir: str, usb = False, web=False):

            usb_machine_path: str = os.path.join('/home', 'pi', 'printer_data', 'gcodes', 'USB')
            if usb:
                if os.path.exists(usb_machine_path):
                    if len(os.listdir(usb_machine_path)) == 0:
                        message: str = _("USB not inserted into Printer")
                        self._screen.show_popup_message(message, level=2)
                        return None
                else:
                    message: str = _("An error has occurred")
                    self._screen.show_popup_message(message, level=2)
                    return None
            if not self._config.internet_connection() and web:
                message: str = _("This procedure requires internet connection")
                self._screen.show_popup_message(message, level=2)
                return None
            try:
                if '.sh' in core_script_dir:
                    subprocess.call(['bash', core_script_dir])

                if '.py' in core_script_dir:
                    subprocess.run(["python3", core_script_dir], check=True)
            except:
                message: str = _("Error")
                self._screen.show_popup_message(message, level=2)
                return None

        core = os.path.join('/home', 'pi', 'SyncraftCore')
        
        class SCRIPT:
            class FIXES:
                MAINSAIL = os.path.join(core, 'fixes', 'mainsail.sh')
                CAMERA = os.path.join(core, 'fixes', 'camera.sh')
                LIGHT = os.path.join(core, 'fixes', 'light.sh')
                MOONRAKER = os.path.join(core, 'fixes', 'moonraker.sh')
                FLASH = os.path.join(core, 'fixes', 'flash.sh')
                REFLASH = os.path.join(core, 'fixes', 'reflash.sh')
            class UPDATE:
                DOWNLOAD = os.path.join(core, 'core', 'update.py')
                APPLY = os.path.join(core, 'state', 'upgrade', 'apply.sh')
            class REVERT:
                APPLY = os.path.join(core, 'state', 'downgrade', 'apply.sh')
            class USB:
                UPDATE = os.path.join(core, 'usb', 'update.sh')
                SLICER = os.path.join(core, 'usb', 'slicer','transfer.sh')
                LOGS = os.path.join(core, 'usb', 'export_logs.sh')
            class MACHINE:
                APPLY = os.path.join(core, 'machine', 'apply.sh')
                SXUSB = os.path.join(core, 'machine', 'usbsxservice', 'apply.sh')

        if (fix_option == "FIX_MAINSAIL"):
            core_script(SCRIPT.FIXES.MAINSAIL, web=True)
            return

        if (fix_option == "FIX_CAMERA"):
            core_script(SCRIPT.FIXES.CAMERA, web=True)
            return

        if (fix_option == "FIX_LIGHT"):
            core_script(SCRIPT.FIXES.LIGHT, web=True)
            return

        if (fix_option == "FIX_MOONRAKER"):
            core_script(SCRIPT.FIXES.MOONRAKER, web=True)
            return

        if (fix_option == "UPDATE_USB"):
            core_script(SCRIPT.USB.UPDATE)
            os.system('sudo reboot')
            return
        
        if (fix_option == "UPDATE_ALL"):
            core_script(SCRIPT.UPDATE.DOWNLOAD)
            core_script(SCRIPT.UPDATE.APPLY)
            os.system('sudo reboot')
            return

        if (fix_option == "REVERT_ALL"):
            core_script(SCRIPT.REVERT.APPLY)
            time.sleep(5)
            return

        if (fix_option == "USB_SLICER"):
            core_script(SCRIPT.USB.SLICER)
            self._screen.reload_panels()
            return

        if (fix_option == "USB_LOGS"):
            core_script(SCRIPT.USB.LOGS)
            self._screen.reload_panels()
            return

        if (fix_option == "CLEAR_GCODES"):
            core_script(SCRIPT.MACHINE.SXUSB)
            os.system('sudo reboot')
            return

        if (fix_option == "FLASH_BOARD"):
            core_script(SCRIPT.FIXES.FLASH)
            return

        if (fix_option == "REFLASH_BOARD"):
            core_script(SCRIPT.FIXES.REFLASH)
            return
