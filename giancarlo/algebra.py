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
from itertools import permutations, combinations
import math

# from .utils import *
from .wick import *
from .draw import *
from .utils import default

__all__ = [
    "Base",
    "CNumber",
    "Symbol",
    "ExchangeSymmetry"
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

    def __mul__(self, other):
        if isinstance(other, Sum):
            return Sum([self * f for f in other.factors])
        return self @ other

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

    def __len__(self):
        if hasattr(self, "factors"):
            return len(self.factors)
        else:
            return 1
    
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

    @property
    def sign(self):
        if hasattr(self, "boson"):
            return 1 if self.boson else -1
        return 1

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
        ps = Sum()
        rs = []
        for f in _factors:
            if isinstance(f, CNumber):
                cs.append(f)
            elif isinstance(f, Symbol):
                ss.append(f)
            elif isinstance(f, Sum):
                ps += f
            else:
                rs.append(f)
        
        # automatic reductions of products
        self.cnum = CNumber.reduce(cs)
        if self.cnum and self.cnum[0].numerator == 0:
            self.symb = []
            self.sum = []
            self.data = []
        else:
            self.symb = Symbol.reduce(ss)
            self.sum = [ps] if len(ps)>0 else []
            self.data = rs

    @property
    def factors(self):
        return self.cnum + self.symb + self.sum + self.data

    @property
    def prefactor(self):
        return Product(self.cnum + self.symb + self.sum)
    
    @property
    def size(self):
        return len(self.factors)
    
    def __str__(self, latex=default.latex):
        if latex:
            return r"\,".join(map(str, self.factors))
        return " * ".join(map(str, self.factors))
    
    def is_negative(self):
        if self.cnum:
            return self.cnum[0].negative
        return False

    def wick(self):
        terms = []
        for c in wick_fields_fast(self.data):
            if 'wick' in default.debug:
                log.debug(f' wick : {c}')
            terms.append(CNumber(c.sign) * self.prefactor * Product(c()))
        return Sum(terms)
    
    def draw(self, title=''):
        # remove prefactors
        _data = [f for f in self.factors if not isinstance(f, (Sum, CNumber, Symbol))]
        # remove tensorproducts
        _no_tp = []
        for f in _data:
            if isinstance(f, ContractedProduct):
                _no_tp.extend(f.factors)
            else:
                _no_tp.append(f)
        # keep only physical propagators
        _props = [p for p in _no_tp if p['pos']!=(None,None)]
        connected = topologies(Product(_props)) #, 'pos')

        g = Diagram(len(connected))
        for i, conn in enumerate(connected):
            g.draw_connected_diagram(i, conn)
        g(self._repr_latex_() if title=='' else title)

    # def trace(self, indices = []):
    #     result = self.prefactor
    #     for factors, closed in split_connected(Product(self.data), indices):
    #         result *= Trace(factors, indices) if closed else Product(factors)
    #     return result

    def contract(self, index):
        if not index:
            return self
        result = self.prefactor
        for factors in split_connected(Product(self.data), index):
            result *= ContractedProduct(factors, index)
        return result

    def permutations(self):
        assert sum([f.sign for f in self.factors]) == len(self.factors)
        for p in permutations(self.factors):
            yield Product(list(p))

    def __contains__(self, other):
        A = other.cyclic_permutations() if isinstance(other, ContractedProduct) else [str(other)]
        B = [str(f) for f in self.factors]
        return bool(set(A) & set(B))    

class ContractedProduct(Base):
    def __init__(self, factors: list, index):
        self.factors = list(factors)
        self.index = index
        a, b = None, None
        for f in factors:
            if not f[index][0] is None:
                if a is None:
                    a = f[index][0]
            if not f[index][1] is None:
                b = f[index][1] 
        self.open_indices = (a, b)
        if a==b:
            if not a is None:
                self.repr_0 = rf'\mathrm{{Tr}}_\mathrm{{{index}}} \big['
                self.repr_1 = rf' \big]'
            else:
                self.repr_0 = self.repr_1 = ''
        else:
            self.repr_0 = rf'\big['
            self.repr_1 = rf' \big]({a},{b})'

    def __str__(self):
        default.verbose[self.index] = False
        s = str(Product([f.stripe(self.index) for f in self.factors]))
        default.verbose[self.index] = True
        return self.repr_0 + s + self.repr_1

    def __getitem__(self, idx):
        if idx == self.index:
            return self.open_indices
        conn = split_connected(Product([f for f in self.factors if not f[idx][0] is None]), idx)
        if len(conn)==1:
            return conn[0][0][idx][0], conn[0][-1][idx][1]
        raise Exception(f'Did not manage to connect all indices of type {idx}')
    
    def swap(self):
        pass

    def stripe(self, index):
        return self

    def cyclic_permutations(self):
        a, b = self.open_indices
        if a == b:
            return [str(ContractedProduct(self.factors[i:] + self.factors[:i], self.index)) for i in range(len(self.factors))]
        return [str(self)]
    
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
        if not self.factors:
            return "0"
        func = lambda f: str(f) if f.is_negative() else '+'+str(f)
        return f"( {''.join(map(func, self.factors))} )"

    def __mul__(self, other):
        if isinstance(other, Sum):
            return Sum([f1 * f2 for f1 in self.factors for f2 in other.factors])
        return Sum([f * other for f in self.factors])

    def simplify(self, *args):
        data = {}
        
        symmetries = [IdentitySymmetry()]# if not any(isinstance(x, IdentitySymmetry) for x in args) else []
        symmetries.extend(list(args))

        symmetries_combined = [
            GenericSymmetry(combo)
            for r in range(1, len(symmetries) + 1)
            for combo in combinations(symmetries, r)
        ]

        def add_to_data(p, expr: Product):
            for k, (_, d) in data.items():
                for s in symmetries_combined:
                    count = 0
                    for element in d.factors:
                        if s(element) in expr:
                            count += 1
                    if count == len(d):
                        data[k][0] += p
                        return

            k = str(expr)
            data[k] = [p, expr]
            return
        
        for f in self.factors:
            p, d = f.prefactor, Product(f.data)
            add_to_data(p, d)

        if 'simplify' in default.debug:
            for key in data:
                log.debug(f'( {data[key][0]} ) * ( {data[key][1]} )')

        return Sum([data[key][0] @ data[key][1] for key in data if data[key][0].factors])
    
    def wick(self):
        return Sum([f.wick() for f in self.factors])

    def contract(self, index):
        return Sum([f.contract(index) for f in self.factors])
    
    def trace(self, indices = []):
        return Sum([f.trace(indices) for f in self.factors])
    
    def elements(self):
        for f in self.factors:
            yield f

    def draw(self):
        for f in self.factors:
            f.draw()

    
class CNumber(Base):
    def __init__(self, numerator, denominator=1):
        def snap_int(x, tol=1e-12):
            if math.isclose(x, round(x), abs_tol=tol):
                return int(round(x))
            return x
        
        if isinstance(numerator,int) and isinstance(denominator, int):
            gcd = math.gcd(numerator, denominator)
            self.numerator = numerator // gcd
            self.denominator = denominator // gcd
        else:
            for key in ['numerator', 'denominator']:
                number = locals()[key]
                if isinstance(number, complex):
                    setattr(self, key, number.real if number.imag==0.0 else number)
                else:
                    setattr(self, key, snap_int(number))

        if isinstance(self.numerator, complex):
            self.negative = False
        else:
            self.negative = self.numerator * self.denominator < 0

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
        sign = '-' if self.negative else ''
        if self.denominator==1.0:
            if self.numerator in (1.0, -1.0):
                return f'{sign}'
            if isinstance(self.numerator, complex):
                return f'{self.numerator}'
            return f'{sign}{abs(self.numerator)}'
        return rf'{sign}\frac{{{abs(self.numerator)}}}{{{self.denominator}}}'

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

    def __eq__(self, other):
        return isinstance(other, Symbol) and [self.value, self.pow] == [other.value, other.pow]
    
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
            cn, item = item.cnum, Product(item.symb + item.sum + item.data)
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
    

class GenericSymmetry:
    def __init__(self, symmetries):
        self.symmetries = symmetries

    def __call__(self, target: Product):
        tmp = target
        for s in self.symmetries:
            tmp = s(tmp)
        return tmp

class IdentitySymmetry:
    def __call__(self, target: Product):
        return target
    
class ExchangeSymmetry:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, target):
        # if propagator is already symmetric no need to apply symmetry
        if hasattr(target, 'symmetric'):
            if target.symmetric:
                return target
        r1 = {}
        r2 = {}
        r3 = {}
        for k, v in self.kwargs.items():
            tmp = f'aaaaa{k}'
            r1[k] = [v[0], tmp]
            r2[k] = [v[1], v[0]]
            r3[k] = [tmp, v[1]]
        return target.replace(r1).replace(r2).replace(r3)