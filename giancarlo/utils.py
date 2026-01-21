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

__all__ = [
    "default",
    "log",
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
    verbose = {
        'pos': True,
        'spin': True,
        'lorentz': True,
        'color': True,
    }
    debug = [] #'wick', 'simplify']
    latex = inside_ipython()

    @classmethod
    def new(cls):
        cls.field_id += 1
        return cls.field_id

    @classmethod
    def var(cls):
        cls.var_id += 1
        return f'x_{{{cls.var_id}}}'


class Log:
    def __init__(self):
        self.debug = lambda x: print(f'[giancarlo] : {x}')

        if default.latex:
            from IPython.display import display, Math
            self.caller = lambda x: display(Math(rf'[\text{{giancarlo}}] : {x}'))
        else:
            self.caller = self.debug        

    def __call__(self, x):
        self.caller(x)

log = Log()
