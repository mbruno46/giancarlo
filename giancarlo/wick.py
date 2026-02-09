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
from collections import Counter
from functools import reduce
from operator import mul
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

    signs = [f.sign for f in factors]
    pairing = {}
    for i, f0 in enumerate(factors):
        pairing[i] = []
        for j, f1 in enumerate(factors):
            if (i!=j) and f0.can_be_contracted(f1):
                pairing[i].append(j)

    def backtrack(remaining, paired, sign = 1):
        if not remaining:
            _c = Contraction(factors, list(paired), sign)
            if _c.fully_contracted:
                if _c.tag not in stack:
                    stack.append(_c.tag)
                    contractions.append(_c)
            return 
    
        for i in remaining:
            for j in set(pairing[i]) & set(remaining):
                paired.append((i,j))
                _sign = 1
                if not factors[i].boson:
                    idx = range(remaining.index(i)+1, remaining.index(j)) if j>i else range(remaining.index(j)+1, remaining.index(i)+1) 
                    _sign = reduce(mul, [signs[remaining[_idx]] for _idx in idx], 1)

                backtrack([k for k in remaining if k not in (i, j)], paired, sign * _sign)
                paired.pop()

    backtrack(list(range(len(factors))), [])
    return contractions

def wick_fields_fast_v0(factors):
    contractions = []
    stack = []

    def get_sign(remaining):
        s = 1
        for f in remaining:
            s *= f.sign
        return s

    # fcon = {}
    # for i, f0 in enumerate(factors):
    #     fcon[i] = []
    #     for j, f1 in enumerate(factors):
    #         if (i!=j) and f0.can_be_contracted(f1):
    #             fcon[i].append(j)

    def backtrack(remaining, paired, sign = 1):
        if not remaining:
            _c = Contraction(factors, list(paired), sign)
            if _c.fully_contracted:
                if _c.tag not in stack:
                    stack.append(_c.tag)
                    contractions.append(_c)
                    print(len(contractions))
            return 
        
        # for jr, j in enumerate(remaining):
        #     for ir, i in enumerate(set(fcon[j]) & set(remaining)):
        #         paired.append((j,i))
        #         _sign = 1
        #         if not factors[j].boson:
        #             if ir>jr:
        #                 _sign = get_sign(remaining[jr+1:ir])
        #             else:
        #                 _sign = get_sign(remaining[ir+1:jr+1])
                
        #         backtrack([k for k in remaining if k not in (i, j)], paired, sign * _sign)
        #         paired.pop()

        for j, f0 in enumerate(remaining):
            for i, f1 in enumerate(remaining):
                if i==j:
                    continue

                if f0.can_be_contracted(f1):
                    i0 = factors.index(f0)
                    i1 = factors.index(f1)
                    paired.append((i0,i1))
                    _sign = 1
                    if not f0.boson:
                        if i>j:
                            _sign = get_sign(remaining[j+1:i])
                        else:
                            _sign = get_sign(remaining[i+1:j+1])
                    
                    backtrack([f for f in remaining if f not in (f0, f1)], paired, sign * _sign)
                    paired.pop()

    backtrack(factors, [])
    return contractions

def build_trace(expr, Trace_class, indices):
    if not indices:
        return expr.factors
        
    traces = []
    stack = []

    def eq_up_to_none(list1, list2):
        print(list1, list2)
        return all(
            (a is None or b is None or a == b)
            for a, b in zip(list1, list2)
        )
    
    def pass_index_over(idx0, idx1):
        return [idx0[i] if val is None else val for i, val in enumerate(idx1)]


    # here we assume indices appear in pairs
    def DFS(idx):
        for i, f in enumerate(expr.factors):
            if i not in stack:
                if ([f[idx][0] for idx in indices] == idx):
                    traces[-1] *= f
                    stack.append(i)
                    DFS([f[idx][1] for idx in indices])
                else:
                    if (f.symmetric) and ([f[idx][1] for idx in indices] == idx):
                        traces[-1] *= f
                        stack.append(i)
                        DFS([f[idx][0] for idx in indices])

    for i, f in enumerate(expr.factors):
        if i not in stack:
            traces += [Trace_class(indices)]
            DFS([f[idx][0] for idx in indices])

    return [t() for t in traces]

    

class ConnectedSet_v0:
    # class IndexStack:
    #     def __init__(self, val):
    #         self.data = {}
    #         for key in val:
    #             self.data[key] = [val[key]]

    #     def append(self, val):
    #         for key in self.data:
    #             self.data[key] += val[key]

    def __init__(self, i, ix, iy):
        self.indices = [{key: [ix[key]] for key in ix}, {key: [iy[key]] for key in iy}]
        self.idx = [i]

    def append(self, i, *val):
        for j, v in enumerate(val):
            for key in v:
                self.indices[j][key].append(v[key])
        self.idx.append(i)

    def contains(self, j, val):
        return all(v in self.indices[j][k] for k, v in val.items()) # if not v is None)

    @property
    def closed(self):        
        def inner(key):
            cx = Counter(self.indices[0][key])
            cy = Counter(self.indices[1][key])
            if (None in cy) and (cy[None] == len(self.indices[1][key])):
                return False
            for iy in self.indices[1][key]:
                if cx[iy] == 0:
                    return False
            return True
        return all(inner(key) for key in self.indices[1])
    
    def __call__(self, factors):
        return [factors[i] for i in self.idx], self.closed

def split_connected_v0(expr, indices, pairs_only = True):
    stack = []

    def get_indices(prop, i):
        return {idx: prop[idx][i] for idx in indices}
    
    for i, f in enumerate(expr.factors):
        # ix, iy = f[index][0], f[index][1]
        i0 = get_indices(f, 0)
        i1 = get_indices(f, 1)

        istack = len(stack)
        for j, c in enumerate(stack):
            if pairs_only:
                #print(i0, c.indices[1], c.contains(1, i0))
                if (c.contains(1, i0)):
                    istack = j    
                    break
                if (f.symmetric and c.contains(1, i1)):
                    istack = j
                    f.swap()
                    break
            else:
                if (c.contains(1, i0) or c.contains(1, i1) or c.contains(0, i0)):
                    istack = j
                    break

        if istack < len(stack):
            stack[istack].append(i, i0, i1)
        else:
            stack.append(ConnectedSet(i, i0, i1))

    return [s(expr.factors) for s in stack]

class ConnectedSet:
    def __init__(self, i):
        self.fidx = []
        self.append(i)

    def append(self, i):
        self.fidx.append(i)

    def __call__(self, factors):
        return [factors[i] for i in self.fidx]

def split_connected(expr, index):
    stack = []
    paired = []
    
    def backtrace(idx):
        for i, f in enumerate(expr.factors):
            if (i not in paired):
                if (f.symmetric and f[index][1] == idx):
                    f.swap()
                if (f[index][0] == idx):
                    stack[-1].append(i)
                    paired.append(i)
                    backtrace(f[index][1])

    for i, f in enumerate(expr.factors):
        if (i not in paired):
            stack.append(ConnectedSet(i))
            paired.append(i)
            backtrace(f[index][1])

    return [s(expr.factors) for s in stack]