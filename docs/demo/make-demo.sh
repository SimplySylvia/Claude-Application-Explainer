#!/usr/bin/env bash
# Rebuilds the live demo (docs/demo/index.html) and the README screenshots (docs/images/) from docs/demo/source/.
#
#   docs/demo/make-demo.sh                   # build, QA, and recapture screenshots
#   docs/demo/make-demo.sh --no-screenshots  # build and QA only
#
# Uses the current engine: scaffolds a fresh guide for the eval fixture app, overlays the committed sections,
# diagrams, and config, builds it, and runs qa_check.py. Needs Python 3.9+ and Google Chrome or Chromium.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SKILL="$ROOT/skills/application-explainer"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

cd "$WORK"
bash "$ROOT/evals/_fixture/make-app.sh" >/dev/null
python3 "$SKILL/scripts/new_guide.py" --repo app --app Shopfront >/dev/null
cp -R "$ROOT/docs/demo/source/." shopfront-guide/
python3 shopfront-guide/build/build.py
python3 "$SKILL/scripts/qa_check.py" shopfront-guide/shopfront-guide.html
cp shopfront-guide/shopfront-guide.html "$ROOT/docs/demo/index.html"
echo "Wrote docs/demo/index.html"

if [ "${1:-}" != "--no-screenshots" ]; then
  python3 "$ROOT/docs/demo/capture.py" "$ROOT/docs/demo/index.html" "$ROOT/docs/images"
fi
