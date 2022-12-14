#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Classes used to update Sirsi Workflows receipt printer configuration
options."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from .configurator import Configurator, local_printers_available
from .path import preference_files
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class ReceiptFont():
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
    def name(self, new_name: str) -> None:
        self._modified = True
        self._name = new_name

    @property
    def size(self) -> str:
        """The size (in points) of the font."""
        return self._size
    @size.setter
    def size(self, new_size: int) -> None:
        self._modified = True
        self._size = str(new_size)

    @property
    def style(self) -> str:
        """The style (regular, bold, or italic) of the font."""
        return self._style
    @style.setter
    def style(self, new_style: str) -> None:
        available_styles = {
            'regular' : '0',
            'bold' : '1',
            'italic' : '2'
        }
        self._modified = True
        self._style = available_styles[new_style]

    def make_regular(self) -> None:
        """Sets the font to regular style."""
        self._modified = True
        self.style = 'regular'

    def make_bold(self) -> None:
        """Sets the font to bold style."""
        self._modified = True
        self.style = 'bold'

    def make_italic(self) -> None:
        """Sets the font to italic style."""
        self._modified = True
        self.style = 'italic'


class ReceiptPrinter(Configurator):
    def __init__(self, target_files: None | set[str] = None) -> object:
        if target_files is None:
            target_files = preference_files
        super(ReceiptPrinter, self).__init__(target_files)
        self.font = ReceiptFont()

    @property
    def changes_staged(self) -> bool:
        """Boolean indicating if changes have been staged."""
        return self._changes_staged or self.font.modified
    
    def add_from(self, *printer_names: str) -> None:
        """
        Provided an arbitrary number of printer names (as strings), checks
        these possible printers against printers that have been installed
        on the system. If one or more installed printer is found, one will
        be chosen arbitrarily and an update will be staged for Workflows
        to be configured to use the chosen printer as its receipt printer.
        If no installed printers are found, Workflows is configured to not
        use a receipt printer.
        """
        print('Adding receipt printer from:', printer_names)
        possible_printers = set([printer for printer in printer_names])
        installed_printers = local_printers_available(possible_printers)
        if installed_printers:
            print('Found receipt printers:', installed_printers)
            set_receipt_printer(self, installed_printers.pop())
        else:
            print('Found NO receipt printer.')
            remove_receipt_printer(self)
            
    def add(self, printer_name: str) -> None:
        """Directly adds the provided printer as the receipt printer."""
        set_receipt_printer(self, printer_name)
    
    def remove(self) -> None:
        """See: remove_receipt_printer"""
        remove_receipt_printer(self)
        
    def run(self, test_run: bool = False) -> None:
        """Stages font changes iff font has been modified. Then runs as Configurator."""
        if self.font.modified:
            set_receipt_font(self, self.font)
        super(ReceiptPrinter, self).run(test_run)

def set_receipt_printer(cfg: Configurator, printer_name: str) -> str:
    """
    Stages an update in the provided Configurator object for Workflows
    to use the provided printer name as its receipt printer.
    """
    print('Setting receipt printer to "%s".' % printer_name)
    cfg.update('peripherals.receipt.name', printer_name)
    cfg.update('peripherals.receipt.dot_matrix', 'N')
    cfg.update('peripherals.receipt.enabled', 'Y')

def remove_receipt_printer(cfg: Configurator) -> None:
    """
    Stages an update in the provided Configurator object instructing
    Workflows to use no receipt printer.
    """
    cfg.update('peripherals.receipt.enabled', 'N')

def set_receipt_font(cfg: Configurator, font: ReceiptFont) -> None:
    """
    Stages an update in the provided Configurator object setting the font
    used by the receipt printer to the one provided.
    """
    new_value = '|'.join([font.name, font.style, font.size])
    cfg.update('peripherals.receipt.font', new_value)
