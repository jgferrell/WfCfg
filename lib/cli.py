#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Sep. 2023
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Command line interface for updating Sirsi Workflows configuration
files."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
import argparse
from .configurator import Configurator
from .receipt_printer import ReceiptPrinter
from .font import FontConfigurator, gui_components, gui_component_styles
from .paper import Paper, paper_units, paper_sizes, paper_orientation
try:
    from .os import add_local_receipt_printer
except NotImplementedError:
    add_local_receipt_printer = lambda x: None
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class WfCfgParser:
    def __init__(self, pref_files, font_files):
        self.main_cfg = Configurator(pref_files)
        self.font_cfg = FontConfigurator(font_files)
        self.receipt = ReceiptPrinter(pref_files)
        self.paper = Paper()
        
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('--test', action='store_true', 
            help='Simulated run --- Does not write changes to disk.')
        subparsers = self._parser.add_subparsers(required=True, 
            help='sub-command help')

        ##################################################################
        # MAIN CONFIG PARSER
        parser_mn = subparsers.add_parser('main', 
            help='Modify preferences of Workflows GUI.')
        parser_mn.add_argument('--update', nargs='+')
        parser_mn.add_argument('--delete', nargs='+')
        parser_mn.add_argument('--find-printer', nargs='+', 
            help='find a screen printer')
        parser_mn.add_argument('--add-printer', nargs=1, 
            help='add a screen printer')
        parser_mn.add_argument('--tabbed-windows', action='store_true',
            help='change desktop settings to use tabbed windows')
        parser_mn.set_defaults(func=self._proc_main)

        ##################################################################
        # SCREEN PRINTER PAPER CONFIG
        parser_paper = subparsers.add_parser('paper',
            help='Paper settings for the "screen printer."')
        margin_help = '''Set all margins to the same value by
        providing a single number. Or set each margin individually by
        providing four numbers. When four numbers are provided, the
        first number will be the top margin and proceed clockwise
        (i.e., top, right, bottom, and then left).'''
        parser_paper.add_argument('--margins', nargs='+',
            help=margin_help)
        parser_paper.add_argument('--units', nargs=1,
            choices=sorted(list(paper_units)))    
        parser_paper.add_argument('--orientation', nargs=1, 
            choices=sorted(list(paper_orientation)))
        parser_paper.add_argument('--size', nargs=1,
            choices=sorted(list(paper_sizes)))
        parser_paper.set_defaults(func=self._proc_paper)
        
        ##################################################################
        # CLIENT-GUI FONT PARSER
        parser_ft = subparsers.add_parser('font', 
            help='Modify display font settings of Workflows GUI.')
        parser_ft.add_argument('component', 
            choices=['ALL'] + gui_components, help='affected UI component')
        parser_ft.add_argument('type', help='font type (name)')
        parser_ft.add_argument('size', type=int, 
            help='font size (in points)')
        parser_ft.add_argument('style', choices=gui_component_styles,
            help='font style')
        parser_ft.set_defaults(func=self._proc_font)

        ##################################################################
        # RECEIPT PRINTER CONFIG parser
        parser_rp = subparsers.add_parser(
            'receipt-printer', help='Modify receipt printer settings.')
        parser_rp.set_defaults(func=self._proc_receipt)
        # add or remove printer: only one of these allowed per call
        rp_addremove = parser_rp.add_mutually_exclusive_group()    
        rp_addremove.add_argument('--find', nargs='+',
            help="provide a list of names to compare against locally "\
                "installed printers before installing one of the "\
                "printers found to be locally installed, chosen "\
                "arbitrarily")
        rp_addremove.add_argument('--add', nargs=1,
            help="provide the name of the printer to add as a receipt printer")
        rp_addremove.add_argument('--remove', action='store_true',
            help="disable the receipt printer in Workflows")
        rp_font = parser_rp.add_argument_group('font')
        rp_font.add_argument('--font-size', type=int, 
            help='font size (in pt)')
        # receipt printer font configuration
        rp_font.add_argument('--font-type', help='font typeface (name)')
        rp_font.add_argument('--font-style', 
            choices=['regular', 'bold', 'italic'], help='font style')
        # receipt printer paper configuration
        rp_paper = parser_rp.add_argument_group('paper')
        rp_paper.add_argument('--paper-margins', nargs='+', 
            help='set paper margins in the following order: top right bottom left')
        rp_paper.add_argument('--paper-units', nargs=1,
            choices=sorted(list(paper_units)),
            help='declare which units to use')
        rp_paper.add_argument('--paper-width', nargs=1, 
            help='set paper width in terms of units')
        
        
    def _proc_main(self, args):
        """Procedure called by running the 'main' subparser."""
        if args.update:
            print('args.update:', args.update)
            for key, val in [arg.split('=') for arg in args.update]:
                self.main_cfg.update(key, val)
        if args.delete:
            for key in args.delete:
                self.main_cfg.delete(key)
        if args.find_printer:
            try:
                printer = local_printers_available(args.find_printer).pop()
                key = 'peripherals.screen.printer'
                self.main_cfg.update(key, printer)
            except KeyError:  # no matching printer found
                pass
        if args.add_printer:
            self.main_cfg.update('peripherals.screen.printer', args.add_printer[0])
        if args.tabbed_windows:
            self.main_cfg.update('desktop.multiple_windows', 'N')
            self.main_cfg.update('desktop.tabbed_windows', 'Y')
            self.main_cfg.update('desktop.tabbed_window_bottom', 'N')
        self.main_cfg.run(args.test)
      
    def _proc_paper(self, args):
        """Procedure called by running the 'paper' subparser."""
        if args.margins:
            if len(args.margins) == 4:
                self.paper.margins = [float(m) for m in args.margins]
            elif len(args.margins) == 1:
                self.paper.margins = float(args.margins[0])
            else:
                raise ValueError("Bad number of values supplied.")
        if args.units:
            self.paper.units = args.units[0]
        if args.orientation:
            self.paper.orientation = args.orientation[0]
        if args.size:
            self.paper.size = args.size[0]
        for key, value in self.paper.settings:
            self.main_cfg.update(key, value)
        self.main_cfg.run(args.test)

    def _proc_font(self, args):   
        """Procedure called by running the 'font' subparser."""
        self.font_cfg.update(args.component, args.type, args.style, args.size)
        self.font_cfg.run(args.test)

    def _proc_receipt(self, args):
        """Procedure called by running the 'receipt-printer' subparser."""
        
        # receipt printer settings
        if args.find:
            add_local_receipt_printer(self.receipt, *args.find)
        if args.add:
            printer_name = args.add[0]
            self.receipt.add(printer_name)
        if args.remove:
            self.receipt.disable()

        # receipt paper settings
        if args.paper_units:
            paper_units = args.paper_units[0]
            self.receipt.paper.units = paper_units
        if args.paper_width:
            paper_width = float(args.paper_width[0])
            self.receipt.paper.width = paper_width
        if args.paper_margins:
            if len(args.paper_margins) == 4:
                self.receipt.paper.margins = [float(m) for m in args.paper_margins]
            elif len(args.paper_margins) == 1:
                self.receipt.paper.margins = float(args.paper_margins[0])
            else:
                raise ValueError("Bad number of values supplied.")

        # receipt font settings
        if args.font_size:
            self.receipt.font.size = args.font_size
        if args.font_type:
            self.receipt.font.name = args.font_type
        if args.font_style:
            self.receipt.font.style = args.font_style
        self.receipt.run(args.test)

    def run(self, args):
        ##################################################################
        # DEFAULT TO 'HELP': display a help message if user does not
        # supply enough arguments to run anything
        if len(args) == 0:
            # user enters: python wfcfg.py
            args = ['-h']
        elif len(args) == 1 and args[0] == 'main':
            # user enters: python wfcfg.py main
            args = ['main', '-h']
        elif len(args) == 1 and args[0] == 'paper':
            # user enters: python wfcfg.py paper
            args = ['paper', '-h']
        elif len(args) == 1 and args[0] == 'font':
            # user enters: python wfcfg.py main font
            args = ['font', '-h']
        elif len(args) == 1 and args[0] == 'receipt-printer':
            # user enters: python wfcfg.py receipt-printer
            args = ['receipt-printer', '-h']
        else:
            # continue as normal
            pass

        args = self._parser.parse_args(args)
        args.func(args)    
