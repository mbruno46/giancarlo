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

from copy import deepcopy
import math

from .utils import *
from .wick import *
from .draw import *

__all__ = [
    "Base",
    "CNumber",
    "Symbol"
]

class Base:        
    def wick(self):
        return self

    def _replace(self, rdict):
        pass

    def replace(self, rdict):
        def inner(x):
            if hasattr(x, "factors"):
                for f in x.factors:
                    inner(f)
            else:
                x._replace(rdict)

        _expr = deepcopy(self)
        inner(_expr)
        return _expr
        
    def tolist(self, ctype):
        return self.factors if isinstance(self, ctype) else [self] 

    # def mul_no_distribute(self, other):
        # return Product(self.tolist(Product) + other.tolist(Product))
        
    def __mul__(self, other):
        if isinstance(other, Sum):
            return Sum([self * f for f in other.factors])
        return self @ other

    # def __rmul__(self, other):
    #     return Product([other] + [self])

    def __matmul__(self, other):
        return Product(self.tolist(Product) + other.tolist(Product))
    
    def __add__(self, other):
        return Sum(self.tolist(Sum) + other.tolist(Sum))
    
    def __sub__(self, other):
        return self + CNumber(-1) * other #.tolist(Sum)
    
    def __pow__(self, n):
        out = self
        for _ in range(1,n):
            out *= self
        return out
    
    ####

    def __repr__(self):
        return self.__str__()

    def _repr_latex_(self):
        return f'${self.__str__()}$'

    def istype(self, ftype):
        return False
    
    def __getitem__(self, idx):
        return self.factors[idx]
    
    def draw(self):
        pass


class Product(Base):
    def __init__(self, factors = []):
        # flattens products of products
        _factors = []
        for f in factors:
            if isinstance(f, Product):
                _factors.extend(f.factors)
            else:
                _factors.append(f)

        # cnumber first, symbols second
        cs = []
        ss = []
        rs = []
        for f in _factors:
            if isinstance(f, CNumber):
                cs.append(f)
            elif isinstance(f, Symbol):
                ss.append(f)
            else:
                rs.append(f)
        
        # automatic reductions of products
        self.cnum = CNumber.reduce(cs)
        if self.cnum and self.cnum[0].numerator == 0:
            self.symb = []
            self.data = []
        else:
            self.symb = Symbol.reduce(ss)
            self.data = rs

    @property
    def factors(self):
        return self.cnum + self.symb + self.data

    @property
    def prefactor(self):
        return Product(self.cnum + self.symb)
    
    @property
    def size(self):
        return len(self.factors)
    
    def __str__(self, latex=default.latex):
        if latex:
            return r"\,".join(map(str, self.factors))
        return " * ".join(map(str, self.factors))
    
    # def __eq__(self, other):
        # return isinstance(other, Product) and self.factors == other.factors
    
    # def simplify(self, split=False):
    #     prefactor = 
    #     if split:
    #         return prefactor, other
    #     return prefactor * other
    
    def wick(self, trace_indices = [], **kwargs):
        terms = []
        for c in wick_fields_fast(self.data):
            if 'wick' in default.debug:
                log.debug(f' wick : {c}')
            tr = build_trace(Product(c()), Trace, trace_indices)
            terms.append(self.prefactor * Product(tr))
        
        return Sum(terms)
    
    def draw(self):
        # remove prefactors
        _data = [f for f in self.factors if not isinstance(f, (Sum, CNumber, Symbol))]
        # remove traces
        _no_traces = []
        for f in _data:
            if isinstance(f, Trace):
                _no_traces.extend(f.factors)
            else:
                _no_traces.append(f)
        # keep only propagators
        _props = [p for p in _no_traces if p['pos']!=(None,None)]
        connected = build_trace(Product(_props), Trace, indices=['pos'])

        g = Diagram(len(connected))
        for conn in connected:
            g.draw_connected_diagram(conn.factors)
        g(self._repr_latex_())


