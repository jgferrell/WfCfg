#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Sep. 2023
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Classes used to create an API for a portion of Sirsi Workflows
configuration files determined by their 'key path' (e.g.,
'peripherals.receipt.')"""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import NoReturn, Any, Set, Tuple, List, Union, Dict
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class CfgSetting:
    def __init__(self, _type: type, valids: Union[Set[Any], None] = None,
                 value: Any = None, getter = None) -> "CfgSetting":
        self._modified: bool = False
        self._type: type = _type
        self._getter = getter

        if valids is None:
            self._valids = None
        else:        
            self._valids: Set[Any] = set()
            for valid in valids:
                if type(valid) is not _type:
                    raise TypeError("Mismatch between declared type "
                                    "and declared valid value.")
                self._valids.add(valid)

        if value is not None:
            self._set_value(value)
        else:
            self._value: Any = None

    def _set_value(self, value):
        # silently convert int to float if needed
        if self._type is float and type(value) is int:
            value = float(value)            
            
        # ensure we receive correct type of value
        if not isinstance(value, self._type):
            raise TypeError("Expected %s but received %s." %\
                            (self._type, type(value)))

        # if we're validating, make sure value is valid
        if ( self._valids is not None ) and \
           ( value not in self._valids ) and not \
           ( self._type is str and value.lower() in self._valids ):
            raise ValueError("Received value '%s'. Valid values are %s." %\
                             (value, self._valids))

        # stage the validated value
        self._value = self._type(value)
        self._modified = True
            
    @property
    def value(self) -> Any:
        """Returns currently staged value."""
        if self._value is None:
            return None
        if self._getter is None:
            return self._value
        return self._getter(self._value)
    @value.setter
    def value(self, value: Any) -> NoReturn:
        """Stage a value for saving to config file."""
        self._set_value(value)

    @property
    def modified(self) -> bool:
        """True if a value has been staged; otherwise False."""
        return self._modified

    @property
    def valids(self) -> Set[Any]:
        """Returns a set of valid values."""
        return self._valids

    def __str__(self) -> str:
        return str(self.value)


class SettingsGroup:
    def __init__(self, keypath) -> "SettingGroup":
        self._settings: Dict[str, CfgSetting] = {}
        self._overrides: Dict[str, str] = {}
        self._keypath = keypath

    @property
    def keypath(self) -> str:
        return self._keypath

    @property
    def settings(self) -> List[Tuple[str, str]]:
        """Returns key/value pairs of modified settings. The key value
        is the full keypath expected by Workflows config files. Both
        key and value are strings."""
        out = []
        for key, obj in self._settings.items():
            if key in self._overrides:
                key = self._overrides[key]
            if obj.modified:
                key, value = self.keypath + key, str(obj.value)
                out.append((key, value))
        return out

    @property
    def modified(self) -> bool:
        return len(self.settings) > 0
    
    def add_setting(self, key, _type, **kwargs) -> NoReturn:
        if key not in self._settings:
            self._settings[key] = CfgSetting(_type, **kwargs)

    def override_key(self, old_key: str, new_key: str) -> NoReturn:
        if old_key not in self._settings:
            raise KeyError("Setting with key '%s' not found." % old_key)
        self._overrides[old_key] = new_key

    def override_setting(self, key: str, setting: "CfgSetting") -> NoReturn:
        self._settings[key] = setting

    def get_setting(self, key) -> "CfgSetting":
        return self._settings[key]

    def delete_setting(self, key) -> NoReturn:
        del self._settings[key]
