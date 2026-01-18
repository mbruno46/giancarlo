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

from itertools import permutations
from .utils import default, log

class Contraction:
    def __init__(self, fields, pairs = [], sign = 1):
        self.pairs = pairs
        self._tag = None
        self.fields = fields
        self.sign = sign

    # def append(self, i, j=None):
    #     self.pairs.append((i,j))

    def __repr__(self):
        return str(self.__dict__)
    
    def __call__(self):
        out = []
        for p in self.pairs:
            if p[1] is None:
                raise
            else:
                out.append(self.fields[p[0]].contract(self.fields[p[1]]))
        return out

    @property
    def fully_contracted(self):
        for p in self.pairs:
            if None in p:
                return False
        return True
        
    @property
    def tag(self):    
        if self._tag is None:
            self._tag = tuple(sorted(tuple(sorted(t)) for t in self.pairs))
        return self._tag

def wick_fields(expr):
    idx = list(range(expr.size))

    stack = []
    contractions = []
    n = len(idx)
    if (n%2)>0:
        raise
    
    ip = 0
    for p in permutations(idx):
        _c = Contraction(expr.factors)
        for i in range(0, n, 2):
            pi = p[i]
            pj = p[i+1]
            if expr.factors[pi].can_be_contracted(expr.factors[pj]):
                _c.append(pi, pj)
            else:
                _c.append(pi)
                _c.append(pj)
                break

        # checks for left-over uncontracted fields
        if _c.fully_contracted:
            if _c.tag not in stack:
                stack.append(_c.tag)
                contractions.append(_c)
        
            ip += 1
            if 'wick' in default.debug:
                log.debug(f'{ip} / {len(idx)}')

    return contractions


def wick_fields_fast(factors):
    contractions = []
    stack = []

    def get_sign(remaining):
        s = 1
        for f in remaining:
            s *= f.sign
        return s
    
    def backtrack(remaining, paired, sign = 1):
        if not remaining:
            _c = Contraction(factors, list(paired), sign)
            if _c.fully_contracted:
                if _c.tag not in stack:
                    stack.append(_c.tag)
                    contractions.append(_c)
            return 
        
        for j in range(len(remaining)):
            f0 = remaining[j]

            for i in range(len(remaining)):
                if i==j:
                    continue
                f1 = remaining[i]

                if f0.can_be_contracted(f1):
                    i0 = factors.index(f0)
                    i1 = factors.index(f1)
                    paired.append((i0,i1))
                    _sign = get_sign(remaining[j+1:i+1])
                    
                    backtrack([f for f in remaining if f not in (f0, f1)], paired, sign * _sign)
                    paired.pop()

    backtrack(factors, [])
    return contractions

def build_trace(expr, Trace_class, indices):
    if not indices:
        return expr.factors
        
    traces = []
    stack = []

    # here we assume indices appear in pairs
    def DFS(idx):
        for i, f in enumerate(expr.factors):
            if i not in stack:
                if ([f[idx][0] for idx in indices] == idx):
                    traces[-1] *= f
                    stack.append(i)
                    DFS([f[idx][1] for idx in indices])

    for i, f in enumerate(expr.factors):
        if i not in stack:
            traces += [Trace_class(indices)]
            DFS([f[idx][0] for idx in indices])

    return [t() for t in traces]
