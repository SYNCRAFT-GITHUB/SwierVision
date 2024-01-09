from ks_includes.questions import Question
from ks_includes.questions import questions
import logging
import random
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):

    def __init__(self, screen, title):

        super().__init__(screen, title)
        self.menu = ['help_panel']

        class ConfigurationButton:
            def __init__(self, reference: str, title: str, question: Question):
                self.reference = reference
                self.title = title
                self.question = question

        self.config_buttons = []

        for q in questions:
            self.config_buttons.append(
                ConfigurationButton(reference=q.reference, title=_(q.title), question=q)
            )

        grid = self._gtk.HomogeneousGrid()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

        columns = 1

        for i, btn in enumerate(self.config_buttons):

            self.button = self._gtk.Button("help", btn.title, f"color{random.randint(1, 4)}", self.bts, Gtk.PositionType.RIGHT, 1)

            self.button.connect("clicked", self.reset_steps_panel)
            self.button.connect("clicked", self.replace_question, btn.question)
            self.button.connect("clicked", self.menu_item_clicked, {
                "name": _(btn.title),
                "panel": "steps"
            })

            if self._screen.vertical_mode:
                row = i % columns
                col = int(i / columns)
            else:
                col = i % columns
                row = int(i / columns)
            grid.attach(self.button, col, row, 1, 1)

        self.labels['help_panel'] = self._gtk.HomogeneousGrid()
        self.labels['help_panel'].attach(grid, 0, 0, 1, 2)

        self.content.add(self.labels['help_panel'])

    def replace_question(self, button, question):
        self._config.replace_question(question)

    def reset_steps_panel(self, button):
        try:
            del self._screen.panels['steps']
        except:
            pass