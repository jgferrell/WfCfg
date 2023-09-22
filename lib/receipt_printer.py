#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Classes used to update Sirsi Workflows receipt printer configuration
options."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import NoReturn, Any, Set, Tuple, List, Union
from .configurator import Configurator
from .paper import Paper
from .settings_group import SettingsGroup, CfgSetting
NumType = Union[float, int]
#::::::::::::::::::::::::::::::p:::::::::::::::::::::::::::::::::::::::

class ReceiptPaper(Paper):
    def __init__(self) -> "ReceiptPaper":
        super().__init__('peripherals.receipt.page.')
        self.add_setting('width', float)
        self.delete_setting('orientation')
        self.delete_setting('paper_size')
        
        # correct for difference between 'screen paper' and 'receipt
        # paper' margin key names
        for m in ['top', 'right', 'bottom', 'left']:
            self.override_key('margin_%s' % m, 'margin.%s' % m)

        # correct for difference between 'screen paper' units and
        # 'receipt paper' units key name
        self.override_key('margin_unit', 'unit')

    @property
    def width(self) -> float:
        """Returns the width of the receipt paper."""
        return self.get_setting('width').value
    @width.setter
    def width(self, w: NumType) -> NoReturn:
        """Sets the width of the receipt paper."""
        self.get_setting('width').value = w
                    

class ReceiptFont(CfgSetting):
    # Workflows stores receipt font style as the following integers:
    REGULAR = 0
    BOLD = 1
    ITALIC = 2
    
    def __init__(self) -> object:
        """An object to store font data. Defaults to 11pt Verdana Bold."""
        self._name='Verdana'
        self._style='1'
        self._size='11'
        self._modified = False
        
    @property
    def modified(self) -> bool:
        """Boolean indicating if font has been modified."""
        return self._modified

    @property
    def name(self) -> str:
        """The typeface or name of the font."""
        return self._name
    @name.setter
    def name(self, new_name: str) -> NoReturn:
        self._modified = True
        self._name = new_name

    @property
    def size(self) -> int:
        """The size (in points) of the font."""
        return self._size
    @size.setter
    def size(self, new_size: int) -> NoReturn:
        self._modified = True
        self._size = new_size

    @property
    def style(self) -> int:
        """The style (regular, bold, or italic) of the font."""
        return self._style
    @style.setter
    def style(self, new_style: str) -> NoReturn:
        available_styles = {
            'regular' : ReceiptFont.REGULAR,
            'bold' : ReceiptFont.BOLD,
            'italic' : ReceiptFont.ITALIC
        }
        if new_style not in available_styles:
            raise ValueError("Value '%s' is not a valid style. "
                             "Valid styles are: " +\
                             ', '.join([k for k in available_styles]))
        self._modified = True
        self._style = available_styles[new_style]


    def make_regular(self) -> NoReturn:
        """Sets the font to regular style."""
        self._modified = True
        self.style = 'regular'

    def make_bold(self) -> NoReturn:
        """Sets the font to bold style."""
        self._modified = True
        self.style = 'bold'

    def make_italic(self) -> NoReturn:
        """Sets the font to italic style."""
        self._modified = True
        self.style = 'italic'

    @property
    def value(self) -> str:
        """Returns string representation in manner of Workflows
        config files."""
        return '|'.join([self.name, str(self.style), str(self.size)])
    @value.setter
    def value(self, value: Any) -> NoReturn:
        raise NotImplementedError

        
class ReceiptPrinter(Configurator, SettingsGroup):
    def __init__(self, config_files: Set[str]) -> "ReceiptPrinter":
        Configurator.__init__(self, config_files)
        SettingsGroup.__init__(self, 'peripherals.receipt.')
        self.paper = ReceiptPaper()

        self.add_setting('font', str)
        self.override_setting('font', ReceiptFont())
        self.add_setting('name', str)
        self.add_setting('dot_matrix', str)
        self.add_setting('enabled', str)

    @property
    def font(self) -> "ReceiptFont":
        return self.get_setting('font')
        
    @property
    def changes_staged(self) -> bool:
        """Boolean indicating if changes have been staged."""
        return super().changes_staged or super().modified
                
    def add(self, printer_name: str) -> NoReturn:
        """Adds a receipt printer with the provided name and enables it."""
        self.get_setting('name').value = printer_name
        self.get_setting('dot_matrix').value = 'N'
        self.enable()

    def enable(self) -> NoReturn:
        """Workflows will attempt to use a receipt printer."""
        self.get_setting('enabled').value = 'Y'

    def disable(self) -> NoReturn:
        """Workflows will not use a receipt printer."""
        self.get_setting('enabled').value = 'N'

    def run(self, test_run: bool = False) -> NoReturn:
        self.batch_update(self.settings)
        super().run(test_run)

    @property
    def settings(self) -> List[Tuple[str, str]]:
        return super().settings + self.paper.settings
