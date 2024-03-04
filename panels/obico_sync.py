import logging
import shutil
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from sv_includes.KlippyGcodes import KlippyGcodes
from sv_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['obico_sync_panel']
        grid = self._gtk.HomogeneousGrid()

        self.focus = 1

        self.digits = {
            '1': None,
            '2': None,
            '3': None,
            '4': None,
            '5': None,
            '6': None,
        }

        self.labels["text"] = Gtk.Label(_("Enter the 6-digit verification code:"))
        grid.attach(self.labels["text"], 0, 0, 5, 1)

        self.labels["left_label"] = Gtk.Label(self.label_code(a=1, b=2))
        grid.attach(self.labels["left_label"], 1, 1, 1, 1)

        self.labels["middle_label"] = Gtk.Label(self.label_code(a=3, b=4))
        grid.attach(self.labels["middle_label"], 2, 1, 1, 1)

        self.labels["right_label"] = Gtk.Label(self.label_code(a=5, b=6))
        grid.attach(self.labels["right_label"], 3, 1, 1, 1)

        i = 1; j = 2
        for digit in range(1, 10):
            button = self._gtk.Button(None, str(digit), "color4")
            button.connect("clicked", self.add_digit, digit)
            grid.attach(button, i, j, 1, 1)
            i += 1
            if i % 4 == 0:
                i = 1
                j += 1
            del button
        del i, j

        self.labels["focus_left"] = self._gtk.Button("key-left", None, "color1", 0.60)
        self.labels["focus_left"].connect("clicked", self.focus_left)
        grid.attach(self.labels["focus_left"], 0, 2, 1, 1)

        self.labels["focus_right"] = self._gtk.Button("key-right", None, "color1", 0.60)
        self.labels["focus_right"].connect("clicked", self.focus_right)
        grid.attach(self.labels["focus_right"], 4, 2, 1, 1)

        self.labels["delete_all"] = self._gtk.Button(None, _("Clear"), "color2")
        self.labels["delete_all"].connect("clicked", self.delete_all)
        grid.attach(self.labels["delete_all"], 0, 3, 1, 1)

        self.labels["zero"] = self._gtk.Button(None, "0", "color4")
        self.labels["zero"].connect("clicked", self.add_digit, 0)
        grid.attach(self.labels["zero"], 0, 4, 1, 1)

        self.labels["help"] = self._gtk.Button("help", None, "color1", 0.70)
        self.labels["help"].connect("clicked", self.menu_item_clicked, {
            "name":_("Help"),
            "panel": "help"
        })
        grid.attach(self.labels["help"], 4, 3, 1, 1)

        self.labels["continue"] = self._gtk.Button("complete", None, "color3")
        self.labels["continue"].connect("clicked", self.finish)
        grid.attach(self.labels["continue"], 4, 4, 1, 1)

        self.content.add(grid)

    def focus_right(self, button):
        if self.focus == 6:
            self.focus = 1
        else:
            self.focus += 1
        self.update_labels()

    def focus_left(self, button):
        if self.focus == 1:
            self.focus = 6
        else:
            self.focus -= 1
        self.update_labels()

    def delete_all(self, button):
        for key in self.digits.keys():
            self.digits[key] = None
        self.focus = 1
        self.update_labels()

    def add_digit(self, button, digit):
        if self.focus in range(1, 7):
            self.digits[str(self.focus)] = digit
        if self.focus < 6:
            self.focus_right(button=None)
        else:
            self.focus = 0
        self.update_labels()

    def update_labels(self):
        self.labels["left_label"].set_label(self.label_code(a=1, b=2))
        self.labels["middle_label"].set_label(self.label_code(a=3, b=4))
        self.labels["right_label"].set_label(self.label_code(a=5, b=6))

    def label_code(self, a: int, b: int):
        text = ""
        for i in range(a, b+1):
            if self.digits[str(i)] is None:
                if i != self.focus:
                    text += " [   ] "
                else:
                    text += "   _   "
            else:
                if i != self.focus:
                    text += f" [ {self.digits[str(i)]} ] "
                else:
                    text += f" - {self.digits[str(i)]} - "
        return text

    def finish(self, button):
        code = ""
        for digit in self.digits.values():
            if digit == None:
                self._screen.show_popup_message(_("Invalid"), level=2)
                return
            else:
                code += str(digit)

        print(code)
        