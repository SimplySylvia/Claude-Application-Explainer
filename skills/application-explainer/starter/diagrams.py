"""Diagrams placed with <div class="diagram" data-diagram="NAME"></div> in a section.

Coordinates are in SVG units (canvas width ~1200). Node categories: client, edge, run, data, ext, ci.
Icons: keys of ICON_FILES in build/icons.py. Edges must be horizontal/vertical segments.
The build prints geometry warnings (overlaps, labels on nodes, overflowing text): fix them all.
"""
from diagram import Diagram, diagram, mid


@diagram('arch')
def arch():
    d = Diagram('arch', 1200, 420)
    d.zone(16, 20, 260, 380, 'USERS & CLIENTS')
    d.zone(296, 20, 560, 380, 'PLATFORM')
    d.zone(876, 20, 308, 380, 'THIRD-PARTY SYSTEMS')
    web = d.node('web', 32, 80, 228, 'client', 'monitor', 'Web app', ['TODO: framework', 'TODO: who uses it'])
    api = d.node('api', 316, 80, 240, 'run', 'server', 'API service', ['TODO: runtime · framework', 'TODO: what it serves'])
    db = d.node('db', 316, 260, 240, 'data', 'db', 'Database', ['TODO: engine', 'TODO: hosting'])
    q = d.node('q', 596, 80, 240, 'edge', 'radio', 'Queue / events', ['TODO: broker', 'TODO: topics'])
    ext = d.node('ext', 892, 80, 276, 'ext', 'globe', 'External APIs', ['TODO: vendors', 'TODO: what for'])
    d.edge([mid(web, 'r'), mid(api, 'l')], 'sync', label='HTTPS', at=(288, 120))
    d.edge([mid(api, 'b'), mid(db, 't')], 'sync', label='SQL', at=(436, 210))
    d.edge([mid(api, 'r'), mid(q, 'l')], 'async')
    d.edge([mid(q, 'r'), mid(ext, 'l')], 'async')
    return d, 'System architecture'
