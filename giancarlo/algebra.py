from copy import deepcopy
import math

from .utils import default, log
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
    
    def __getitem__(self, idx):
        return self.factors[idx]
    
    def draw(self):
        pass


class Product(Base):
    def __init__(self, factors = []):
        self.factors = []
        for f in factors:
            if isinstance(f, Product):
                self.factors.extend(f.factors)
            else:
                self.factors.append(f)

    @property
    def size(self):
        return len(self.factors)
    
    def __str__(self):
        if default.latex:
            return r"\,".join(map(str, self.factors))
        return " * ".join(map(str, self.factors))
    
    def simplify(self, split=False):
        cs = []
        ss = []
        rs = []
        for f in self.factors:
            if isinstance(f, CNumber):
                cs.append(f)
            elif isinstance(f, Symbol):
                ss.append(f)
            else:
                rs.append(f)
        
        prefactor = CNumber.reduce(cs) * Symbol.reduce(ss)
        other = Product(rs)

        if split:
            return prefactor, other
        return prefactor * other
    
    def wick(self, trace_indices = [], **kwargs):
        prefactor, fields = self.simplify(split=True)

        terms = []
        for c in wick_fields_fast(fields):
            if 'wick' in default.debug:
                log.debug(f' wick : {c}')
            tr = build_trace(Product(c()), Trace, trace_indices)
            terms.append(prefactor * Product(tr))
        
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
        print('quaa ', _props)
        connected = build_trace(Product(_props), Trace, indices=['pos'])

        g = Graph(len(connected))
        for conn in connected:
            g.draw_connected_diagram(conn.factors)
        g(self._repr_latex_())

class Sum(Base):
    def __init__(self, factors = []):
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
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'{self.value}'

    def reduce(cnumbers: list) -> Product:
        if not cnumbers:
            return Product()
        return Product([CNumber(math.prod([c.value for c in cnumbers]))])


class Symbol(Base):
    def __init__(self, value: str, pow: int = 1):
        self.value = value
        self.pow = pow
        
    def __str__(self):
        return self.value + (f'^{self.pow}' if self.pow>1 else '')

    def reduce(symbols: list) -> Product:
        if not symbols:
            return Product()
        
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

        return Product([Symbol(_v,_p) for _v, _p in zip(_vals, _pows)])