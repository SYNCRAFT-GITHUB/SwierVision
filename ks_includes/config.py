from ks_includes.host import Moonraker as M
from ks_includes.questions import Question
from ks_includes.questions import questions
import configparser
import gettext
import socket
import os
import logging
import json
import re
import copy
import pathlib
import locale

from io import StringIO

SCREEN_BLANKING_OPTIONS = [
    300,  # 5 Minutes
    480,  # 8 Minutes
    600,  # 10 Minutes
    900,  # 15 Minutes
    1800,  # 30 Minutes
    2700,  # 45 Minutes
    3600,  # 1 Hour
    7200,  # 2 Hours
    14400,  # 4 Hours
    28800, # 8 Hours
]

klipperscreendir = pathlib.Path(__file__).parent.resolve().parent


class ConfigError(Exception):
    pass


class KlipperScreenConfig:
    config = None
    configfile_name = "KlipperScreen.conf"
    do_not_edit_line = "#~# --- Do not edit below this line. This section is auto generated --- #~#"
    do_not_edit_prefix = "#~#"

    def __init__(self, configfile, screen=None):
        self.lang_list = None
        self.errors = []
        self.fix_option: str = "NONE"
        self.extruder_option: str = "NONE"
        self.selected_question: Question = None
        self.nozzle0: str = self.variables_value_reveal('nozzle0')
        self.nozzle1: str = self.variables_value_reveal('nozzle1')
        self.default_config_path = os.path.join(klipperscreendir, "ks_includes", "defaults.conf")
        self.config = configparser.ConfigParser()
        self.config_path = self.get_config_file_location(configfile)
        logging.debug(f"Config path location: {self.config_path}")
        self.defined_config = None
        self.lang = None
        self.langs = {}

        try:
            self.config.read(self.default_config_path)
            # In case a user altered defaults.conf
            self.validate_config(self.config)
            if self.config_path != self.default_config_path:
                user_def, saved_def = self.separate_saved_config(self.config_path)
                self.defined_config = configparser.ConfigParser()
                self.defined_config.read_string(user_def)

                includes = [i[8:] for i in self.defined_config.sections() if i.startswith("include ")]
                for include in includes:
                    self._include_config("/".join(self.config_path.split("/")[:-1]), include)

                self.exclude_from_config(self.defined_config)

                self.log_config(self.defined_config)
                if self.validate_config(self.defined_config, string=user_def):
                    self.config.read_string(user_def)
                if saved_def is not None:
                    auto_gen = configparser.ConfigParser()
                    auto_gen.read_string(saved_def)
                    if self.validate_config(auto_gen, string=saved_def, remove=True):
                        self.config.read_string(saved_def)
                        logging.info(f"====== Saved Def ======\n{saved_def}\n=======================")
            # This is the final config
            # self.log_config(self.config)
        except KeyError as Kerror:
            msg = f"Error reading config: {self.config_path}\n{Kerror}"
            logging.exception(msg)
            self.errors.append(msg)
            raise ConfigError(msg) from Kerror
        except ValueError as Verror:
            msg = f"Invalid Value in the config:\n{Verror}"
            logging.exception(msg)
            self.errors.append(msg)
        except Exception as e:
            msg = f"Unknown error with the config:\n{e}"
            logging.exception(msg)
            self.errors.append(msg)

        printers = [i for i in self.config.sections() if i.startswith("printer ")]
        if len(printers) == 0:
            printers.append("Printer Syncraft IDEX")

        host_json_path = os.path.join(os.getcwd(), "ks_includes", "dev-host.json")
        if os.path.exists(host_json_path):
            try:
                with open(host_json_path, 'r') as file:
                    data = json.load(file)
                    M.set_new_connection(
                        host=data['host'],
                        port=data['port'],
                        api=data['api_key']
                        )
            except:
                print('Unable to read host json file')

        self.printers = [
            {printer[8:]: {
                "moonraker_host": self.config.get(printer, "moonraker_host", fallback=M.get_host()),
                "moonraker_port": self.config.get(printer, "moonraker_port", fallback=M.get_port()),
                "moonraker_api_key": self.config.get(printer, "moonraker_api_key", fallback=M.get_api()).replace('"', '')
            }} for printer in printers
        ]

        conf_printers_debug = copy.deepcopy(self.printers)
        for printer in conf_printers_debug:
            name = list(printer)[0]
            item = conf_printers_debug[conf_printers_debug.index(printer)]
            if item[name]['moonraker_api_key'] != "":
                item[name]['moonraker_api_key'] = "redacted"
        logging.debug(f"Configured printers: {json.dumps(conf_printers_debug, indent=2)}")

        self.create_translations()
        self._create_configurable_options(screen)

    def create_translations(self):
        lang_path = os.path.join(klipperscreendir, "ks_includes", "locales")
        self.lang_list = [d for d in os.listdir(lang_path) if not os.path.isfile(os.path.join(lang_path, d))]
        self.lang_list.sort()
        for lng in self.lang_list:
            self.langs[lng] = gettext.translation('KlipperScreen', localedir=lang_path, languages=[lng], fallback=True)

        lang = self.get_main_config().get("language", None)
        logging.debug(f"Selected lang: {lang} OS lang: {locale.getlocale()[0]}")
        self.install_language(lang)

    def install_language(self, lang):
        if lang is None or lang == "system_lang":
            for language in self.lang_list:
                try:
                    if locale.getlocale()[0].startswith(language):
                        logging.debug("Using system lang")
                        lang = language
                except:
                    lang = "English - EN"
        if lang is not None and lang not in self.lang_list:
            # try to match a parent
            for language in self.lang_list:
                if lang.startswith(language):
                    lang = language
                    self.set("main", "language", lang)
        if lang not in self.lang_list:
            logging.error(f"lang: {lang} not found")
            logging.info(f"Available lang list {self.lang_list}")
            lang = "English - EN"
        logging.info(f"Using lang {lang}")
        self.lang = self.langs[lang]
        self.lang.install(names=['gettext', 'ngettext'])

    def validate_config(self, config, string="", remove=False):
        valid = True
        if string:
            msg = "Section headers have extra information after brackets possible newline issue:"
            for line in string.split('\n'):
                if re.match(r".+\].", line):
                    logging.error(line)
                    self.errors.append(f'{msg}\n\n{line}')
                    return False
        for section in config:
            if section == 'DEFAULT' or section.startswith('include '):
                # Do not validate 'DEFAULT' or 'include*' sections
                continue
            bools = strs = numbers = ()
            if section == 'main':
                bools = (
                    'invert_x', 'invert_y', 'invert_z', '24htime', 'only_heaters', 'show_cursor', 'confirm_estop',
                    'autoclose_popups', 'use_dpms', 'use_default_menu', 'side_macro_shortcut', 'use-matchbox-keyboard',
                    'show_heater_power', "show_scroll_steppers", "show_experimental_material", "materials_on_top",
                )
                strs = (
                    'default_printer', 'language', 'print_sort_dir', 'theme', 'screen_blanking', 'font_size',
                    'print_estimate_method', 'screen_blanking', "screen_on_devices", "screen_off_devices",
                )
                numbers = (
                    'job_complete_timeout', 'job_error_timeout', 'move_speed_xy', 'move_speed_z',
                    'print_estimate_compensation', 'width', 'height',
                )
            elif section == 'hidden':
                bools = (
                    'welcome',
                )
                strs = ()
                numbers = ()
            elif section.startswith('printer '):
                bools = (
                    'invert_x', 'invert_y', 'invert_z',
                )
                strs = (
                    'moonraker_api_key', 'moonraker_host', 'titlebar_name_type',
                    'screw_positions', 'power_devices', 'titlebar_items', 'z_babystep_values',
                    'extrude_distances', 'extrude_speeds', 'move_distances',
                )
                numbers = (
                    'moonraker_port', 'move_speed_xy', 'move_speed_z', 'screw_rotation',
                    'calibrate_x_position', 'calibrate_y_position',
                )
            elif section.startswith('preheat '):
                strs = ('gcode', '')
                numbers = [f'{option}' for option in config[section] if option != 'gcode']
            elif section.startswith('menu '):
                strs = ('name', 'icon', 'panel', 'method', 'params', 'enable', 'confirm', 'style')
            elif section.startswith('graph')\
                    or section.startswith('displayed_macros')\
                    or section.startswith('spoolman'):
                bools = [f'{option}' for option in config[section]]
            else:
                self.errors.append(f'Section [{section}] not recognized')

            for key in config[section]:
                if key not in bools and key not in strs and key not in numbers:
                    msg = f'Option "{key}" not recognized for section "[{section}]"'
                    if key == "camera_url":
                        msg = (
                            "camera_url has been deprecated in favor of moonraker cameras\n\n"
                            + "https://moonraker.readthedocs.io/en/latest/configuration/#webcam\n\n"
                            + "remove camera_url from KlipperScreen config file"
                        )
                    if remove:
                        # This should only be called for the auto-generated section
                        self.config.remove_option(section, key)
                    else:
                        self.errors.append(msg)
                elif key in numbers and not self.is_float(config[section][key]) \
                        or key in bools and not self.is_bool(config[section][key]):
                    msg = (
                        f'Unable to parse "{key}" from [{section}]\n'
                        f'Expected a {"number" if key in numbers else "boolean"} but got: {config[section][key]}'
                    )
                    self.errors.append(msg)
                    logging.error('Invalid configuration detected !!!')
                    valid = False
        return valid

    @staticmethod
    def is_float(element):
        try:
            float(element)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_bool(element):
        return element in ["False", "false", "True", "true"]

    def get_errors(self):
        return "".join(f'{error}\n\n' for error in self.errors)

    def _create_configurable_options(self, screen):

        self.configurable_options = [
            {"language": {
                "section": "main", "name": _("Language"), "type": None, "value": "system_lang",
                "callback": screen.change_language, "options": [
                    {"name": _("System") + " " + _("(default)"), "value": "system_lang"}]}},
            {"theme": {
                "section": "main", "name": _("Icon Theme"), "type": "dropdown",
                "value": "Industrial", "callback": screen.restart_ks, "options": [
                    {"name": "Industrial" + " " + _("(default)"), "value": "Industrial"}]}},
            {"print_estimate_method": {
                "section": "main", "name": _("Estimated Time Method"), "type": "dropdown",
                "value": "auto", "options": [
                    {"name": _("Auto") + " " + _("(default)"), "value": "auto"},
                    {"name": _("File"), "value": "file"},
                    {"name": _("Filament Used"), "value": "filament"},
                    {"name": _("Slicer"), "value": "slicer"}]}},
            {"screen_blanking": {
                "section": "main", "name": _("Screen Power Off Time"), "type": "dropdown",
                "value": "3600", "callback": screen.set_screenblanking_timeout, "options": [
                    {"name": _("Never"), "value": "off"}]
            }},
            {"24htime": {"section": "main", "name": _("24 Hour Time"), "type": "binary", "value": "True"}},
            {"welcome": {"section": "hidden", "name": _("Welcome to Syncraft"), "type": "binary", "value": "False"}},
            {"side_brightness_shortcut": {
                "section": "main", "name": _("Change Screen Brightness"), "type": "binary",
                "value": "False", "callback": screen.toggle_brightness_shortcut}},
            {"font_size": {
                "section": "main", "name": _("Font Size"), "type": "dropdown",
                "value": "medium", "callback": screen.restart_ks, "options": [
                    {"name": _("Small"), "value": "small"},
                    {"name": _("Medium") + " " + _("(default)"), "value": "medium"},
                    {"name": _("Large"), "value": "large"}]}},
            {"confirm_estop": {"section": "main", "name": _("Confirm Emergency Stop"), "type": "binary",
                               "value": "True"}},
            {"only_heaters": {"section": "main", "name": _("Hide sensors in Temp."), "type": "binary",
                              "value": "False", "callback": screen.reload_panels}},
            {"use_dpms": {"section": "main", "name": _("Screen DPMS"), "type": "binary",
                          "value": "True", "callback": screen.set_dpms}},
            {"autoclose_popups": {"section": "main", "name": _("Auto-close notifications"), "type": "binary",
                                  "value": "True"}},
            {"show_heater_power": {"section": "main", "name": _("Show Heater Power"), "type": "binary",
                                   "value": "False", "callback": screen.reload_panels}},
            {"show_scroll_steppers": {"section": "main", "name": _("Show Scrollbars Buttons"), "type": "binary",
                                      "value": "False", "callback": screen.reload_panels}},
            {"show_experimental_material": {"section": "main", "name": _("Show experimental Materials"), "type": "binary",
                                   "value": "True", "callback": screen.reload_panels}},
            {"materials_on_top": {"section": "main", "name": _("Display materials in the top"), "type": "binary",
                                   "value": "False", "callback": screen.reload_panels}},
            # {"": {"section": "main", "name": _(""), "type": ""}}
        ]

        # Options that are in panels and shouldn't be added to the main settings
        panel_options = [
            {"invert_x": {"section": "main", "name": _("Invert X"), "type": None, "value": "False"}},
            {"invert_y": {"section": "main", "name": _("Invert Y"), "type": None, "value": "False"}},
            {"invert_z": {"section": "main", "name": _("Invert Z"), "type": None, "value": "False"}},
            {"move_speed_xy": {"section": "main", "name": _("XY Move Speed (mm/s)"), "type": None, "value": "50"}},
            {"move_speed_z": {"section": "main", "name": _("Z Move Speed (mm/s)"), "type": None, "value": "10"}},
            {"print_sort_dir": {"section": "main", "type": None, "value": "name_asc"}},
        ]

        self.configurable_options.extend(panel_options)

        t_path = os.path.join(klipperscreendir, 'styles')
        themes = [d for d in os.listdir(t_path) if (not os.path.isfile(os.path.join(t_path, d)) and d != "Industrial")]
        themes.sort()
        theme_opt = self.configurable_options[1]['theme']['options']

        for theme in themes:
            theme_opt.append({"name": theme, "value": theme})

        index = self.configurable_options.index(
            [i for i in self.configurable_options if list(i)[0] == "screen_blanking"][0])
        for num in SCREEN_BLANKING_OPTIONS:
            hour = num // 3600
            minute = num / 60
            if hour > 0:
                name = f'{hour} ' + ngettext("hour", "hours", hour)
            else:
                name = f'{minute:.0f} ' + ngettext("minute", "minutes", minute)
            self.configurable_options[index]['screen_blanking']['options'].append({
                "name": name,
                "value": f"{num}"
            })

        for item in self.configurable_options:
            name = list(item)[0]
            vals = item[name]
            if vals['section'] not in self.config.sections():
                self.config.add_section(vals['section'])
            if name not in list(self.config[vals['section']]):
                self.config.set(vals['section'], name, vals['value'])

    def exclude_from_config(self, config):
        exclude_list = ['preheat']
        if not self.defined_config.getboolean('main', "use_default_menu", fallback=True):
            logging.info("Using custom menu, removing default menu entries.")
            exclude_list.extend(('menu __main', 'menu __print', 'menu __splashscreen'))
        for i in exclude_list:
            for j in config.sections():
                if j.startswith(i):
                    for k in list(self.config.sections()):
                        if k.startswith(i):
                            del self.config[k]

    def linux(self, version: str): 
        try:
            with open("/etc/os-release", "r") as os_release_file:
                for line in os_release_file:
                    if line.startswith("VERSION="):
                        version_info = line.strip().split("=")[1].strip('"')
                        if version_info and version in version_info.lower():
                            return True
        except FileNotFoundError:
            if 'dev' in version:
                return True
            else:
                return None

    def materials_path(self, custom: bool) -> str:
        core_path = os.path.join('/home', 'pi', 'SyncraftCore')
        if not os.path.exists(core_path):
            print("SyncraftCore does not exist, this should not happen!")
            if custom:
                custom_path = os.path.join(os.getcwd(), "ks_includes", "custom.json")
                if not os.path.exists(custom_path):
                    with open(custom_path, 'w') as _:
                        print(f"custom.json file created at {custom_path}")
                        return custom_path
                else:
                    return custom_path
            else:
                return os.path.join(os.getcwd(), "ks_includes", "materials.json")
        else:
            if custom:
                custom_path = os.path.join(core_path, "materials", "custom.json")
                if not os.path.exists(custom_path):
                    with open(custom_path, 'w') as _:
                        print(f"custom.json file created at {custom_path}")
                        return custom_path
                else:
                    return custom_path
            else:
                return os.path.join(core_path, "materials", "stock.json")

    def internet_connection(self) -> bool:
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            pass
        return False

    def _include_config(self, directory, filepath):
        full_path = filepath if filepath[0] == "/" else f"{directory}/{filepath}"
        parse_files = []

        if "*" in full_path:
            parent_dir = "/".join(full_path.split("/")[:-1])
            file = full_path.split("/")[-1]
            if not os.path.exists(parent_dir):
                logging.info(f"Config Error: Directory {parent_dir} does not exist")
                return
            files = os.listdir(parent_dir)
            regex = f"^{file.replace('*', '.*')}$"
            parse_files.extend(os.path.join(parent_dir, file) for file in files if re.match(regex, file))

        else:
            if not os.path.exists(os.path.join(full_path)):
                logging.info(f"Config Error: {full_path} does not exist")
                return
            parse_files.append(full_path)

        logging.info(f"Parsing files: {parse_files}")
        for file in parse_files:
            config = configparser.ConfigParser()
            config.read(file)
            includes = [i[8:] for i in config.sections() if i.startswith("include ")]
            for include in includes:
                self._include_config("/".join(full_path.split("/")[:-1]), include)
            self.exclude_from_config(config)
            self.log_config(config)
            with open(file, 'r') as f:
                string = f.read()
                if self.validate_config(config, string=string):
                    self.config.read(file)

    def separate_saved_config(self, config_path):
        user_def = []
        saved_def = []
        found_saved = False
        if not os.path.exists(config_path):
            return ["", None]
        with open(config_path) as file:
            for line in file:
                line = line.replace('\n', '')
                if line == self.do_not_edit_line:
                    found_saved = True
                    saved_def = []
                    continue
                if found_saved is False:
                    user_def.append(line.replace('\n', ''))
                elif line.startswith(self.do_not_edit_prefix):
                    saved_def.append(line[(len(self.do_not_edit_prefix) + 1):])
        return ["\n".join(user_def), None if saved_def is None else "\n".join(saved_def)]

    def variables_value_reveal(self, key, isString=True) -> str:
        config = configparser.ConfigParser()
        pdc_path = os.path.join('/home', 'pi', 'printer_data', 'config')
        variables_path = os.path.join(pdc_path, 'variables.cfg')
        # variables_path = '/Users/rafael/variables.cfg'
        try:
            with open(variables_path, 'r') as variab:
                config.read_file(variab, source=variables_path)
                if isString:
                    return str(config.get('Variables', str(key).lower())[1:-1])
                else:
                    return str(config.get('Variables', str(key).lower()))
        except:
            print(f"Unable to read 'variables.cfg' to get value from key '{key}'.")
            return 'none'

    def get_fix_option (self) -> str:
        return self.fix_option

    def get_extruder_option (self) -> str:
        return self.extruder_option

    def get_question (self) -> Question:
        return self.selected_question

    def replace_fix_option (self, newvalue):
        self.fix_option = newvalue

    def replace_extruder_option (self, newvalue):
        self.extruder_option = newvalue

    def replace_question (self, question: Question):
        self.selected_question = question

    def get_config_file_location(self, file):
        # Passed config (-c) by default is ~/KlipperScreen.conf
        logging.info(f"Passed config (-c): {file}")
        if os.path.exists(file):
            return file

        file = os.path.join(klipperscreendir, self.configfile_name)
        if os.path.exists(file):
            return file
        file = os.path.join(klipperscreendir, self.configfile_name.lower())
        if os.path.exists(file):
            return file

        klipper_config = os.path.join(os.path.expanduser("~/"), "printer_data", "config")
        file = os.path.join(klipper_config, self.configfile_name)
        if os.path.exists(file):
            return file
        file = os.path.join(klipper_config, self.configfile_name.lower())
        if os.path.exists(file):
            return file

        # OLD config folder
        klipper_config = os.path.join(os.path.expanduser("~/"), "klipper_config")
        file = os.path.join(klipper_config, self.configfile_name)
        if os.path.exists(file):
            return file
        file = os.path.join(klipper_config, self.configfile_name.lower())
        if os.path.exists(file):
            return file

        # fallback
        return self.default_config_path

    def get_config(self):
        return self.config

    def get_configurable_options(self):
        return self.configurable_options

    def get_lang(self):
        return self.lang

    def get_main_config(self):
        return self.config['main']

    def get_hidden_config(self):
        return self.config['hidden']

    def get_menu_items(self, menu="__main", subsection=""):
        if subsection != "":
            subsection = f"{subsection} "
        index = f"menu {menu} {subsection}"
        items = [i[len(index):] for i in self.config.sections() if i.startswith(index)]
        menu_items = []
        for item in items:
            split = item.split()
            if len(split) == 1:
                menu_items.append(self._build_menu_item(menu, index + item))

        return menu_items

    def get_menu_name(self, menu="__main", subsection=""):
        name = f"menu {menu} {subsection}" if subsection != "" else f"menu {menu}"
        return False if name not in self.config else self.config[name].get('name')

    def get_preheat_options(self):
        index = "preheat "
        items = [i[len(index):] for i in self.config.sections() if i.startswith(index)]
        return {item: self._build_preheat_item(index + item) for item in items}

    def _build_preheat_item(self, name):
        if name not in self.config:
            return False
        cfg = self.config[name]
        return {opt: cfg.get("gcode", None) if opt == "gcode" else cfg.getfloat(opt, None) for opt in cfg}

    def get_printer_config(self, name):
        if not name.startswith("printer "):
            name = f"printer {name}"

        return None if name not in self.config else self.config[name]

    def get_printers(self):
        return self.printers

    def save_user_config_options(self):
        save_config = configparser.ConfigParser()
        for item in self.configurable_options:
            name = list(item)[0]
            opt = item[name]
            curval = self.config[opt['section']].get(name)
            if curval != opt["value"] or (
                    self.defined_config is not None and opt['section'] in self.defined_config.sections() and
                    self.defined_config[opt['section']].get(name, None) not in (None, curval)):
                if opt['section'] not in save_config.sections():
                    save_config.add_section(opt['section'])
                save_config.set(opt['section'], name, str(curval))

        extra_sections = [i for i in self.config.sections() if i.startswith("displayed_macros")]
        extra_sections.extend([i for i in self.config.sections() if i.startswith("graph")])
        extra_sections.extend([i for i in self.config.sections() if i.startswith("spoolman")])
        for section in extra_sections:
            for item in self.config.options(section):
                value = self.config[section].getboolean(item, fallback=True)
                if value is False or (self.defined_config is not None and
                                      section in self.defined_config.sections() and
                                      self.defined_config[section].getboolean(item, fallback=True) is False and
                                      self.defined_config[section].getboolean(item, fallback=True) != value):
                    if section not in save_config.sections():
                        save_config.add_section(section)
                    save_config.set(section, item, str(value))

        save_output = self._build_config_string(save_config).split("\n")
        for i in range(len(save_output)):
            save_output[i] = f"{self.do_not_edit_prefix} {save_output[i]}"

        if self.config_path == self.default_config_path:
            user_def = ""
            saved_def = None
        else:
            user_def, saved_def = self.separate_saved_config(self.config_path)

        contents = (f"{user_def}\n"
                    f"{self.do_not_edit_line}\n"
                    f"{self.do_not_edit_prefix}\n"
                    + '\n'.join(save_output) + f"\n"
                                               f"{self.do_not_edit_prefix}\n")

        if self.config_path != self.default_config_path:
            filepath = self.config_path
        else:
            filepath = os.path.expanduser("~/")
            klipper_config = os.path.join(filepath, "printer_data", "config")
            old_klipper_config = os.path.join(filepath, "klipper_config")
            if os.path.exists(klipper_config):
                filepath = os.path.join(klipper_config, self.configfile_name)
            elif os.path.exists(old_klipper_config):
                filepath = os.path.join(old_klipper_config, self.configfile_name)
            else:
                filepath = os.path.join(filepath, self.configfile_name)
            logging.info(f'Creating a new config file in {filepath}')

        try:
            with open(filepath, 'w') as file:
                file.write(contents)
        except Exception as e:
            logging.error(f"Error writing configuration file in {filepath}:\n{e}")

    def set(self, section, name, value):
        self.config.set(section, name, value)

    def log_config(self, config):
        lines = [
            " "
            "===== Config File =====",
            re.sub(
                r'(moonraker_api_key\s*=\s*\S+)',
                'moonraker_api_key = [redacted]',
                self._build_config_string(config)
            ),
            "======================="
        ]
        logging.info("\n".join(lines))

    @staticmethod
    def _build_config_string(config):
        sfile = StringIO()
        config.write(sfile)
        sfile.seek(0)
        return sfile.read().strip()

    def _build_menu_item(self, menu, name):
        if name not in self.config:
            return False
        cfg = self.config[name]
        item = {
            "name": cfg.get("name"),
            "icon": cfg.get("icon", None),
            "panel": cfg.get("panel", None),
            "method": cfg.get("method", None),
            "confirm": cfg.get("confirm", None),
            "enable": cfg.get("enable", "True"),
            "params": cfg.get("params", "{}"),
            "style": cfg.get("style", None)
        }

        return {name[(len(menu) + 6):]: item}
