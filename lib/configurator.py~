#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""A class to update Sirsi Workflows configuration files."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import Generator
import os, winreg
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class Configurator:
    def __init__(self, config_files: set[str]) -> object:
        """
        Create a new Configurator object. Subject files are provided as
        a set of strings of filepaths.
        """
        self._update_items = {}
        self._delete_items = set()
        self._config_files = config_files
        self._changes_staged = False
        
    @property
    def changes_staged(self) -> bool:
        """Boolean indicating if changes have been staged."""
        return self._changes_staged

    def update(self, key: str, value: str) -> None:
        """
        Stages an update to a key in the preference files, replacing its
        current value with the provided value. If `key` doesn't exist in
        current file, it will be appended with value provided.

        If an update has already been staged for the provided key, it will
        be overwritten with the provided value.
        """
        self._update_items[key] = value
        self._changes_staged = True

    def delete(self, key: str) -> None:
        """
        Slates a key in the preference files for deletion.
        """
        self._delete_items.add(key)
        self._changes_staged = True

    def _updated_files(self) -> Generator[tuple[str, str], None, None]:
        """
        Yields a (path, content) tuple for each subject file of the
        Configurator. The 'path' value contains the full path to the file,
        and the 'content' value contains the new content of the file based
        on delete and update rules of the configurator.
        """
        for path in self._config_files:
            keys_to_update = set(self._update_items.keys())
            lines_to_delete = set()
            with open(path) as pref:
                buffer = [self.processed_buffer_line(line) for line in pref]
            # do the staged updates; record the line numbers to be deleted
            for i, (key, _) in enumerate(buffer):
                if key in self._delete_items:
                    lines_to_delete.add(i)
                if key in keys_to_update:
                    buffer[i][1] = self._update_items[key]
                    keys_to_update.remove(key)
            # delete the keys slated for deletion
            i = 0
            for line_num in sorted(list(lines_to_delete)):
                del buffer[line_num - i]
                i += 1
            # append 'update' values that were not in file
            for new_item in keys_to_update:
                value = self._update_items[new_item]
                buffer.append((new_item, value))
            # reformat buffer and write to file
            content = '\n'.join([self.formatted_config_item(key,val) \
                                for key, val in buffer])
            yield path, content
            
    def processed_buffer_line(self, line: str) -> list[str]:
        """Returns a two-item list, [key, item], based on provided configuration line."""
        return line.strip().split('=')
            
    def formatted_config_item(self, key: str, value: str) -> str:
        """Return a configuration file item properly formatted for the configuration file."""
        return key + '=' + value
        
    def run(self, test_run: bool = False) -> None:
        """
        Applies updates and deletions to preference files.
        """
        if not self._changes_staged:
            print("No changes staged. Not executing run.")
            return None
        if self._update_items:
            print("Updating items:")
            for key, value in self._update_items.items():
                print(' *', key, '-->', value)
            print()
        if self._delete_items:
            print("Deleting items:")
            print('\n'.join([' * ' + itm for itm in self._delete_items]) + '\n')
        print('Updating files:')
        for j, (path, updated_file) in enumerate(self._updated_files()):
            print(' *', path)
            if test_run:
                # if we're in test mode, don't write staged changes
                continue
            with open(path, 'w') as fo:
                fo.write(updated_file)


def local_printers_available(printers_sought: None | set[str] = None) -> set[str]:
    """
    Returns a set of names of locally installed printers.

    If a set of printer names is provided, returns the intersection of 
    the provided set and names of locally installed printers (i.e., 
    keys in HKML\SYSTEM\CurrentControlSet\Control\Print\Printers).
    """
    print("Looking for printers:", printers_sought)
    printers_sought = set(map(str.lower, printers_sought))
    printers_found = set()

    key_path = r'SYSTEM\CurrentControlSet\Control\Print\Printers'
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as printers:
        i = 0
        while True:
            try:
                printer = winreg.EnumKey(printers, i)
                # if we're looking for all printers, add this one
                # to results
                if printers_sought is None:
                    printers_found.add(printer)
                # if we're looking for specific printers, check
                # what we've found against that set
                else:
                    if printer.lower() in printers_sought:
                        print("Found printer:", printer)
                        printers_found.add(printer)                        
                i += 1
            except OSError:
                # no more printers
                break

    # with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hklm:
        # key_path = r'SYSTEM\CurrentControlSet\Control\Print\Printers'
        # with winreg.OpenKey(hklm, key_path) as printers:
            # i = 0
            # while True:
                # try:
                    # printer = winreg.EnumKey(printers, i)
                    # # if we're looking for all printers, add this one
                    # # to results
                    # if printers_sought is None:
                        # printers_found.add(printer)
                    # # if we're looking for specific printers, check
                    # # what we've found against that set
                    # else:
                        # if printer.lower() in printers_sought:
                            # print("Found printer:", printer)
                            # printers_found.add(printer)                        
                    # i += 1
                # except OSError:
                    # # no more printers
                    # break
    return printers_found
