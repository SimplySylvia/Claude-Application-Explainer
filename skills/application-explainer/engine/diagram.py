"""Diagram builder: zones, nodes, and orthogonal edges rendered as SVG, with geometry checks.

Use from diagrams.py:

    @diagram('arch')
    def arch():
        d = Diagram('arch', 1200, 600)
        d.zone(16, 20, 400, 500, 'CLIENTS')
        a = d.node('web', 30, 80, 180, 'client', 'monitor', 'Web app', ['React', 'SPA'])
        ...
        d.edge([(210, 105), (260, 105)], 'sync', label='HTTPS')
        return d, 'System architecture'   # (diagram, aria label)

Run the build and fix every warning it prints (overlaps, labels crossing nodes, overflow).
"""
import html
from icons import ICONS

REGISTRY = {}

def diagram(name):
    def wrap(fn):
        REGISTRY[name] = fn
        return fn
    return wrap

def esc(s):
    return html.escape(s, quote=False)

def tw(s, size, medium=False):
    return len(s) * size * (0.57 if medium else 0.535)

# Node categories → color families (used for node colors and the auto legend)
CATS = {
    'client': ('blue', 'Client / UI', 'monitor'),
    'edge': ('purple', 'Edge & messaging', 'hub'),
    'run': ('teal', 'Compute & app code', 'server'),
    'data': ('orange', 'Data store', 'db'),
    'ext': ('pink', 'External / third-party', 'globe'),
    'ci': ('gray', 'Tooling & CI', 'terminal'),
}

