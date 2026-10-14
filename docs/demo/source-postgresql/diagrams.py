"""Diagrams placed with <div class="diagram" data-diagram="NAME"></div> in a section."""
from diagram import Diagram, diagram, mid


@diagram('postgresql-flow')
def t_postgresql_flow():
    # Placing an order, from the database's side: numbered to match the PostgreSQL walkthrough.
    d = Diagram('postgresql-flow', 1200, 330)
    d.zone(16, 20, 640, 290, 'API PROCESS (server/)')
    d.zone(676, 20, 508, 290, 'POSTGRESQL')
    h = d.node('h', 32, 90, 190, 'run', 'code', 'createOrder', ['orders.js:6'], num=1)
    p = d.node('p', 252, 90, 180, 'edge', 'layers', 'Pool', ['server/db.js'], num=2)
    c = d.node('c', 462, 90, 176, 'edge', 'link', 'Client', ['one connection'], num=3)
    q = d.node('q', 696, 90, 220, 'data', 'db', 'INSERT … RETURNING', ['orders table'], num=4)
    r = d.node('r', 252, 220, 386, 'run', 'table', 'Result', ['rows[0].id → 201 { id }'], num=5)
    d.edge([mid(h, 'r'), mid(p, 'l')], 'sync')
    d.edge([mid(p, 'r'), mid(c, 'l')], 'sync')
    d.edge([mid(c, 'r'), mid(q, 'l')], 'sync')
    d.edge([mid(q, 'b'), (806, mid(r, 'r')[1]), mid(r, 'r')], 'async', label='rows', at=(806, 200))
    return d, 'How a query travels from a handler to PostgreSQL and back'
