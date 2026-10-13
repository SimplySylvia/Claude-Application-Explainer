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