class Diagram:
    def __init__(self, name, w, h):
        self.name, self.w, self.h = name, w, h
        self.layers = {'zone': [], 'edge': [], 'node': [], 'label': []}
        self.nodes, self.zones, self.labels, self.edges = {}, [], [], []
        self.cats, self.kinds = set(), set()
        self.warn = []

    def zone(self, x, y, w, h, label, right=False):
        self.layers['zone'].append(
            f'<rect class="zone" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>')
        lw = tw(label, 10.5, True) + label.count(' ') * 0 + len(label) * 0.7 + 16
        px = x + w - 12 - lw if right else x + 12
        self.layers['label'].append(
            f'<rect class="zone-pill" x="{px:.0f}" y="{y-9}" width="{lw:.0f}" height="18" rx="9"/>'
            f'<text class="zone-label" x="{px+8:.0f}" y="{y+4}">{esc(label)}</text>')
        self.zones.append((px, y - 9, lw, 18, label))

    def node(self, nid, x, y, w, cat, icon, title, lines=(), num=None, h=None):
        n = len(lines)
        h = h or (50 if n == 0 else 46 + 16 * n)
        color = CATS[cat][0]
        self.cats.add(cat)
        out = [f'<g class="node c-{color}">',
               f'<rect class="card" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/>',
               f'<rect class="badge" x="{x+12}" y="{y+12}" width="26" height="26" rx="6"/>',
               f'<svg class="glyph" x="{x+15}" y="{y+15}" width="20" height="20" viewBox="0 0 24 24">{ICONS[icon]}</svg>',
               f'<text class="title" x="{x+48}" y="{y+30}">{esc(title)}</text>']
        if tw(title, 13.5, True) > w - 48 - (30 if num else 10):
            self.warn.append(f'title overflow: {title!r} {tw(title, 13.5, True):.0f}>{w-48-(30 if num else 10)}')
        for i, line in enumerate(lines):
            out.append(f'<text class="sub" x="{x+14}" y="{y+54+15*i}">{esc(line)}</text>')
            if tw(line, 11.5) > w - 26:
                self.warn.append(f'line overflow in {nid}: {line!r} {tw(line, 11.5):.0f}>{w-26}')
        if num is not None:
            out.append(f'<circle class="num" cx="{x+w-18}" cy="{y+18}" r="10"/>'
                       f'<text class="num-t" x="{x+w-18}" y="{y+22}" text-anchor="middle">{num}</text>')
        out.append('</g>')
        self.layers['node'].append(''.join(out))
        self.nodes[nid] = (x, y, w, h)
        return (x, y, w, h)

    def edge(self, pts, kind='sync', label=None, at=None, arrow=True, dot_end=False):
        self.kinds.add(kind)
        d = 'M' + ' L'.join(f'{px},{py}' for px, py in pts)
        mk = ' marker-end="url(#arrow)"' if arrow else ''
        self.layers['edge'].append(f'<path class="edge {kind}" d="{d}"{mk}/>')
        if dot_end:
            self.layers['edge'].append(f'<circle class="joint" cx="{pts[-1][0]}" cy="{pts[-1][1]}" r="3.5"/>')
        self.edges.append(pts)
        if label:
            if at is None:  # midpoint of longest segment
                segs = list(zip(pts, pts[1:]))
                a, b = max(segs, key=lambda s: abs(s[0][0]-s[1][0]) + abs(s[0][1]-s[1][1]))
                at = ((a[0]+b[0]) / 2, (a[1]+b[1]) / 2)
            lw = tw(label, 11) + 18
            lx, ly = at[0] - lw / 2, at[1] - 10
            self.layers['label'].append(
                f'<rect class="edge-pill" x="{lx:.0f}" y="{ly:.0f}" width="{lw:.0f}" height="20" rx="10"/>'
                f'<text class="edge-label" x="{at[0]:.0f}" y="{at[1]+4:.0f}" text-anchor="middle">{esc(label)}</text>')
            self.labels.append((lx, ly, lw, 20, label))

    # ---- geometry checks
    def check(self):
        rects = list(self.nodes.items())
        for i, (a, ra) in enumerate(rects):
            for b, rb in rects[i+1:]:
                if overlap(ra, rb, 4):
                    self.warn.append(f'nodes overlap/too close: {a} {b}')
        for pts in self.edges:
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                if x1 != x2 and y1 != y2:
                    self.warn.append(f'diagonal segment {pts}')
                steps = int(max(abs(x2-x1), abs(y2-y1)) / 2) or 1
                for k in range(steps + 1):
                    px, py = x1 + (x2-x1)*k/steps, y1 + (y2-y1)*k/steps
                    if (px, py) in (pts[0], pts[-1]):
                        continue
                    for zx, zy, zw, zh, zl in self.zones:
                        if zx < px < zx + zw and zy < py < zy + zh:
                            self.warn.append(f'edge {pts[0]}→{pts[-1]} crosses zone label {zl!r}')
                    for nid, (nx, ny, nw, nh) in rects:
                        if nx + 2 < px < nx + nw - 2 and ny + 2 < py < ny + nh - 2:
                            self.warn.append(f'edge {pts[0]}→{pts[-1]} passes through {nid} at {px:.0f},{py:.0f}')
                            break
                    else:
                        continue
                    break
        for lx, ly, lw, lh, text in self.labels + [z[:4] + (z[4],) for z in self.zones]:
            for nid, r in rects:
                if overlap((lx, ly, lw, lh), r, 0):
                    self.warn.append(f'label {text!r} overlaps node {nid}')
        for i, a in enumerate(self.labels):
            for b in self.labels[i+1:]:
                if overlap(a[:4], b[:4], 2):
                    self.warn.append(f'labels overlap {a[4]!r} {b[4]!r}')
        for nid, (x, y, w, h) in rects:
            if x < 0 or y < 0 or x + w > self.w or y + h > self.h:
                self.warn.append(f'node {nid} outside canvas')

    def svg(self, aria):
        body = ''.join(self.layers['zone'] + self.layers['edge'] + self.layers['node'] + self.layers['label'])
        return (f'<svg class="dg" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(aria)}">'
                f'{body}</svg>')

    def legend(self):
        items = []
        for cat in ['client', 'edge', 'run', 'data', 'ext', 'ci']:
            if cat in self.cats:
                color, label, icon = CATS[cat]
                items.append(f'<span class="lg-item"><span class="lg-badge c-{color}">'
                             f'<svg viewBox="0 0 24 24">{ICONS[icon]}</svg></span>{esc(label)}</span>')
        items.append('<span class="lg-sep"></span>')
        if 'sync' in self.kinds:
            items.append('<span class="lg-item lg-line"><svg width="38" height="10"><path class="edge sync" '
                         'd="M2,5 L30,5" marker-end="url(#arrow)"/></svg>Synchronous call</span>')
        if 'async' in self.kinds:
            items.append('<span class="lg-item lg-line"><svg width="38" height="10"><path class="edge async" '
                         'd="M2,5 L30,5" marker-end="url(#arrow)"/></svg>Async / event / queued</span>')
        return f'<div class="legend">{"".join(items)}</div>'


def overlap(a, b, pad):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw + pad and bx < ax + aw + pad and ay < by + bh + pad and by < ay + ah + pad


def mid(r, side, off=0):
    x, y, w, h = r
    return {'l': (x, y + h/2 + off), 'r': (x + w, y + h/2 + off),
            't': (x + w/2 + off, y), 'b': (x + w/2 + off, y + h)}[side]

