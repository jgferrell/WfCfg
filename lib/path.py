#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Locations of Sirsi Workflows configuration files."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
import os
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def get_sirsi_dirs() -> set[str]:
    """
    Returns a set containing C:\\Program Files (x86)\\Sirsi\\JWF\\ and
    C:\\Users\\*\\Sirsi\\Workflows\\ folders.
    """
    sirsi_dirs = set([main_sirsi_dir])
    for username in os.listdir('C:\\Users'):
        path = os.path.join('C:\\Users', username, 'Sirsi', 'Workflows')
        if os.path.isdir(path):
            sirsi_dirs.add(path)
    return sirsi_dirs

def get_property_files(filename: str, sirsi_dirs: None | set[str] = None) -> set[str]:
    """
    Returns a set of paths to files located in Workflows' "Property"
    folder. Target directories containing "Property" folder can be
    provided as a set of paths (string format); if no set is provided,
    then one will be generated with get_sirsi_dirs() function.
    """
    if sirsi_dirs is None:
        sirsi_dirs = get_sirsi_dirs()
    pref_files = set()
    for sirsi_dir in sirsi_dirs:
        path = os.path.join(sirsi_dir, 'Property', filename)
        if os.path.isfile(path):
            pref_files.add(path)
    return pref_files

main_sirsi_dir = 'C:\\Program Files (x86)\\Sirsi\JWF\\'
preference_files = get_property_files('preference')
font_files = get_property_files('font')
