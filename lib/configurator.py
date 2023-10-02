#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Nov. 2022
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""A class to update Sirsi Workflows configuration files."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import NoReturn, Any, Set, Tuple, List, Union, Generator
from .os import LockedFile
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class Configurator:
    def __init__(self, config_files: Set[str]) -> "Configurator":
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

    def update(self, key: str, value: str) -> NoReturn:
        """
        Stages an update to a key in the preference files, replacing its
        current value with the provided value. If `key` doesn't exist in
        current file, it will be appended with value provided.

        If an update has already been staged for the provided key, it will
        be overwritten with the provided value.
        """
        self._update_items[key] = value
        self._changes_staged = True

    def batch_update(self, batch: List[Tuple[str, str]]) -> NoReturn:
        for key, value in batch:
            self.update(key, value)

    def delete(self, key: str) -> NoReturn:
        """
        Slates a key in the preference files for deletion.
        """
        self._delete_items.add(key)
        self._changes_staged = True
                
    def _updated_files(self) -> Generator[Tuple[str, str], None, None]:
        """
        Yields a (path, content) tuple for each subject file of the
        Configurator. The 'path' value contains the full path to the file,
        and the 'content' value contains the new content of the file based
        on delete and update rules of the configurator.
        """
        for path in self._config_files:
            keys_to_update = set(self._update_items.keys())
            lines_to_delete = set()
            buffer = []
            with open(path) as pref:
                for line in [_.strip() for _ in pref if _.strip()]:
                    key, value = self.config_line_processor(line)
                    buffer.append([key, value])
            # do the staged updates; record the line numbers to be deleted
            if buffer:
                for i, cfg in enumerate(buffer):
                    key = cfg[0]
                    if key in self._delete_items:
                        lines_to_delete.add(i)
                    if key in keys_to_update:
                        buffer[i][1] = self._update_items[key]
                        keys_to_update.remove(key)
            # delete the keys slated for deletion
            if buffer:
                for i, line_num in enumerate(sorted(list(lines_to_delete))):
                    del buffer[line_num - i]
                    i += 1
            # append 'update' values that were not in file
            for new_item in keys_to_update:
                value = self._update_items[new_item]
                buffer.append((new_item, value))
            # reformat buffer and write to file
            content = '\n'.join([self.config_line_formatter(key,val) \
                                for key, val in buffer])
            yield path, content
            
    def config_line_processor(self, line: str) -> List[str]:
        """Config line to key/value pair: Returns a two-item list,
        [key, item], based on provided configuration line."""
        key, value = line.strip().split('=')
        return [key, value]
            
    def config_line_formatter(self, key: str, value: str) -> str:
        """Key/value pair to config line: Return a configuration file
        item properly formatted for the configuration file."""
        return key + '=' + value

    @property
    def config_files(self):
        """A set containing paths to configuration files affected by
        this Configurator."""
        return self._config_files

    def run(self, test_run: bool = False) -> NoReturn:
        """Applies updates and deletions to preference files."""
        if not self.changes_staged:
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
            with LockedFile(path, 'w') as fo:
                fo.write(updated_file)
        self._changes_staged = False
