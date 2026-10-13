#!/usr/bin/env bash
# The fixture app plus an existing application-explainer guide for it, in the default sibling folder.
set -euo pipefail
bash "$(dirname "$0")/../_fixture/make-app.sh"
mkdir -p shopfront-guide/sections
cat > shopfront-guide/guide_config.py <<PY
TITLE = 'Shopfront — Product & Engineering Guide'
OUTPUT_NAME = 'shopfront-guide'
SOURCE_REPO = '$(pwd)/app'
SOURCE_COMMIT = '$(git -C app rev-parse HEAD)'
PARTS = [
    ('product', 'Product', 'What the app is.', [
        ('overview', 'What is Shopfront?'),
    ]),
]
PY
