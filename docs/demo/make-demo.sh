#!/usr/bin/env bash
# Rebuilds the live demo (docs/demo/) and the README screenshots (docs/images/) from the demo sources:
#
#   source/             the Shopfront Product & Engineering Guide, with an Express deep dive on its Topics page
#   source-postgresql/  a separate PostgreSQL topic guide
#   source-hub/         the hub that links the two (docs/demo/index.html redirects to it)
#
#   docs/demo/make-demo.sh                   # build, QA, and recapture screenshots
#   docs/demo/make-demo.sh --no-screenshots  # build and QA only
#
# Uses the current engine: scaffolds the guides and hub for the eval fixture app, overlays the committed sources,
# builds them, and runs qa_check.py on both guides. Needs Python 3.9+ and Google Chrome or Chromium.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
DEMO="$ROOT/docs/demo"
SKILL="$ROOT/skills/application-explainer"
# Pin the hub's dates so the committed demo only changes when its content does.
export SOURCE_DATE_EPOCH=1791936000
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"
bash "$ROOT/evals/_fixture/make-app.sh" >/dev/null
python3 "$SKILL/scripts/new_guide.py" --repo app --app Shopfront --no-hub >/dev/null
python3 "$SKILL/scripts/new_guide.py" --repo app --app Shopfront --topic PostgreSQL --no-hub >/dev/null
python3 "$SKILL/scripts/new_hub.py" --repo app --app Shopfront >/dev/null
cp -R "$DEMO/source/." shopfront-guide/
rm -rf shopfront-postgresql-guide/sections
cp -R "$DEMO/source-postgresql/." shopfront-postgresql-guide/
cp "$DEMO/source-hub/hub_config.py" shopfront-guides/
python3 shopfront-guide/build/build.py --no-hub
python3 shopfront-postgresql-guide/build/build.py --no-hub
python3 shopfront-guides/build/build.py            # once both guides exist (a guide's own build would refresh it too)
python3 "$SKILL/scripts/qa_check.py" shopfront-guide/shopfront-guide.html
python3 "$SKILL/scripts/qa_check.py" shopfront-postgresql-guide/shopfront-postgresql-guide.html

for d in shopfront-guide shopfront-postgresql-guide shopfront-guides; do rm -rf "${DEMO:?}/$d" && mkdir -p "$DEMO/$d"; done
cp shopfront-guide/shopfront-guide.html "$DEMO/shopfront-guide/"
cp shopfront-postgresql-guide/shopfront-postgresql-guide.html "$DEMO/shopfront-postgresql-guide/"
cp shopfront-guides/index.html shopfront-guides/nav.js "$DEMO/shopfront-guides/"
cat > "$DEMO/index.html" <<'HTML'
<!DOCTYPE html>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=shopfront-guides/">
<link rel="canonical" href="shopfront-guides/">
<title>Shopfront demo guides</title>
<p>Redirecting to the <a href="shopfront-guides/">Shopfront demo guides</a>…</p>
HTML
echo "Wrote docs/demo/"
if [ "${1:-}" != "--no-screenshots" ]; then
  python3 "$DEMO/capture.py" "$DEMO" "$ROOT/docs/images"
fi
