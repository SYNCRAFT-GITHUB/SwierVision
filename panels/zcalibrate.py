import logging
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):
    widgets = {}
    distances = ['.01', '.05', '.1', '.5', '1', '5']
    distance = distances[-2]

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.z_offset = None
        self.probe = self._printer.get_probe()
        if self.probe:
            self.z_offset = float(self.probe['z_offset'])
        logging.info(f"Z offset: {self.z_offset}")
        self.widgets['zposition'] = Gtk.Label(label="Z: ?")

        pos = self._gtk.HomogeneousGrid()
        pos.attach(self.widgets['zposition'], 0, 1, 2, 1)
        if self.z_offset is not None:
            self.widgets['zoffset'] = Gtk.Label(label="?")
            pos.attach(Gtk.Label(_("Probe Offset") + ": "), 0, 2, 2, 1)
            pos.attach(Gtk.Label(_("Saved")), 0, 3, 1, 1)
            pos.attach(Gtk.Label(_("New")), 1, 3, 1, 1)
            pos.attach(Gtk.Label(f"{self.z_offset:.3f}"), 0, 4, 1, 1)
            pos.attach(self.widgets['zoffset'], 1, 4, 1, 1)
        self.buttons = {
            'zpos': self._gtk.Button('z-farther', _("Raise Nozzle"), 'color4'),
            'zneg': self._gtk.Button('z-closer', _("Lower Nozzle"), 'color1'),
            'start': self._gtk.Button('resume', _("Start"), 'color3'),
            'complete': self._gtk.Button('complete', _('Accept'), 'color3'),
            'cancel': self._gtk.Button('cancel', _('Abort'), 'color2'),
        }
        self.buttons['zpos'].connect("clicked", self.move, "+")
        self.buttons['zneg'].connect("clicked", self.move, "-")
        self.buttons['complete'].connect("clicked", self.accept)
        self.buttons['cancel'].connect("clicked", self.abort)

        self.buttons['start'].connect("clicked", self.start_calibration)

        distgrid = Gtk.Grid()
        for j, i in enumerate(self.distances):
            self.widgets[i] = self._gtk.Button(label=f"{i}{_('mm')}")
            self.widgets[i].set_direction(Gtk.TextDirection.LTR)
            self.widgets[i].connect("clicked", self.change_distance, i)
            ctx = self.widgets[i].get_style_context()
            if (self._screen.lang_ltr and j == 0) or (not self._screen.lang_ltr and j == len(self.distances) - 1):
                ctx.add_class("distbutton_top")
            elif (not self._screen.lang_ltr and j == 0) or (self._screen.lang_ltr and j == len(self.distances) - 1):
                ctx.add_class("distbutton_bottom")
            else:
                ctx.add_class("distbutton")
            if i == self.distance:
                ctx.add_class("distbutton_active")
            distgrid.attach(self.widgets[i], j, 0, 1, 1)

        distances = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        distances.pack_start(distgrid, True, True, 0)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.attach(self.buttons['zpos'], 0, 0, 1, 1)
        grid.attach(self.buttons['zneg'], 0, 1, 1, 1)
        grid.attach(self.buttons['start'], 1, 0, 1, 1)
        grid.attach(pos, 1, 1, 1, 1)
        grid.attach(self.buttons['complete'], 2, 0, 1, 1)
        grid.attach(self.buttons['cancel'], 2, 1, 1, 1)
        grid.attach(distances, 0, 2, 3, 1)
        self.content.add(grid)

    def start_calibration(self, widget):
        self.buttons['start'].set_sensitive(False)
        self._screen._ws.klippy.gcode_script("PROBE_CALIBRATE")

    def screws_method(self):
        self.menu_item_clicked(widget=None, item={
            "name": _("Calibrate"),
            "panel": "screws_adjust"
        })

    def activate(self):
        if self._printer.get_stat("manual_probe", "is_active"):
            self.buttons_calibrating()
        else:
            self.buttons_not_calibrating()

    def process_update(self, action, data):
        if action == "notify_status_update":
            if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
                self.widgets['zposition'].set_text("Z: ?")
            elif "gcode_move" in data and "gcode_position" in data['gcode_move']:
                self.update_position(data['gcode_move']['gcode_position'])
            if "manual_probe" in data:
                if data["manual_probe"]["is_active"]:
                    self.buttons_calibrating()
                else:
                    self.buttons_not_calibrating()
        elif action == "notify_gcode_response":
            if "out of range" in data.lower():
                self._screen.show_popup_message(data)
                logging.info(data)
            elif "fail" in data.lower() and "use testz" in data.lower():
                self._screen.show_popup_message(_("Failed, adjust position first"))
                logging.info(data)
        return

    def update_position(self, position):
        self.widgets['zposition'].set_text(f"Z: {position[2]:.3f}")
        if self.z_offset is not None:
            self.widgets['zoffset'].set_text(f"{abs(position[2] - self.z_offset):.3f}")

    def change_distance(self, widget, distance):
        logging.info(f"### Distance {distance}")
        self.widgets[f"{self.distance}"].get_style_context().remove_class("distbutton_active")
        self.widgets[f"{distance}"].get_style_context().add_class("distbutton_active")
        self.distance = distance

    def move(self, widget, direction):
        self._screen._ws.klippy.gcode_script(f"TESTZ Z={direction}{self.distance}")

    def abort(self, widget):
        logging.info("Aborting calibration")
        self._screen._ws.klippy.gcode_script("ABORT")
        self.buttons_not_calibrating()
        self._screen._menu_go_back()

    def accept(self, widget):
        self._screen._ws.klippy.gcode_script("IDEX_NOZZLE_CHECK")
        message: str = _("Nozzle height will be checked.") + "\n\n" \
        + _("If not properly leveled, perform a mechanical calibration.")
        self._screen.show_popup_message(message, level=4)
        logging.info("Accepting Z position")
        self._screen._ws.klippy.gcode_script("ACCEPT")

    def buttons_calibrating(self):
        self.buttons['start'].get_style_context().remove_class('color3')
        self.buttons['start'].set_sensitive(False)

        self.buttons['zpos'].set_sensitive(True)
        self.buttons['zpos'].get_style_context().add_class('color4')
        self.buttons['zneg'].set_sensitive(True)
        self.buttons['zneg'].get_style_context().add_class('color1')
        self.buttons['complete'].set_sensitive(True)
        self.buttons['complete'].get_style_context().add_class('color3')
        self.buttons['cancel'].set_sensitive(True)
        self.buttons['cancel'].get_style_context().add_class('color2')

    def buttons_not_calibrating(self):
        self.buttons['start'].get_style_context().add_class('color3')
        self.buttons['start'].set_sensitive(True)

        self.buttons['zpos'].set_sensitive(False)
        self.buttons['zpos'].get_style_context().remove_class('color4')
        self.buttons['zneg'].set_sensitive(False)
        self.buttons['zneg'].get_style_context().remove_class('color1')
        self.buttons['complete'].set_sensitive(False)
        self.buttons['complete'].get_style_context().remove_class('color3')
        self.buttons['cancel'].set_sensitive(False)
        self.buttons['cancel'].get_style_context().remove_class('color2')
