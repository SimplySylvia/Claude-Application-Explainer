"""Diagrams placed with <div class="diagram" data-diagram="NAME"></div> in a section."""
from diagram import Diagram, diagram, mid


@diagram('arch')
def arch():
    d = Diagram('arch', 1200, 380)
    d.zone(16, 20, 260, 340, 'USERS & CLIENTS')
    d.zone(296, 20, 560, 340, 'PLATFORM')
    d.zone(876, 20, 308, 340, 'DELIVERY')
    web = d.node('web', 32, 80, 228, 'client', 'monitor', 'Web client', ['React 18 · Vite 5', 'client/src'])
    sso = d.node('sso', 32, 240, 228, 'edge', 'shield', 'SSO proxy', ['identifies staff', 'outside this repo'])
    api = d.node('api', 336, 80, 240, 'run', 'server', 'API server', ['Node 20 · Express 4', 'server/index.js'])
    db = d.node('db', 616, 80, 220, 'data', 'db', 'PostgreSQL', ['products · orders', 'DATABASE_URL'])
    ci = d.node('ci', 892, 80, 276, 'ci', 'build', 'GitHub Actions', ['lint · jest', 'deploy on main'])
    img = d.node('img', 892, 240, 276, 'ci', 'package', 'Docker image', ['node:20-slim', 'Dockerfile'])
    d.edge([mid(web, 'r'), mid(api, 'l')], 'sync', label='/api/*')
    d.edge([mid(api, 'r'), mid(db, 'l')], 'sync', label='SQL')
    d.edge([mid(sso, 'r'), (456, mid(sso, 'r')[1]), mid(api, 'b')], 'sync', label='/api/admin')
    d.edge([mid(ci, 'b'), mid(img, 't')], 'async', label='build')
    return d, 'System architecture'


# ---- Express deep dive (sections/express-*.html)
@diagram('express-flow')
def express_flow():
    # POST /api/orders, numbered to match the steps in the guided walkthrough.
    d = Diagram('express-flow', 1200, 420)
    d.zone(16, 20, 220, 380, 'CALLER')
    d.zone(256, 20, 700, 380, 'EXPRESS APP (server/)')
    d.zone(976, 20, 208, 380, 'DATA')
    c = d.node('c', 32, 80, 188, 'client', 'monitor', 'Client', ['fetch / curl', 'POST /api/orders'], num=1)
    j = d.node('j', 276, 80, 200, 'edge', 'filter', 'express.json()', ['parses req.body', 'index.js:7'], num=2)
    r = d.node('r', 516, 80, 200, 'run', 'tree', 'Orders router', ['/api/orders', 'index.js:9'], num=3)
    h = d.node('h', 756, 80, 180, 'run', 'code', 'createOrder', ['validates, inserts', 'orders.js:4-8'], num=4)
    db = d.node('db', 992, 80, 176, 'data', 'db', 'Postgres', ['db.query()', 'server/db.js'], num=5)
    s = d.node('s', 516, 270, 200, 'edge', 'shield', 'requireStaff', ['/api/admin only', 'server/auth.js'])
    a = d.node('a', 756, 270, 180, 'run', 'code', 'Admin router', ['POST /products', 'products.js:5-6'])
    d.edge([mid(c, 'r'), mid(j, 'l')], 'sync')
    d.edge([mid(j, 'r'), mid(r, 'l')], 'sync')
    d.edge([mid(r, 'r'), mid(h, 'l')], 'sync')
    d.edge([mid(h, 'r'), mid(db, 'l')], 'sync', label='SQL')
    d.edge([(376, 158), (376, 309), mid(s, 'l')], 'sync', label='/api/admin', at=(376, 236))
    d.edge([mid(s, 'r'), mid(a, 'l')], 'sync')
    return d, 'How Shopfront handles an API request'


# ---- PostgreSQL deep dive
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
