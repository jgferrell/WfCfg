#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Command line interface for updating Sirsi Workflows configuration
files."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
import argparse
from lib.configurator import Configurator, local_printers_available
from lib.receipt_printer import ReceiptPrinter
from lib.font import FontConfigurator, gui_components, gui_component_styles
from lib.path import preference_files
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def _main_config(args):
    wfcfg = Configurator(preference_files)
    if args.update:
        print('args.update:', args.update)
        for key, val in [arg.split('=') for arg in args.update]:
            wfcfg.update(key, val)
    if args.delete:
        for key in args.delete:
            wfcfg.delete(key)
    if args.find_printer:
        try:
            printer = local_printers_available(args.find_printer).pop()
            key = 'peripherals.screen.printer'
            wfcfg.update(key, printer)
        except KeyError:  # no matching printer found
            pass
    if args.add_printer:
        wfcfg.update('peripherals.screen.printer', args.add_printer[0])
    wfcfg.run(args.test)
    
def _gui_font_config(args):
    wfcfg = FontConfigurator()
    wfcfg.update(args.component, args.type, args.style, args.size)
    wfcfg.run(args.test)

def _receipt_printer_config(args):
    wfcfg_rp = ReceiptPrinter()
    if args.find:
        wfcfg_rp.add_from(*args.find)
    if args.add:
        wfcfg_rp.add(args.add)
    if args.remove:
        wfcfg_rp.remove()
    if args.font_size:
        wfcfg_rp.font.size = args.font_size
    if args.font_type:
        wfcfg_rp.font.name = args.font_type
    if args.font_style:
        wfcfg_rp.font.style = args.font_style
    wfcfg_rp.run(args.test)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', 
        help='Simulated run --- Does not write changes to disk.')
    subparsers = parser.add_subparsers(required=True, 
        help='sub-command help')

    # MAIN CONFIG PARSER
    parser_mn = subparsers.add_parser('main', 
        help='Modify preferences of Workflows GUI.')
    parser_mn.add_argument('--update', nargs='+')
    parser_mn.add_argument('--delete', nargs='+')    
    parser_mn.add_argument('--find-printer', nargs='+', 
        help='find a screen printer')
    parser_mn.add_argument('--add-printer', nargs=1, 
        help='add a screen printer')
    parser_mn.set_defaults(func=_main_config)
    
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
    parser_ft.set_defaults(func=_gui_font_config)

    # RECEIPT PRINTER CONFIG parser
    parser_rp = subparsers.add_parser(
        'receipt-printer', help='Modify receipt printer settings.')
    parser_rp.set_defaults(func=_receipt_printer_config)
    rp_addremove = parser_rp.add_mutually_exclusive_group()    
    rp_addremove.add_argument('--find', nargs='+')
    rp_addremove.add_argument('--add')
    rp_addremove.add_argument('--remove', action='store_true')
    rp_font = parser_rp.add_argument_group('font')
    rp_font.add_argument('--font-size', type=int, 
        help='font size (in pt)')
    rp_font.add_argument('--font-type', help='font typeface (name)')
    rp_font.add_argument('--font-style', 
        choices=['regular', 'bold', 'italic'], help='font style')

    args = parser.parse_args()
    args.func(args)
