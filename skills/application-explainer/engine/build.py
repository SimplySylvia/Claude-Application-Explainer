"""Builds a self-contained product & engineering guide from guide_config.py, sections/, diagrams.py, and shots.py.

    python3 build/build.py                   # full guide (+ the no-screenshots share version if screenshots exist)
    python3 build/build.py --no-screenshots  # share version only

Output goes to the guide root: <OUTPUT_NAME>.html and <OUTPUT_NAME>-no-screenshots.html.
"""
import base64, json, os, re, subprocess, sys

E = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(E)
sys.path[:0] = [E, ROOT]

import guide_config as cfg
import layout
import diagram as dg
import highlight
from diagram import esc
from icons import ICONS
import diagrams  # noqa: F401  (registers diagram builders)

NO_SHOTS = '--no-screenshots' in sys.argv
NAME = cfg.OUTPUT_NAME
OUT = os.path.join(ROOT, NAME + ('-no-screenshots' if NO_SHOTS else '') + '.html')
KEY = re.sub(r'[^a-z0-9]+', '-', NAME.lower()).strip('-')

for _k in ('COLLAPSED_SECTIONS', 'COLLAPSED_SUBSECTIONS', 'COLLAPSED_GROUP_SECTIONS', 'OPEN_TABLE_GROUPS', 'COLLAPSED_TABLE_GROUPS'):
    setattr(layout, _k, set(getattr(cfg, _k, ())))


def read(*parts):
    return open(os.path.join(*parts), encoding='utf-8').read()


warnings = []
# A <code> span that looks like a repo path or file name: has a slash (src/app, /api/x) or a file extension (Makefile excepted).
CITED_PATH = re.compile(r'<code>[^<]*(/|\.[A-Za-z]{1,6}\b|Makefile|Dockerfile)[^<]*</code>')
# A link to an outside page: topic guides cite official docs this way. Opened in a new tab, without a referrer.
EXTERNAL_LINK = re.compile(r'<a href="(https?://[^"]+)"(?![^>]*\btarget=)')

# ---------------------------------------------------------------- sections
PARTS = [(pid, str(i + 1), title, blurb, items) for i, (pid, title, blurb, items) in enumerate(cfg.PARTS)]
sections = {}
for pid, num, title, blurb, items in PARTS:
    for sid, _label in layout.flat(items):
        path = os.path.join(ROOT, 'sections', sid + '.html')
        src = read(path)
        assert f'<section id="{sid}">' in src, f'{path} must contain <section id="{sid}">'
        sections[sid] = EXTERNAL_LINK.sub(r'<a href="\1" target="_blank" rel="noopener noreferrer"', src.strip())
        # Every claim should be traceable to the repo or a cited page. Unfinished sections (TODOs) are caught by qa_check.py.
        if 'TODO' not in src and 'Sources:' not in src and not CITED_PATH.search(src) and not EXTERNAL_LINK.search(src):
            warnings.append(f'section {sid!r} cites no repo paths: add a "Sources:" line or paths in a Where/Code column')

# ---------------------------------------------------------------- screenshots (optional)
shot_data = {}
shots = None
if not NO_SHOTS and os.path.exists(os.path.join(ROOT, 'shots.py')):
    import shots
    for n, (area, title, route, note) in shots.SHOTS.items():
        p = os.path.join(ROOT, 'screenshots', n + '.jpg')
        if os.path.exists(p):
            shot_data[n] = {'src': 'data:image/jpeg;base64,' + base64.b64encode(open(p, 'rb').read()).decode(),
                            'title': title, 'route': route, 'note': note, 'area': area}
        else:
            warnings.append(f'missing screenshot {n}.jpg')
HAS_SHOTS = bool(shot_data)


def shot_cell(name):
    v = shots.FEATURE_SHOTS.get(name) if shots else None
    if isinstance(v, list) and all(x in shot_data for x in v):
        more = f'<span class="shot-more">+{len(v) - 1}</span>' if len(v) > 1 else ''
        return (f'<td><button type="button" class="shot-thumb" data-shots="{",".join(v)}" title="Open screenshot">'
                f'<img data-shot="{v[0]}" alt="" loading="lazy">{more}</button></td>')
    return f'<td class="shot-none">{v or "—"}</td>'


def add_screen_column(table):
    """Tables marked data-screens get a Screen column keyed by each row's first <b> text (FEATURE_SHOTS)."""
    table = table.replace(' data-screens', '', 1)
    if not HAS_SHOTS:
        return table
    table = table.replace('</colgroup>', '<col style="width:12%"></colgroup>', 1)
    table = re.sub(r'(<tr>\s*<th.*?)</tr>', lambda m: m.group(1) + '<th>Screen</th></tr>', table, count=1, flags=re.S)
    table = re.sub(r'colspan="(\d+)"', lambda m: f'colspan="{int(m.group(1)) + 1}"', table)
    return re.sub(r'(<tr><td><b>(.*?)</b></td>.*?)</tr>', lambda m: m.group(1) + shot_cell(m.group(2)) + '</tr>', table, flags=re.S)


