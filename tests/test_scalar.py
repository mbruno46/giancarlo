import giancarlo as gc

phir = gc.RealScalarField(r'\phi')
phi, phidag = gc.ComplexScalarField(r'\phi')
A = gc.PhotonField()

op_r = lambda x: phir(x) * phir(x)
op = lambda x: phidag(x) * phi(x)

def phi4(x):
    return gc.CNumber(1,4*3*2) * gc.Symbol(r'\lambda') * phir(x) * phir(x) * phir(x) * phir(x)

gc.print(phi4('z'))

tests = {
    r'( +S_{\phi}(x, y) )': (phir('x') * phir('y')).wick(),
    r'\phi(x) * \phi(x)': op_r('x'),
    r'( +S_{\phi}(x, x) * S_{\phi}(y, y)+2 * S_{\phi}(x, y) * S_{\phi}(x, y) )': (op_r('x') * op_r('y')).wick(),
    r'( +\frac{1}{8} * \lambda * S_{\phi}(z, z) * S_{\phi}(z, z) )': phi4('z').wick(),
    r'( +S_{\phi}(y, x) )': (phidag('x') * phi('y')).wick(),
    r'( +S_{\phi}(x, y) )': (phi('x') * phidag('y')).wick(),
    r'( +S_{\phi}(x, x) * S_{\phi}(y, y)+S_{\phi}(x, y) * S_{\phi}(y, x) )': (op('x') * op('y')).wick(),
    r'( +S_{A}(x, y)(\mu, \nu) )': (A('x', r'\mu') * A('y', r'\nu')).wick()
}

def test_scalar():
    for key, value in tests.items():
        assert key == str(value)