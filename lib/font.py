#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Utilities for working with client fonts."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from .configurator import Configurator
from .path import font_files
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class FontConfigurator(Configurator):
    def __init__(self, target_files: None | set[str] = None) -> object:
        if target_files is None:
            target_files = font_files
        super(FontConfigurator, self).__init__(target_files)

    def update(self, gui_component: str, font_type: str, 
                  font_style: str, font_size: int) -> None:
        """
        Stages an update to a GUI component in the font files, replacing
        its current configuration (font type, style, and size) with the
        provided values. If `gui_component` doesn't exist in current
        file, it will be appended with value provided.

        If an update has already been staged for the provided GUI
        component, it will be overwritten with the provided value.
        """
        if gui_component.lower() == 'all':
            for gc in gui_components:
                self._update_items[gc] = [font_type, font_style, str(font_size)]
        else:
            self._update_items[gui_component] = [font_type, font_style, str(font_size)]
        self._changes_staged = True
            
    def formatted_config_item(self, key: str, value) -> str:
        """Return a configuration file item properly formatted for the
        configuration file."""
        return '|'.join([key] + value) + '|'
        
    def processed_buffer_line(self, line: str) -> list:
        """Return a list in [key, value] format of a configuration line."""
        line = line.strip().split('|')
        return [line[0], line[1:]]


gui_components = ['VerifyfieldFont', 'NextstepFont', 'WritefieldFont', 
    'RadiobuttonFont', 'StatusFont', 'MenubarFont', 'ReadfieldFont', 
    'NavigationFont', 'ListboxFont', 'CheckboxFont', 'LabelFont', 
    'ButtonFont'
    ]
    
gui_component_styles = ['plain', 'bold', 'italic']