class Sum(Base):
    def __init__(self, factors = []):
        _factors = []
        for f in factors:
            if isinstance(f, Sum):
                _factors.extend(f.factors)
            else:
                _factors.append(f)
        
        count = Counter()
        for f in _factors:
            count(f)

        self.factors = []
        for f in count.unique():
            if count[f]==0.0:
                continue
            elif count[f]==1.0:
                self.factors.append(f if isinstance(f, Product) else Product([f]))
            else:
                self.factors.append(count[f] * f)


    def __str__(self):
        return f"( {' + '.join(map(str, self.factors))} )"

    def __mul__(self, other):
        if isinstance(other, Sum):
            return Sum([f1 * f2 for f1 in self.factors for f2 in other.factors])
        return Sum([f * other for f in self.factors])


    def simplify(self):
        data = {}

        for f in self.factors:
            p, d = f.prefactor, Product(f.data)
            k = str(d)
            if k in data:
                data[k][0] += p
            else:
                data[k] = [p, d]

        if 'simplify' in default.debug:
            for key in data:
                log.debug(f'( {data[key][0]} ) * ( {data[key][1]} )')

        return Sum([data[key][0] @ data[key][1] for key in data])
    
    def wick(self, *args, **kwargs):
        return Sum([f.wick(*args, **kwargs) for f in self.factors])

    def elements(self):
        for f in self.factors:
            yield f

    def draw(self):
        for f in self.factors:
            f.draw()

class Trace(Base):
    def __init__(self, indices: list):
        self.factors = []
        self.indices = indices

    def __imul__(self, other):
        self.factors.append(other)
        return self
    
    def __str__(self):
        tag = ' '.join(rf'\mathrm{{Tr}}_\mathrm{{{idx}}}' for idx in self.indices if idx!='pos')
        return f'{tag} [ {Product(self.factors)} ]'

    # checks that trace effectively is closed, otherwise returns product
    def __call__(self):
        indices0 = [self.factors[0].fx[idx] for idx in self.indices]
        indices1 = [self.factors[-1].fy[idx] for idx in self.indices]
        if indices0 == indices1:
            return self
        return Product(self.factors)
    
    # def cyclic(self):
    #     def scroll(lst, n):
    #         n = n % len(lst)
    #         return lst[-n:] + lst[:-n]

    #     for i in range(len(self.factors)):
    #         t = Trace(self.index)
    #         t.factors = scroll(self.factors, i)
    #         yield t

    # def draw(self, g):
    #     lines = [f for f in self.factors if f.tag[0] == 'S']
    #     if len(lines)==1:
    #         g.draw_tadpole(lines[0].fx['pos'])
    #     else:
    #         loop = g.new_loop()
    #         for f in self.factors:
    #             if f.tag[0] == 'S': # it's a propagator
    #                 loop.add_line(f.fx['pos'], f.fy['pos'])
    #         loop()
    #     return

class CNumber(Base):
    def __init__(self, numerator, denominator=1):
        if not isinstance(numerator, int):
            assert denominator==1
            self.numerator = numerator
            self.denominator = 1
        else:
            assert isinstance(denominator, int)
            gcd = math.gcd(numerator, denominator)
            self.numerator = numerator // gcd
            self.denominator = denominator // gcd
        
    def __add__(self, other):
        if isinstance(other, CNumber):
            return CNumber(self.numerator*other.denominator + self.denominator*other.numerator, self.denominator*other.denominator)
        return super().__add__(other)
    
    def __mul__(self, other):
        if isinstance(other, CNumber):
            return CNumber(self.numerator*other.numerator, self.denominator*other.denominator)
        return super().__mul__(other)
    
    def __eq__(self, value):
        _value = self.numerator/self.denominator
        return _value == value
    
    def __str__(self):
        if self.denominator==1.0:
            if self.numerator==1.0:
                return ''
            return f'{self.numerator}'
        return rf'\frac{{{self.numerator}}}{{{self.denominator}}}'

    def reduce(cnumbers: list) -> list:
        if not cnumbers:
            return []
        p = cnumbers[0]
        for c in cnumbers[1:]:
            p *= c
        return [p]

class Symbol(Base):
    def __init__(self, value: str, pow: int = 1):
        self.value = value
        self.pow = pow
        
    def __str__(self):
        return self.value + (f'^{self.pow}' if self.pow>1 else '')

    def reduce(symbols: list) -> list:
        if not symbols:
            return []
        
        vals = [s.value for s in symbols]
        pows = [s.pow for s in symbols]

        _vals = []
        _pows = []
        for v, p in zip(vals, pows):
            if v not in _vals:
                _vals.append(v)
                _pows.append(p)
            else:
                i = _vals.index(v)
                _pows[i] += p

        return sorted([Symbol(_v,_p) for _v, _p in zip(_vals, _pows)], key=str)


class Counter:
    def __init__(self):
        self.data = {}
        self.count = {}

    def __call__(self, item):
        f = CNumber(1)
        if isinstance(item, Product):
            cn, item = item.cnum, Product(item.symb + item.data)
            if cn:
                f = cn[0]
                
        key = str(item)
        if key in self.count:
            self.count[key] += f
        else:
            self.count[key] = f
            self.data[key] = item

    def __getitem__(self, item):
        key = str(item)
        return self.count[key]
    
    def unique(self):
        return [self.data[key] for key in self.count] 