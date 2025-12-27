#
# Copyright (C) 2025 Mattia Bruno
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

from __future__ import annotations

from .algebra import Base
from .utils import default, log

__all__ = [
    "Field",
    "Propagator",
]

class Field(Base):
    def __init__(self, id: int, tag: str, anti: bool, index: dict = {}, linestyle = 'default'):
        self.id = id
        self.tag = tag
        self.anti = anti
        self.index = index
        self.linestyle = linestyle

    def __str__(self):
        tags = ''.join(f'{self.index[key]}, ' for key in self.index if default.verbose[key])
        return f'{self.tag}({tags[:-2]})'

    def __getitem__(self, idx):
        if idx in self.index:
            return self.index[idx]
        return None
        
    def can_be_contracted(self, other: Field):
        if self.id == other.id:
            return not self.anti and other.anti
        return False

    def contract(self, other: Field):
        p = Propagator(self, other)
        p.linestyle = self.linestyle
        return p
    
class Propagator(Base):
    def __init__(self, fx, fy):
        self.fx = fx
        self.fy = fy
        
        if fx.tag=='G':
            self.tag = r'\gamma'
        else:
            self.tag = f'S_{fx.tag}'
        
        self.index = {}
        for key in fx.index:
            self.index[key] = (fx[key], fy[key])
        
        self.linestyle = 'default'

    def __str__(self):
        if self.fx.tag == 'G':
            for key in self.index:
                if default.verbose[key]:
                    if key == 'lorentz':
                        tags = rf'_{{{self.index[key][0]}}}'
                    else:
                        tags += f'({self.index[key][0]}, {self.index[key][1]})'
        else:
            tags = ''.join(f'({self.index[key][0]}, {self.index[key][1]})' for key in self.index if default.verbose[key])
        return f'{self.tag}{tags}'

    def __getitem__(self, idx):
        if idx in self.index:
            return self.index[idx]
        return (None, None)
        
    def _replace(self, rdict):
        if self.tag in rdict:
            self.tag = rdict[self.tag]
        for idx in self.index:
            if (idx in rdict) and (rdict[idx][0] == self.index[idx]):
                self.index[idx] = rdict[idx][1]

