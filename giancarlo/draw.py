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
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.path import Path
import math

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


def squiggle_patch(p0, p1, n_periods=5, amp=0.05, n_points=300, **patch_kwargs):
    x0, y0 = p0
    x1, y1 = p1

    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)

    nx, ny = -dy / length, dx / length

    verts = []
    codes = []
    for i in range(n_points):
        t = i / (n_points-1)
        x = x0 + dx * t
        y = y0 + dy * t

        # Sinusoidal offset
        phase = 2 * math.pi * n_periods * t
        offset = amp * math.sin(phase)

        x += nx * offset
        y += ny * offset

        verts.append((x,y))
        codes.append(Path.MOVETO if i==0 else Path.LINETO)

    path = Path(verts, codes)
    return patches.PathPatch(path, fill=False, **patch_kwargs)



class PlotStyle:
    points = {}
    linestyles = {
        'default': '-',
        'squiggle': '',
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
        for x in self.pts:
            if type(x) is str:
                self.draw_point(self.pts[x], x)
        
        self.ax.set_title(title)
        self.fig.tight_layout()

    def line(self, x, y, s):
        ls = PlotStyle.linestyles[s] if s in PlotStyle.linestyles else PlotStyle.linestyles['default']
        if s=='squiggle':
            patch = squiggle_patch(x, y)
        elif s=='default':
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

        for pt in pts:
            self.pts[pt] = pts[pt]
        del pts

        for p in propagators:
            x, y = p.fx['pos'], p.fy['pos']
            s = p.linestyle
            if x==y:
                self.tadpole(self.pts[x], s)
            else:
                self.line(self.pts[x], self.pts[y], s)