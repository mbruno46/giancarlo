__all__ = []

from .algebra import *
from .qft import *
from .utils import *
from .manipulate import *
from .draw import *

__all__.extend(algebra.__all__)
__all__.extend(qft.__all__)
__all__.extend(utils.__all__)
__all__.extend(manipulate.__all__)
__all__.extend(draw.__all__)

def ScalarField(flavor):
    id = default.new()
    def phi(pos):
        return Field(id, flavor, False, {'pos': pos})
    def phidag(pos):
        return Field(id, rf'{{{flavor}}}^\dagger', True, {'pos': pos})
    return phi, phidag

def SpinorField(flavor):
    id = default.new()
    def psi(pos, spin):
        return Field(id, flavor, False, {'pos': pos, 'spin': spin})
    def psibar(pos, spin):
        return Field(id, rf'\bar{{{flavor}}}', True, {'pos': pos, 'spin': spin})
    return psi, psibar

def DiracGamma(mu, a, b, ):
    id = default.new()
    return Field(id, 'G', False, {'lorentz': mu, 'spin': a}) * Field(id, 'G', True, {'lorentz': mu, 'spin': b})
