import giancarlo as gc

a, b = gc.Symbol('a'), gc.Symbol('b')

tests = {
    '4.5': gc.CNumber(4.5),
    r'\frac{4}{5}': gc.CNumber(4, 5),
    r'\frac{9}{16}': gc.CNumber(6,8) ** 2,
    r'-\frac{1}{2}': gc.CNumber(1,2) + gc.CNumber(-1),
    'a * b': a*b,
    'a^3': a**3,
    '( +2 * a * b+b^2 )': (a + b)**2 - a*a,
    '0': a * gc.CNumber(1,2) - a + gc.CNumber(1,2) * a,
}

def test_cnumber_symbol():
    for key, value in tests.items():
        assert key == str(value)