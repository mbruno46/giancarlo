from itertools import permutations
from .utils import default, log

class Contraction:
    def __init__(self, fields, pairs = []):
        self.pairs = pairs
        self._tag = None
        self.fields = fields
        
    def append(self, i, j=None):
        self.pairs.append((i,j))

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


def wick_fields_fast(expr):
    contractions = []
    stack = []

    def backtrack(remaining, paired):
        if not remaining:
            _c = Contraction(expr.factors, list(paired))
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
                    i0 = expr.factors.index(f0)
                    i1 = expr.factors.index(f1)
                    paired.append((i0,i1))

                    backtrack([f for f in remaining if f not in (f0, f1)], paired)
                    paired.pop()

    backtrack(expr.factors, [])
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

    return traces
        
    