#!/usr/bin/python
# -*- coding: utf-8 -*-
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# By: Jason Ferrell, Sep. 2023
# https://github.com/jgferrell/
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""Classes used to update Sirsi Workflows configuration settings
related to printer paper."""
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
from typing import NoReturn, Any, Set, Tuple, List, Union
from .settings_group import SettingsGroup
NumType = Union[float, int]
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

paper_units = {'centi', 'inch'}
paper_sizes = {'a4', 'legal', 'letter', 'receipt', 'custom'}
paper_orientation = {'landscape', 'portrait'}

class Paper(SettingsGroup):
    def __init__(self, keypath='peripherals.page.') -> "Paper":
        super().__init__(keypath)
        up = lambda x: x.upper()
        self.add_setting('margin_top', float)
        self.add_setting('margin_right', float)
        self.add_setting('margin_bottom', float)
        self.add_setting('margin_left', float)
        self.add_setting('margin_unit', str, valids=paper_units, getter=up)
        self.add_setting('orientation', str, valids=paper_orientation, getter=up)
        self.add_setting('paper_size', str, valids=paper_sizes, getter=up)

    @property
    def margin_top(self) -> float:
        """Returns the value of the top margin."""
        return self.get_setting('margin_top').value
    @margin_top.setter
    def margin_top(self, m: NumType) -> NoReturn:
        """Sets the top margin."""
        self.get_setting('margin_top').value = m

    @property
    def margin_right(self) -> float:
        """Returns the value of the right margin."""
        return self.get_setting('margin_right').value
    @margin_right.setter
    def margin_right(self, m: NumType) -> NoReturn:
        """Sets the right margin."""
        self.get_setting('margin_right').value = m

    @property
    def margin_bottom(self) -> float:
        """Returns the value of the bottom margin."""
        return self.get_setting('margin_bottom').value
    @margin_bottom.setter
    def margin_bottom(self, m: NumType) -> NoReturn:
        """Sets the bottom margin."""
        self.get_setting('margin_bottom').value = m

    @property
    def margin_left(self) -> float:
        """Returns the value of the left margin."""
        return self.get_setting('margin_left').value
    @margin_left.setter
    def margin_left(self, m: NumType) -> NoReturn:
        """Sets the left margin."""
        self.get_setting('margin_left').value = m
        
    @property
    def margins(self) -> List[float]:
        """Returns a list of paper margins in clockwise order,
        beginning at top."""
        return [self.margin_top, self.margin_right, self.margin_bottom, self.margin_left]
    @margins.setter
    def margins(self, new_margins: Union[List[NumType], Tuple[NumType], NumType]) -> NoReturn:
        """If a single float or int value is provided, all margins will be
        set to that value. If a tuple or list of four int or float values is
        provided, paper margins will be set in a clockwise fashion,
        beginning by setting the top margin with the first value in
        the tuple/list."""
        if isinstance(new_margins, list) or isinstance(new_margins, tuple):
            self.margin_top = new_margins[0]
            self.margin_right = new_margins[1]
            self.margin_bottom = new_margins[2]
            self.margin_left = new_margins[3]
        else:
            # supplying a single float value sets all margins to that value
            self.margins = tuple([new_margins for _ in range(4)])
           
    @property
    def size(self) -> str:
        """Returns the current paper size."""
        return self.get_setting('paper_size').value
    @size.setter
    def size(self, new_size: str) -> NoReturn:
        """Sets new paper size. Valid settings are: a4, legal, letter,
        receipt, or custom."""
        self.get_setting('paper_size').value = new_size

    @property
    def units(self) -> str:
        """Returns the current units for settings margins or size."""
        return self.get_setting('margin_unit').value
    @units.setter
    def units(self, new_units: str) -> NoReturn:
        """Sets new units. Valid settings are: centi or inch."""
        self.get_setting('margin_unit').value = new_units

    @property
    def orientation(self) -> str:
        """Returns the current paper/print orientation."""
        return self.get_setting('orientation').value
    @orientation.setter
    def orientation(self, new_orientation: str) -> NoReturn:
        """Sets new orientation. Valid settings are: landscape or portrait."""
        self.get_setting('orientation').value = new_orientation
