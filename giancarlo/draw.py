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
    'text.usetex': True,
    'font.size': 14
})

import math

__all__ = [
    "Diagram",
    "PlotStyle"
]




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

class Points:
    def __init__(self):
        self.pts = {}
        self.nlines = {}

    def init(self, name):
        if not name in self.pts:
            self.pts[name] = None
            self.nlines[name] = 0

    def add_line(self, name):
        self.nlines[name] += 1

    def __getitem__(self, name):
        return self.pts[name]
    
    def __iter__(self):
        for p in self.pts:
            yield p

    def fill_points_circle(self, radius=1.0, center=(0.0, 0.0)):
        cx, cy = center
        n = len(self.pts)

        for i, k in enumerate(self.pts):
            angle = 2 * math.pi * i / n
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.pts[k] = (x,y)

        return
    
class Diagram:
    def __init__(self, nconn):
        plt.style.use(PlotStyle.style)

        self.fig, self.ax = plt.subplots(figsize=(5,3.5))
        self.ax.axis('off')

        self.nconn = nconn
        self.pts = Points()
        for i in range(nconn):
            self.pts.init(i)
        self.pts.fill_points_circle()

    def draw_point(self, pt, x):
        style = PlotStyle.points[x] if x in PlotStyle.points else PlotStyle.points['default']

        self.ax.scatter(*pt, **style)
        self.ax.text(*pt, f'  ${x}$')


    def __call__(self, title=''):        
        self.ax.set_title(title)
        self.fig.tight_layout()

    def line(self, x, y, s, nl):
        ls = PlotStyle.linestyles[s] if s in PlotStyle.linestyles else PlotStyle.linestyles['default']
        if s=='squiggle':
            patch = squiggle_patch(x, y)
        elif s=='default':
            patch = FancyArrowPatch(
                x, y,
                connectionstyle=f"arc3,rad={0.3 + 0.1 * nl}",
                arrowstyle='-',
                ls=ls
            )
        self.ax.add_patch(patch)

    def tadpole(self, x, s, nl):
        x1, x2 = x
        r = 0.3 + 0.1 * nl
        patch = Circle((x1+r, x2), radius=r, fill=False)
        self.ax.add_patch(patch)

    def draw_connected_diagram(self, idx, propagators):
        pts = Points()

        for p in propagators:
            x, y = p.fx['pos'], p.fy['pos']
            pts.init(x)
            pts.init(y)

        pts.fill_points_circle(radius=0.5, center=self.pts[idx])
        
        for p in propagators:
            x, y = p.fx['pos'], p.fy['pos']
            s = p.linestyle
            if x==y:
                self.tadpole(pts[x], s, pts.nlines[x])
            else:
                self.line(pts[x], pts[y], s, pts.nlines[x])
            pts.add_line(x)

        for x in pts:
            self.draw_point(pts[x], x)

        del pts
            
