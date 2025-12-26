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

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
plt.rcParams.update({
    'font.size': 14
})

import math

__all__ = [
    "Diagram",
    "PlotStyle"
]

def fill_points_circle(d: dict, radius=1.0, center=(0.0, 0.0)):
    cx, cy = center
    n = len(d)

    for i, k in enumerate(d.keys()):
        angle = 2 * math.pi * i / n
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        d[k] = (x, y)

    return


class PlotStyle:
    points = {}
    linestyles = {
        'default': '-',
    }
    style = 'default'

    @staticmethod
    def point(color='C0', size=80):
        return {'c': color, 's': size}

PlotStyle.points['default'] = PlotStyle.point()

class Diagram:
    def __init__(self, nconn):
        plt.style.use(PlotStyle.style)

        self.fig, self.ax = plt.subplots(figsize=(5,3.5))
        self.ax.axis('off')

        self.nconn = nconn
        self.pts = {}
        for i in range(nconn):
            self.pts[i] = None
        fill_points_circle(self.pts, radius=1)
        self.idx = -1
    
    def new(self):
        if self.idx<self.nconn:
            self.idx += 1


    def draw_point(self, pt, x):
        style = PlotStyle.points[x] if x in PlotStyle.points else PlotStyle.points['default']

        self.ax.scatter(*pt, **style)
        self.ax.text(*pt, f'  ${x}$')


    def __call__(self, title=''):
        self.ax.set_title(title)
        self.fig.tight_layout()

    def line(self, x, y, s):
        ls = PlotStyle.linestyles[s] if s in PlotStyle.linestyles else PlotStyle.linestyles['default']
        patch = FancyArrowPatch(
            x, y,
            connectionstyle=f"arc3,rad={0.3}",
            arrowstyle='-',
            ls=ls
        )
        self.ax.add_patch(patch)

    def tadpole(self, x, s):
        x1, x2 = x
        patch = Circle((x1+0.3, x2), radius=0.3, fill=False)
        self.ax.add_patch(patch)

    def draw_connected_diagram(self, propagators):
        self.new()
        pts = {}

        for p in propagators:
            x, y = p.fx['pos'], p.fy['pos']
            if not x in self.pts:
                pts[x] = None
            if not y in self.pts:
                pts[y] = None

        fill_points_circle(pts, radius=0.5, center=self.pts[self.idx])

        for p in propagators:
            x, y = p.fx['pos'], p.fy['pos']
            s = 'default'
            if x==y:
                self.tadpole(pts[x], s)
            else:
                self.line(pts[x], pts[y], s)
            
        for x in pts:
            self.draw_point(pts[x], x)