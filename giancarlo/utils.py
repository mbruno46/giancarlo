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

import builtins

__all__ = [
    "default",
    "print"
]

def inside_ipython():
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False
    
class default:
    field_id = 0
    var_id = 0
    indices = ['spin', 'lorentz', 'color']
    verbose = {
        'pos': True,
        'spin': True,
        'lorentz': True,
        'color': True,
    }
    # debug = [] #'wick', 'simplify']
    latex = inside_ipython()

    @classmethod
    def new(cls):
        cls.field_id += 1
        return cls.field_id

    @classmethod
    def var(cls):
        cls.var_id += 1
        return f'x_{{{cls.var_id}}}'


def init_printer():
    if inside_ipython():
        from IPython.display import display, Math
        def inner(*args):
            display(Math(rf'[\text{{giancarlo}}] : {" ".join(str(a) for a in args)}'))
        return inner
    def inner(*args):
        builtins.print(rf'[\text{{giancarlo}}] : {" ".join(str(a) for a in args)}')
    return inner
    
print = init_printer()