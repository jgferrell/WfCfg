#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Utilities for working with client fonts."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import NoReturn, Any, Set, Tuple, List, Union
from .configurator import Configurator
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class Font:
    def __init__(self, font_name, font_style, font_size):
        self.name = font_name
        self.style = font_style
        self.size = font_size

    def __str__(self):
        f = [self.name, self.style, str(self.size)]
        f = [_.strip('\'"') for _ in f]
        return '|'.join(f)
        

class FontConfigurator(Configurator):
    def __init__(self, config_files) -> "FontConfigurator":
        super().__init__(config_files)    

    def update(self, gui_component: str, font_type: str, 
                  font_style: str, font_size: int) -> NoReturn:
        """
        Stages an update to a GUI component in the font files, replacing
        its current configuration (font type, style, and size) with the
        provided values. If `gui_component` doesn't exist in current
        file, it will be appended with value provided.

        If an update has already been staged for the provided GUI
        component, it will be overwritten with the provided value.
        """
        font = Font(font_type, font_style, font_size)
        if gui_component.lower() == 'all':
            for gc in gui_components:
                super().update(gc, str(font))
        else:
            super().update(gui_component, str(font))

    def batch_update(self, batch: List[Tuple[str, str]]) -> NoReturn:
        raise NotImplementedError

    def delete(self, key: str) -> NoReturn:
        raise NotImplementedError

    def config_line_processor(self, line: str) -> List[str]:
        """Return a list in [key, value] format of a configuration line."""
        line = line.strip().split('|')
        return [line[0], '|'.join(line[1:-1])]
            
    def config_line_formatter(self, key: str, value: str) -> str:
        """Return a configuration file item properly formatted for the
        configuration file."""
        return '|'.join((key, value)) + '|'

gui_components = ['VerifyfieldFont', 'NextstepFont', 'WritefieldFont', 
    'RadiobuttonFont', 'StatusFont', 'MenubarFont', 'ReadfieldFont', 
    'NavigationFont', 'ListboxFont', 'CheckboxFont', 'LabelFont', 
    'ButtonFont'
    ]
    
gui_component_styles = ['plain', 'bold', 'italic']