def gallery_html():
    areas = [a for a in getattr(shots, 'AREAS', []) if any(d['area'] == a[0] for d in shot_data.values())]
    missing = {d['area'] for d in shot_data.values()} - {a[0] for a in areas}
    assert not missing, f'add AREAS entries in shots.py for: {missing}'
    order = [n for a in areas for n in shot_data if shot_data[n]['area'] == a[0]]
    gid = lambda area: 'gallery-' + re.sub(r'[^a-z0-9]+', '-', area.lower()).strip('-')
    g = ['\n  <h3 style="margin-top:24px">Screen gallery</h3>\n',
         f'  <p class="caption">{getattr(shots, "GALLERY_CAPTION", "")} Click any screen to open it full size, use ← → to move between screens, and click the image to toggle actual size.</p>\n',
         '  <nav class="gallery-jump" aria-label="Gallery areas">' + ''.join(
             f'<a class="c-{color}" href="#{gid(area)}"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[icon]}</svg>{esc(area)}'
             f'<b>{sum(d["area"] == area for d in shot_data.values())}</b></a>' for area, icon, color, _ in areas) + '</nav>\n']
    for area, icon, color, blurb in areas:
        names = [n for n in order if shot_data[n]['area'] == area]
        g.append(f'  <div class="gallery-group c-{color}" id="{gid(area)}">'
                 f'<div class="gallery-head"><span class="gallery-icon"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[icon]}</svg></span>'
                 f'<div class="gallery-head-text"><h4>{esc(area)}</h4><p>{esc(blurb)}</p></div>'
                 f'<span class="gallery-count">{len(names)} screen{"s" if len(names) != 1 else ""}</span></div>\n    <div class="gallery">')
        for n in names:
            d = shot_data[n]
            note = f'<span class="shot-note-line">{esc(d["note"])}</span>' if d['note'] else ''
            g.append(f'<figure class="shot-card"><button type="button" data-shots="{",".join(order)}" data-start="{n}" title="Open full size">'
                     f'<img data-shot="{n}" alt="" loading="lazy"><code class="shot-route-chip">{esc(d["route"])}</code></button>'
                     f'<figcaption><b>{esc(d["title"])}</b>{note}</figcaption></figure>')
        g.append('</div></div>\n')
    if getattr(shots, 'NOT_CAPTURED', None):
        g.append('\n  <h3 style="margin-top:24px">Not captured</h3>\n  <table>\n    <tr><th style="width:30%">Route</th><th style="width:24%">What the app showed</th><th>Why</th></tr>\n')
        for r, w, y in shots.NOT_CAPTURED:
            g.append(f'    <tr><td><code>{esc(r)}</code></td><td>{esc(w)}</td><td>{esc(y)}</td></tr>\n')
        g.append('  </table>\n')
    return ''.join(g)


for sid in sections:
    if re.search(r'<pre(?! class="code" data-lang=)', sections[sid]):
        warnings.append(f'section {sid!r} has a <pre> without class="code" data-lang="…": it won\'t be highlighted')
    sections[sid] = highlight.render_blocks(sections[sid], lambda w, sid=sid: warnings.append(f'section {sid!r}: {w}'))
    s = re.sub(r'<table[^>]*\sdata-screens[^>]*>.*?</table>', lambda m: add_screen_column(m.group(0)), sections[sid], flags=re.S)
    if '<!-- SCREEN GALLERY -->' in s:
        s = s.replace('<!-- SCREEN GALLERY -->', gallery_html() if HAS_SHOTS else '')
    sections[sid] = s

# ---------------------------------------------------------------- diagrams and icons
built = {}
for sid, s in sections.items():
    for name in re.findall(r'<div class="diagram" data-diagram="([\w-]+)"></div>', s):
        assert name in dg.REGISTRY, f'section {sid} uses diagram {name!r} but diagrams.py has no @diagram({name!r})'
        if name not in built:
            d, aria = dg.REGISTRY[name]()
            d.check()
            warnings += [f'[diagram {name}] {w}' for w in d.warn]
            built[name] = (d, aria)
    s = re.sub(r'<div class="diagram" data-diagram="([\w-]+)"></div>',
               lambda m: built[m.group(1)][0].legend() + '\n  <div class="diagram">' + built[m.group(1)][0].svg(built[m.group(1)][1]) + '</div>', s)
    s = re.sub(r'<svg viewBox="0 0 24 24" data-card-icon="(\w+)"></svg>', lambda m: f'<svg viewBox="0 0 24 24">{ICONS[m.group(1)]}</svg>', s)
    s = re.sub(r'<span class="row-icon" data-icon="(\w+)"></span>',
               lambda m: f'<span class="row-icon"><svg viewBox="0 0 24 24">{ICONS[m.group(1)]}</svg></span>', s)
    sections[sid] = s
for name in set(dg.REGISTRY) - set(built):
    warnings.append(f'diagram {name!r} is defined but not placed in any section')

# ---------------------------------------------------------------- layout: collapsibles, pages, header, sidebar
subsections = {}
for sid in sections:
    sections[sid], subsections[sid] = layout.wrap_section(sections[sid], sid)

