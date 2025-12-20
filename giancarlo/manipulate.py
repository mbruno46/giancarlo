from .algebra import Sum, Product

__all__ = [
    "simplify"
]

def simplify(expr):
    if not isinstance(expr, Sum):
        expr = Sum([expr])

    def split(prod):
        for i, f in enumerate(prod.factors):
            if not (f.istype('cnumber') or f.istype('symbol')):
                break
        return Product(prod.factors[0:i]), Product(prod.factors[i:])


    p, t = split(expr.factors[0])
    keys = [str(t)]
    pref = [p]
    traces = [t]
    
    for f in expr.factors[1:]:
        p, t = split(f)
        k = str(t)
        if k in keys:
            pref[keys.index(k)] += p
        else:
            keys += [k]
            pref += [p]
            traces += [t]

    for p, t in zip(pref, traces):
        print(f'( {p} ) * ( {t} )')
        
    return Sum([p.mul(t) for p, t in zip(pref, traces)])
