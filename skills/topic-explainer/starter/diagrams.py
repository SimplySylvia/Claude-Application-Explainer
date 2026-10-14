"""Diagrams placed with <div class="diagram" data-diagram="NAME"></div> in a section.

Coordinates are in SVG units (canvas width ~1200). Node categories: client, edge, run, data, ext, ci.
Icons: keys of ICON_FILES in build/icons.py. Edges must be horizontal/vertical segments.
The build prints geometry warnings (overlaps, labels on nodes, overflowing text): fix them all.
"""
from diagram import Diagram, diagram, mid


@diagram('__T__flow')
def __TFN__flow():
    # One real flow through __TOPIC__ in __APP__, numbered to match the steps in the guided walkthrough.
    d = Diagram('__T__flow', 1200, 300)
    d.zone(16, 20, 280, 260, 'CALLER')
    d.zone(316, 20, 560, 260, 'APP CODE')
    d.zone(896, 20, 288, 260, 'DOWNSTREAM')
    a = d.node('a', 32, 110, 248, 'client', 'monitor', 'Entry point', ['TODO: file or component'], num=1)
    b = d.node('b', 336, 110, 240, 'run', 'server', 'TODO: layer', ['TODO: file'], num=2)
    c = d.node('c', 616, 110, 240, 'run', 'code', 'TODO: handler', ['TODO: file'], num=3)
    e = d.node('e', 912, 110, 256, 'data', 'db', 'TODO: data source', ['TODO: what it reads'], num=4)
    d.edge([mid(a, 'r'), mid(b, 'l')], 'sync')
    d.edge([mid(b, 'r'), mid(c, 'l')], 'sync')
    d.edge([mid(c, 'r'), mid(e, 'l')], 'sync')
    return d, '__TOPIC__ request flow'