PAGE_TABS = '<nav class="page-tabs" aria-label="Guide pages">' + ''.join(
    f'<a href="#part-{pid}" data-page="{pid}" title="Part {num} · {esc(title)}"><span class="page-tab-num">{num}</span>'
    f'<span class="page-tab-label">{esc(title)}</span></a>' for pid, num, title, _, _ in PARTS) + '</nav>'
pages = []
for i, (pid, num, title, blurb, items) in enumerate(PARTS):
    pages.append(f'\n<div class="page" id="page-{pid}" data-page="{pid}">'
                 f'\n<div class="part" id="part-{pid}"><span class="part-num">Part {num}</span>'
                 f'<span class="part-title">{esc(title)}</span><span class="part-blurb">{esc(blurb)}</span></div>\n')
    for it in items:
        if layout.is_group(it):
            pages.append(layout.topic_head(it[0], it[1], it[2], esc) + '\n')
            pages.extend(sections[sid] + '\n' for sid, _ in it[3])
        else:
            pages.append(sections[it[0]] + '\n')
    pager = []
    for j, cls, arrow in ((i - 1, 'prev', '← Previous'), (i + 1, 'next', 'Next →')):
        if 0 <= j < len(PARTS):
            q = PARTS[j]
            pager.append(f'<a class="pager-{cls}" href="#part-{q[0]}"><span class="pager-dir">{arrow}</span>'
                         f'<span class="pager-title">Part {q[1]} · {esc(q[2])}</span><span class="pager-blurb">{esc(q[3])}</span></a>')
        else:
            pager.append('<span></span>')
    pages.append('<nav class="pager" aria-label="More pages">' + ''.join(pager) + '</nav>\n</div>\n')

# ---------------------------------------------------------------- styles, fonts, scripts
tokens = read(ROOT, cfg.TOKENS_CSS) if getattr(cfg, 'TOKENS_CSS', None) else read(E, 'tokens.css')
fonts = ''
for family, weight, path in getattr(cfg, 'FONTS', []):
    data = base64.b64encode(open(os.path.join(ROOT, path), 'rb').read()).decode()
    fonts += f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2');}}"
brand = f':root {{ --guide-brand: {cfg.BRAND_COLOR}; }}' if getattr(cfg, 'BRAND_COLOR', None) else ''
css = fonts + '\n' + tokens + '\n' + read(E, 'styles.css') + '\n' + brand + '\n' + layout.CSS

THEME_JS = '''<script>
(function () {
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem('__GUIDE_KEY__-theme'); } catch (e) { /* storage unavailable */ }
  root.setAttribute('data-theme', stored || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('theme-toggle');
    var label = function () { btn.textContent = root.getAttribute('data-theme') === 'dark' ? '☀ Light' : '☾ Dark'; };
    label();
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('__GUIDE_KEY__-theme', next); } catch (e) { /* storage unavailable */ }
      label();
    });
  });
})();
</script>'''
DEFS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path class="arrowhead" d="M0,1 L10,5 L0,9 z"/></marker></defs></svg>')

viewer = read(E, 'diagram-viewer.js').replace('__ICONS__', json.dumps({k: ICONS[k] for k in ('expand', 'zoomIn', 'zoomOut', 'fit', 'close')}))
tail = '<script>\n' + read(E, 'layout.js') + '</script>\n<script>\n' + viewer + '</script>\n'
if HAS_SHOTS:
    payload = {k: {kk: v[kk] for kk in ('src', 'title', 'route', 'note')} for k, v in shot_data.items()}
    tail += '<script type="application/json" id="shots-data">' + json.dumps(payload) + '</script>\n<script>\n' + read(E, 'shots-viewer.js') + '</script>\n'
tail += '<script>\n' + read(E, 'search.js') + '</script>\n<script>\n' + read(E, 'glossary.js') + '</script>\n'
if 'class="code-copy"' in ''.join(pages):
    tail += '<script>\n' + read(E, 'code.js') + '</script>\n'

footer = getattr(cfg, 'FOOTER', '')
if NO_SHOTS:
    footer = 'This share version leaves out the screenshots; the full guide includes them. ' + footer

doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(cfg.TITLE)}</title>
<style>
{css}
</style>
{THEME_JS}
</head>
<body>
{DEFS}
{layout.header(getattr(cfg, 'LOGO_SVG', ''), PAGE_TABS, esc(cfg.TITLE), esc(cfg.SHORT_TITLE))}
{layout.sidebar(PARTS, subsections, esc)}
<main>
{''.join(pages)}
<footer><p class="caption">{footer}</p></footer>
</main>
{tail}</body>
</html>
'''
doc = doc.replace('__GUIDE_KEY__', KEY)
open(OUT, 'w', encoding='utf-8').write(doc)

for w in warnings:
    print('WARNING', w)
print('OK' if not warnings else f'{len(warnings)} WARNINGS', OUT, f'{os.path.getsize(OUT) / 1e6:.2f} MB')

if not NO_SHOTS and HAS_SHOTS:
    subprocess.run([sys.executable, os.path.abspath(__file__), '--no-screenshots'], check=True)
