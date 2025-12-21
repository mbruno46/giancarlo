from __future__ import annotations

from .algebra import Base
from .utils import default, log

__all__ = [
    "Field",
    "Propagator",
]

class Field(Base):
    def __init__(self, id: int, tag: str, anti: bool, index: dict = {}):
        self.id = id
        self.tag = tag
        self.anti = anti
        self.index = index

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
        return Propagator(self, other)
    
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

