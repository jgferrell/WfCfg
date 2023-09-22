#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Command line interface for updating Sirsi Workflows configuration
files."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from sys import argv
import lib.cli as cli
import lib.os as os
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

if os.RUNNING_WINDOWS:
    pref_files = os.preference_files
    font_files = os.font_files
else:
    pref_files = os.get_property_files('preference', {'/tmp'}, True)
    font_files = os.get_property_files('font', {'/tmp'}, True)
    
# Run from command line with: python wfcfg.py
if __name__ == '__main__':
    parser = cli.WfCfgParser(pref_files, font_files)
    print('argv = %s' % str(argv))
    parser.run(argv[1:])
