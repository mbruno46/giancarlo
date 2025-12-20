import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

import math

__all__ = ["Graph"]

def fill_points_circle(d: dict, radius=1.0, center=(0.0, 0.0)):
    cx, cy = center
    n = len(d)

    for i, k in enumerate(d.keys()):
        angle = 2 * math.pi * i / n
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        d[k] = (x, y)

    return

class Graph:
    def __init__(self, ntraces):
        self.fig, self.ax = plt.subplots()
        self.ntraces = ntraces
        self.pts = {}
        for i in range(ntraces):
            self.pts[i] = None
        fill_points_circle(self.pts, radius=1)

    def draw_loop(self, t, i):
        pts = {}
        for p in t.factors:
            try:
                x, y = p.fx.index['pos'], p.fy.index['pos']
                if not x in pts:
                    pts[x] = None
                if not y in pts:
                    pts[y] = None
            except:
                pass

        fill_points_circle(pts, radius=0.5, center=self.pts[i])

        stack = []
        for p in t.factors:
            try:
                x, y = p.fx.index['pos'], p.fy.index['pos']
                (x1, x2), (y1, y2) = pts[x], pts[y]
                if x==y:
                    patch = Circle((x1+0.3, x2), radius=0.3, fill=False, color='k')
                    self.ax.add_patch(patch)
                    patch = Circle((y1+0.3, y2), radius=0.3, fill=False, color='k')
                    self.ax.add_patch(patch)
                else:
                    patch = FancyArrowPatch(
                        pts[x], pts[y],
                        connectionstyle=f"arc3,rad={0.3}",
                        arrowstyle='-'
                    )
                    self.ax.add_patch(patch)

                if not x in stack:
                    self.ax.scatter(*pts[x])
                    self.ax.text(*pts[x], f'  {x}')
                    stack.append(x)

                if not y in stack:
                    self.ax.scatter(*pts[y])
                    self.ax.text(*pts[y], f'  {y}')
                    stack.append(y) 

            except:
                pass

    def __call__(self, title=''):
        self.ax.set_title(title)
        self.fig.tight_layout()

