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

__all__ = []

from .algebra import *
from .qft import *
from .utils import *
from .draw import *

__all__.extend(algebra.__all__)
__all__.extend(qft.__all__)
__all__.extend(utils.__all__)
__all__.extend(draw.__all__)

def RealScalarField(flavor):
    id = default.new()
    def phi(pos):
        return RealField(id, flavor, {'pos': pos})
    return phi
  
def ComplexScalarField(flavor):
    id = default.new()
    def phi(pos):
        return ComplexField(id, flavor, False, True, {'pos': pos})
    def phidag(pos):
        return ComplexField(id, rf'{{{flavor}}}^\dagger', True, True, {'pos': pos})
    return phi, phidag

def PhotonField():
    id = default.new()
    def A(pos, mu):
        return RealField(id, 'A', {'pos': pos, 'lorentz': mu}, linestyle='squiggle')
    return A

def SpinorField(flavor):
    id = default.new()
    def psi(pos, spin):
        return ComplexField(id, flavor, False, False, {'pos': pos, 'spin': spin})
    def psibar(pos, spin):
        return ComplexField(id, rf'\bar{{{flavor}}}', True, False, {'pos': pos, 'spin': spin})
    return psi, psibar

def QuarkField(flavor):
    id = default.new()
    def psi(pos, spin, color):
        return ComplexField(id, flavor, False, False, {'pos': pos, 'spin': spin, 'color': color})
    def psibar(pos, spin, color):
        return ComplexField(id, rf'\bar{{{flavor}}}', True, False, {'pos': pos, 'spin': spin, 'color': color})
    return psi, psibar

def DiracGamma(mu, a, b):
    id = default.new()
    return ComplexField(id, 'G', False, True, {'lorentz': mu, 'spin': a}) * ComplexField(id, 'G', True, True, {'lorentz': mu, 'spin': b})