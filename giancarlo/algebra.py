from copy import deepcopy

from .utils import default, log
from .wick import *

__all__ = [
    "Base",
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

    def mul_no_distribute(self, other):
        return Product(self.tolist(Product) + other.tolist(Product))
        
    def __mul__(self, other):
        if isinstance(other, Sum):
            return Sum([self * f for f in other.factors])
        return self @ other

    def __matmul__(self, other):
        return Product(self.tolist(Product) + other.tolist(Product))
    
    def __add__(self, other):
        return Sum(self.tolist(Sum) + other.tolist(Sum))
        
    def __repr__(self):
        return self.__str__()

    def _repr_latex_(self):
        return f'${self.__str__()}$'

    def istype(self, ftype):
        return False
    
class Product(Base):    
    def __init__(self, factors = []):
        self.factors = factors

    @property
    def size(self):
        return len(self.factors)
    
    def __str__(self):
        if default.latex:
            return r"\,".join(map(str, self.factors))
        return " * ".join(map(str, self.factors))
    
    def simplify(self, split=False):
        def collect(ftype):
            return [f for f in self.factors if f.istype(ftype)]
        c = Product(collect('cnumber'))
        if c.size>1:
            c = c.factors[0].reduce(c.factors)
        s = Product(collect('symbol'))
        if s.size>1:
            s = s.factors[0].reduce(s.factors)
        prefactor = c * s
        fields = Product([f for f in self.factors if not (f.istype('cnumber') or f.istype('symbol'))])
        if split:
            return prefactor, fields
        return prefactor * fields
    
    def wick(self, trace_indices = [], **kwargs):
        prefactor, fields = self.simplify(split=True)

        terms = []
        for c in wick_fields(fields):
            if 'wick' in default.debug:
                log.debug(f' wick : {c}')
            tr = build_trace(Product(c()), Trace, trace_indices)
            terms.append(prefactor * Product(tr))
        
        return Sum(terms)
    
class Sum(Base):
    def __init__(self, factors):
       self.factors = []
       for f in factors:
            if isinstance(f, Sum):
                self.factors.extend(f.factors)
            else:
                self.factors.append(f)
                
    def __str__(self):
        return f"( {' + '.join(map(str, self.factors))} )"

    def __mul__(self, other):
        if isinstance(other, Sum):
            return Sum([f1 * f2 for f1 in self.factors for f2 in other.factors])
        return Sum([f * other for f in self.factors])

    def simplify(self):
        keys = []
        pref = []
        rest = []

        for f in self.factors:
            p, r = f.simplify(split = True)
            k = str(r)
            if k in keys:
                pref[keys.index(k)] += p
            else:
                keys += [k]
                pref += [p]
                rest += [r]

        if 'simplify' in default.debug:
            for p, r in zip(pref, rest):
                log.debug(f'( {p} ) * ( {r} )')
        
        return Sum([p @ r for p, r in zip(pref, rest)])
    
    def wick(self, *args, **kwargs):
        return Sum([f.wick(*args, **kwargs) for f in self.factors])

    def elements(self):
        for f in self.factors:
            yield f


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

    def cyclic(self):
        def scroll(lst, n):
            n = n % len(lst)
            return lst[-n:] + lst[:-n]

        for i in range(len(self.factors)):
            t = Trace(self.index)
            t.factors = scroll(self.factors, i)
            yield t

