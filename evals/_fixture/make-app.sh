#!/usr/bin/env bash
# Creates ./app: a small, fictional "Shopfront" web app (Express API + React client) committed to git.
# Shared by the eval cases; each case's fixture.sh calls this.
set -euo pipefail
mkdir -p app && cd app
mkdir -p server/routes client/src/pages .github/workflows test

cat > README.md <<'MD'
# Shopfront

Shopfront is the storefront for Acme's online shop. Shoppers browse products and track orders;
staff use the admin screens to manage the catalog.

## Run locally

    npm install
    npm run dev        # API on :4000, client on :5173

## Test

    npm test
MD

cat > package.json <<'JSON'
{
  "name": "shopfront",
  "private": true,
  "scripts": {
    "dev": "concurrently \"node server/index.js\" \"vite client\"",
    "build": "vite build client",
    "test": "jest",
    "lint": "eslint ."
  },
  "dependencies": { "express": "^4.19.2", "pg": "^8.11.0", "react": "^18.3.1", "react-router-dom": "^6.23.0" },
  "devDependencies": { "concurrently": "^8.2.0", "eslint": "^9.0.0", "jest": "^29.7.0", "supertest": "^7.0.0", "vite": "^5.2.0" }
}
JSON

cat > server/index.js <<'JS'
const express = require('express');
const products = require('./routes/products');
const orders = require('./routes/orders');
const { requireStaff } = require('./auth');

const app = express();
app.use(express.json());
app.use('/api/products', products);
app.use('/api/orders', orders);
app.use('/api/admin', requireStaff, products.admin);

if (require.main === module) app.listen(process.env.PORT || 4000);
module.exports = app;
JS

cat > server/auth.js <<'JS'
// Staff are identified by a signed session cookie set by the company SSO proxy.
exports.requireStaff = (req, res, next) =>
  req.headers['x-staff-role'] ? next() : res.status(403).json({ error: 'staff only' });
JS

cat > server/db.js <<'JS'
const { Pool } = require('pg');
module.exports = new Pool({ connectionString: process.env.DATABASE_URL });
JS

cat > server/routes/products.js <<'JS'
const router = require('express').Router();
const db = require('../db');
router.get('/', async (req, res) => res.json((await db.query('select * from products')).rows));
router.get('/:id', async (req, res) => res.json((await db.query('select * from products where id=$1', [req.params.id])).rows[0]));
router.admin = require('express').Router();
router.admin.post('/products', async (req, res) => res.status(201).json(req.body));
module.exports = router;
JS

cat > server/routes/orders.js <<'JS'
const router = require('express').Router();
const db = require('../db');
// createOrder: validates the cart, inserts an order row, and returns its id.
async function createOrder(req, res) {
  if (!Array.isArray(req.body.items) || !req.body.items.length) return res.status(400).json({ error: 'empty cart' });
  const { rows } = await db.query('insert into orders(items) values ($1) returning id', [JSON.stringify(req.body.items)]);
  res.status(201).json({ id: rows[0].id });
}
router.post('/', createOrder);
router.get('/:id', async (req, res) => res.json((await db.query('select * from orders where id=$1', [req.params.id])).rows[0]));
module.exports = router;
JS

cat > client/src/routes.jsx <<'JS'
import { createBrowserRouter } from 'react-router-dom';
import Home from './pages/Home';
import Products from './pages/Products';
import Order from './pages/Order';
import Admin from './pages/Admin';
import { flags } from './flags';

export const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/products', element: <Products /> },
  { path: '/orders/:id', element: <Order /> },
  // The admin catalog editor is behind the newAdmin feature flag.
  ...(flags.newAdmin ? [{ path: '/admin', element: <Admin /> }] : []),
]);
JS

cat > client/src/flags.js <<'JS'
export const flags = { newAdmin: import.meta.env.VITE_FLAG_NEW_ADMIN === 'true' };
JS

for p in Home Products Order Admin; do
  echo "export default function $p() { return <main><h1>$p</h1></main>; }" > "client/src/pages/$p.jsx"
done

cat > test/orders.test.js <<'JS'
const request = require('supertest');
const app = require('../server');
test('rejects an empty cart', async () => {
  await request(app).post('/api/orders').send({ items: [] }).expect(400);
});
JS

cat > Dockerfile <<'DOCKER'
FROM node:20-slim
WORKDIR /srv
COPY . .
RUN npm ci && npm run build
CMD ["node", "server/index.js"]
DOCKER

cat > .github/workflows/ci.yml <<'YML'
name: ci
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm test
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "docker build + push to the staging registry, then promote to production by tag"
YML

git init -q
git -c user.name=eval -c user.email=eval@example.com add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "Shopfront fixture"
