from __future__ import annotations

from .algebra import Base, Product
from .utils import default, log

__all__ = [
    "CNumber",
    "Symbol",
    "Field",
    "Propagator",
]

class QFTBase(Base):
    def istype(self, t):
        if isinstance(self, Symbol):
            return t=='symbol'
        elif isinstance(self, CNumber):
            return t=='cnumber'
        elif isinstance(self, Field):
            return t=='field'


class CNumber(QFTBase):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'{self.value}'

    def reduce(self, factors):
        for f in factors:
            if f.istype('cnumber'):
                self.value *= f.value
        return self


class Symbol(QFTBase):
    def __init__(self, value: str, pow: int = 1):
        self.value = value
        self.pow = pow
        
    def __str__(self):
        return self.value + (f'^{self.pow}' if self.pow>1 else '')

    def reduce(self, factors):
        vals = [f.value for f in factors if f.istype('symbol')]
        pows = [f.pow for f in factors if f.istype('symbol')]
        
        if not vals:
            return Product()

        _vals = []
        _pows = []
        for v, p in zip(vals, pows):
            if v not in _vals:
                _vals.append(v)
                _pows.append(p)
            else:
                i = _vals.index(v)
                _pows[i] += p

        pref = None
        for i in range(len(_vals)):
            if i==0:
                pref = Symbol(_vals[i], _pows[i])
            else:
                pref = pref * Symbol(_vals[i], _pows[i])
        return pref

class Field(QFTBase):
    def __init__(self, id: int, tag: str, anti: bool, index: dict = {}):
        self.id = id
        self.tag = tag
        # self.coor = coor
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

