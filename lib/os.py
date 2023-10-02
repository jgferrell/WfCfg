#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Sep. 2023
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""For when we have to deal with Windows."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import NoReturn, Any, Set, Tuple, List, Union, Generator
import os, time, random
LOCKFILE = '.wfcfg_lock~'
RUNNING_WINDOWS = os.name == 'nt'
if RUNNING_WINDOWS:
    import winreg
#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: 

class LockedFile:
    def __init__(self, filepath, mode):
        if not os.path.isfile(filepath):
            raise ValueError("%s is not a file." % filepath)        
        self._filepath = filepath
        self._mode = mode
        self._lockfile = filepath + LOCKFILE
        self._has_lock = False

        # check for and delete stale locks
        max_lock_age = 15 # minutes
        if os.path.exists(self._lockfile):
            modtime = os.path.getmtime(self._lockfile)
            if time.time() - modtime > 60 * max_lock_age:
                os.remove(self._lockfile)

    @property
    def locked(self):
        """Returns true iff the file is currently locked."""
        return os.path.exists(self._lockfile)

    def wait(self):
        """Wait until target file is not locked."""
        while self.locked:
            print("WAITING!")
            time.sleep(random.uniform(0,3))

    def get_lock(self):
        """Acquire lock on target file. If the target file is already
        locked, wait and try again."""
        try:
            # open for exclusive creation
            with open(self._lockfile, 'x'):
                pass
            self._has_lock = True
        except FileExistsError:
            self.wait()
            self.get_lock()

    def release_lock(self):
        """Release lock on target file."""
        if not self._has_lock:
            raise Exception("Foreign lock.")
        os.remove(self._lockfile)
        self._has_lock = False

    def write(self, content):
        self._file.write(content)

    def __enter__(self):
        self.get_lock()
        self._file = open(self._filepath, self._mode)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()
        self.release_lock()
        

def add_local_receipt_printer(rpConfigurator: "ReceiptPrinter",
                              *printer_names) -> NoReturn:
    """
    Provided rpConfigurator, a ReceiptPrinter instance, and
    printer_names, an arbitrary number of printer names (as strings),
    checks these possible printers against printers that have been
    installed on the system. If one or more installed printer is
    found, one will be chosen arbitrarily and an update will be staged
    for Workflows to be configured to use the chosen printer as its
    receipt printer.  If no installed printers are found, Workflows is
    configured to not use a receipt printer.
    """
    print('Adding receipt printer from:', printer_names)
    requested_printers = set(printer_names)
    installed_printers = local_printers_available(requested_printers)
    if installed_printers:
        print('Found receipt printers:', installed_printers)
        rpConfigurator.add(installed_printers.pop())
    else:
        print('Found NO receipt printer.')
        rpConfigurator.disable()

def local_printers_available(printers_sought: Union[None, Set[str]] =\
                             None) -> Set[str]:
    """
    Returns a set of names of locally installed printers.

    If a set of printer names is provided, returns the intersection of 
    the provided set and names of locally installed printers (i.e., 
    keys in HKML\SYSTEM\CurrentControlSet\Control\Print\Printers).
    """
    if not RUNNING_WINDOWS:
        raise NotImplementedError
    
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
    return printers_found

def get_sirsi_dirs() -> Set[str]:
    """
    Returns a set containing C:\\Program Files (x86)\\Sirsi\\JWF\\ and
    C:\\Users\\*\\Sirsi\\Workflows\\ folders.
    """
    if not RUNNING_WINDOWS: # presumably testing from Linux
        raise NotImplementedError("Directory must be specified.")

    main_sirsi_dir = 'C:\\Program Files (x86)\\Sirsi\JWF\\'
    sirsi_dirs = set([main_sirsi_dir])
    for username in os.listdir('C:\\Users'):
        path = os.path.join('C:\\Users', username, 'Sirsi', 'Workflows')
        if os.path.isdir(path):
            sirsi_dirs.add(path)
    return sirsi_dirs

def _make_file(fpath):
    try:
        os.mkdir(os.path.dirname(fpath))
    except FileExistsError:
        pass
    if not os.path.exists(fpath):
        with open(fpath, 'w') as fo:
            pass      

def get_property_files(filename: str, sirsi_dirs: Union[None, Set[str]] = None,
                       create_as_needed = False) -> Set[str]:
    """
    Returns a set of paths to files located in Workflows' "Property"
    folder. Target directories containing "Property" folder can be
    provided as a set of paths (string format); if no set is provided,
    then one will be generated with get_sirsi_dirs() function.
    """
    if sirsi_dirs is None:
        sirsi_dirs = get_sirsi_dirs()
    if not isinstance(sirsi_dirs, set):
        raise TypeError("sirsi_dirs must be a set")
    pref_files = set()
    for sirsi_dir in sirsi_dirs:
        property_dir = os.path.join(sirsi_dir, 'Property')
        fpath = os.path.join(property_dir, filename)
        if create_as_needed:
            _make_file(fpath)
        if os.path.isfile(fpath):
            pref_files.add(fpath)
    return pref_files

if RUNNING_WINDOWS:
    preference_files = get_property_files('preference')
    font_files = get_property_files('font')
