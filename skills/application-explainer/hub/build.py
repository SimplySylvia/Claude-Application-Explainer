"""Builds a guide hub: one page that links every guide built for the same app repo, with its pages, sections and
topic deep dives, plus nav.js, which those guides load for their Guides menu, reading position and cross-guide search.

    python3 build/build.py   # from the hub folder; writes index.html and nav.js

Guides in sibling folders whose guide_config.py has the same SOURCE_REPO are found on their own. A guide's own build
re-runs this when its HUB_URL points here, so the hub stays current. Links are relative: keep the folders side by side.
"""
import ast, base64, datetime, html, importlib.util, json, os, re, sys

E = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(E)
PARENT = os.path.dirname(ROOT)
sys.path.insert(0, ROOT)
import hub_config as cfg  # noqa: E402

QUICK_TOPICS = 8   # topic buttons under the search box; the rest are one click away in the table
# Marker colors for the main guide's page tiles; a guide's own marker is its BRAND_COLOR.
PALETTE = ['#0064fa', '#905d9a', '#49786d', '#ad5900', '#a9527c', '#437e00']
esc = lambda s: html.escape(str(s), quote=True)
warnings = []
APP = cfg.APP
STORE = getattr(cfg, 'STORAGE_KEY', None) or re.sub(r'[^a-z0-9]+', '-', APP.lower()).strip('-') + '-guides'


def real(path, base):
    return os.path.realpath(os.path.join(base, os.path.expanduser(path)))


HUB_REPO = real(cfg.SOURCE_REPO, ROOT)


def load_config(folder):
    spec = importlib.util.spec_from_file_location(f'cfg_{re.sub(r"[^A-Za-z0-9]", "_", folder)}',
                                                  os.path.join(PARENT, folder, 'guide_config.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(PARENT, folder))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return mod


def parts_literal(path):
    """PARTS from a builder script that keeps it as a literal: (id, [num,] title, blurb, items)."""
    tree = ast.parse(open(path, encoding='utf-8').read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'PARTS' for t in node.targets):
            return [(p[0], p[-3], p[-2], p[-1]) for p in ast.literal_eval(node.value)]
    sys.exit(f'{path} has no PARTS literal')


# SOURCE_DATE_EPOCH (the reproducible-builds convention) pins every date, so a committed hub doesn't change by rebuilding.
EPOCH = os.environ.get('SOURCE_DATE_EPOCH')
TODAY = datetime.datetime.fromtimestamp(int(EPOCH), datetime.timezone.utc).date() if EPOCH else datetime.date.today()


def built_on(path):
    if not os.path.exists(path):
        return None
    return TODAY.isoformat() if EPOCH else datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def kind_of(g):
    k = getattr(g, 'GUIDE_KIND', None)
    if k in ('app', 'topic'):
        return k
    return 'topic' if 'Topic Guide' in getattr(g, 'TITLE', '') else 'app'


# ---------------------------------------------------------------- collect guides
guides = []
blurbs = getattr(cfg, 'BLURBS', {})
for folder in sorted(os.listdir(PARENT)):
    path = os.path.join(PARENT, folder, 'guide_config.py')
    if folder == os.path.basename(ROOT) or not os.path.isfile(path):
        continue
    g = load_config(folder)
    if real(getattr(g, 'SOURCE_REPO', '') or '.', os.path.join(PARENT, folder)) != HUB_REPO:
        continue
    out = os.path.join(PARENT, folder, g.OUTPUT_NAME + '.html')
    if not os.path.exists(out):
        warnings.append(f'{folder}: {g.OUTPUT_NAME}.html is not built yet; run python3 {folder}/build/build.py')
    hub_url = getattr(g, 'HUB_URL', None)
    if not hub_url or real(os.path.dirname(hub_url), os.path.join(PARENT, folder)) != os.path.realpath(ROOT):
        warnings.append(f'{folder} is listed here but not connected (its header has no Guides menu); run new_hub.py --connect {folder}')
    guides.append(dict(kind=kind_of(g), folder=folder, href=f'../{folder}/{g.OUTPUT_NAME}.html', title=g.SHORT_TITLE,
                       blurb=blurbs.get(folder) or g.PARTS[0][2], parts=g.PARTS, topics=getattr(g, 'TOPICS', {}) or {},
                       color=getattr(g, 'BRAND_COLOR', None) or cfg.BRAND_COLOR,
                       commit=(getattr(g, 'SOURCE_COMMIT', '') or '')[:10], path=out, built=built_on(out)))

# Guides built some other way (no guide_config.py): listed by hand, with PARTS read from their builder script.
for x in getattr(cfg, 'OTHER_GUIDES', []):
    out = os.path.join(PARENT, x['folder'], x['html'])
    guides.append(dict(kind=x.get('kind', 'app'), folder=x['folder'], href=f'../{x["folder"]}/{x["html"]}', title=x['title'],
                       blurb=x.get('blurb', ''), parts=parts_literal(os.path.join(PARENT, x['folder'], x['parts_from'])),
                       topics={}, color=x.get('color', cfg.BRAND_COLOR), commit='', path=out, built=built_on(out)))
guides.sort(key=lambda g: (g['kind'] != 'app', g['title'].lower()))
if not guides:
    warnings.append(f'no guides found next to this hub for {HUB_REPO}')

# Topic index: every technology a guide covers, as a whole guide or as a deep dive on its Topics page.
topic_index = []
for gd in guides:
    groups = {it[0] for _pid, _t, _b, items in gd['parts'] for it in items if len(it) == 4}
    for slug, meta in gd['topics'].items():
        if slug in groups:
            topic_index.append((meta['name'], f'{gd["href"]}#topic-{slug}', f'Deep dive in {gd["title"]}', gd['folder']))
        else:
            topic_index.append((meta['name'], gd['href'], gd['title'], gd['folder']))
topic_index.sort(key=lambda t: t[0].lower())


# ---------------------------------------------------------------- render
def plural(n, word):
    return f'{n} {word}' + ('' if n == 1 else 's')


def hue_style(color):
    return (f'style="--h: {color}; --h-bg: color-mix(in srgb, {color} 16%, var(--color-bg-light)); '
            f'--h-fg: color-mix(in srgb, {color} 75%, var(--color-text))"')


def flat_sections(items):
    """[(section id, label, topic group title or None)] in reading order."""
    out = []
    for it in items:
        if len(it) == 4:
            out.extend((sid, label, it[1]) for sid, label in it[3])
        else:
            out.append((it[0], it[1], None))
    return out


def count(gd):
    return sum(len(flat_sections(items)) for *_, items in gd['parts'])


SUBSEC = re.compile(r'<div class="subsec" id="([^"]+)"><h3 class="subsec-title"><button[^>]*>(.*?)</button>', re.S)


def headings(path):
    """(id, text) for every subsection heading in a built guide."""
    if not os.path.exists(path):
        return []
    return [(hid, html.unescape(re.sub(r'<[^>]+>', '', text)).strip())
            for hid, text in SUBSEC.findall(open(path, encoding='utf-8').read())]


search_index = []
for gd in guides:
    entry = lambda t, k, c, h: search_index.append(dict(t=t, k=k, g=gd['title'], u=gd['folder'], c=c, h=h))
    entry(gd['title'], 'Guide', gd['blurb'], gd['href'])
    where = {}
    for pid, ptitle, _b, items in gd['parts']:
        entry(ptitle, 'Page', '', f'{gd["href"]}#part-{pid}')
        for it in items:
            if len(it) == 4:
                entry(it[1], 'Topic', ptitle, f'{gd["href"]}#topic-{it[0]}')
        for sid, label, grp in flat_sections(items):
            entry(label, 'Section', ' › '.join(x for x in (ptitle, grp) if x), f'{gd["href"]}#{sid}')
            where[sid] = (ptitle, label)
    for hid, text in headings(gd['path']):
        ptitle, label = where.get(hid.split('--')[0], ('', ''))
        entry(text, 'Heading', ' › '.join(x for x in (ptitle, label) if x), f'{gd["href"]}#{hid}')

# ---- nav.js: the shared header script every guide loads from this folder
manifest = dict(hub='index.html', title=cfg.TITLE, themeKey=STORE + '-theme', recentKey=STORE + '-recent',
                guides=[dict(folder=g['folder'], title=g['title'], kind=g['kind'], href=g['href'], color=g['color']) for g in guides])
nav = open(os.path.join(E, 'nav.src.js'), encoding='utf-8').read().replace('__MANIFEST__', json.dumps(manifest))
open(os.path.join(ROOT, 'nav.js'), 'w', encoding='utf-8').write(nav)
REPO_NAME = os.path.basename(HUB_REPO)


def toc_cols(gd):
    """Every page and section of a guide, one column per page."""
    cols = []
    for i, (pid, ptitle, _b, items) in enumerate(gd['parts']):
        rows, grp_open = [], None
        for sid, label, grp in flat_sections(items):
            if grp != grp_open and grp:
                rows.append(f'<li class="grp">Topic: {esc(grp)}</li>')
            grp_open = grp
            cls = ' class="in-grp"' if grp else ''
            rows.append(f'<li{cls}><a href="{gd["href"]}#{sid}">{esc(label)}</a></li>')
        cols.append(f'<div class="toc-col"><a class="toc-page" href="{gd["href"]}#part-{pid}"><span class="num">{i + 1}</span>{esc(ptitle)}</a>'
                    f'<ul>{"".join(rows)}</ul></div>')
    return f'<div class="toc-cols">{"".join(cols)}</div>'


def contents(gd):
    return f'<details class="toc"><summary>{"All " if count(gd) > 1 else ""}{plural(count(gd), "section")}</summary>{toc_cols(gd)}</details>'


def meta_line(gd, short=False, html=True):
    meta = [f'Updated {gd["built"]}' if gd['built'] else 'Not built yet']
    if gd.get('commit') and not short:
        meta.append(f'{esc(REPO_NAME)} <code>{esc(gd["commit"])}</code>' if html else f'from {REPO_NAME} @ {gd["commit"]}')
    return ' · '.join(meta)


def page_tiles(gd):
    return '<ol class="tiles">' + ''.join(
        f'<li {hue_style(PALETTE[i % len(PALETTE)])}><a class="tile" href="{gd["href"]}#part-{pid}"><span class="num">{i + 1}</span>'
        f'<span class="tile-body"><span class="tile-title">{esc(ptitle)}</span><span class="tile-blurb">{esc(blurb)}</span>'
        f'<span class="tile-count">{plural(len(flat_sections(items)), "section")}</span></span></a></li>'
        for i, (pid, ptitle, blurb, items) in enumerate(gd['parts'])) + '</ol>'


def featured(gd):
    return (f'<article class="card featured" aria-labelledby="g-{gd["folder"]}">'
            f'<div class="card-head"><div><h3 id="g-{gd["folder"]}">{esc(gd["title"])}</h3><p class="blurb">{esc(gd["blurb"])}</p>'
            f'<p class="meta">{meta_line(gd)}</p></div>'
            f'<a class="btn primary" href="{gd["href"]}">Open guide <span aria-hidden="true">→</span></a></div>'
            f'{page_tiles(gd)}{contents(gd)}</article>')


def topic_row(i, gd):
    chips = ''.join(f'<li>{esc(t["name"])}</li>' for t in gd['topics'].values())
    pages = ''.join(f'<li><a href="{gd["href"]}#part-{pid}">{esc(ptitle)}</a></li>' for pid, ptitle, _b, _items in gd['parts'])
    words = ' '.join([gd['title'], gd['blurb']] + [t['name'] for t in gd['topics'].values()]).lower()
    return (f'<tbody class="row-group" {hue_style(gd["color"])} data-words="{esc(words)}" data-name="{esc(gd["title"].lower())}" data-sections="{count(gd)}" '
            f'data-updated="{gd["built"] or ""}">'
            f'<tr class="row"><td class="c-toggle"><button type="button" class="expand" aria-expanded="false" aria-controls="pv-{i}" '
            f'aria-label="Preview sections of {esc(gd["title"])}" title="Preview sections"><svg viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="M9.29 6.71a1 1 0 0 0 0 1.41L13.17 12l-3.88 3.88a1 1 0 1 0 1.41 1.41l4.59-4.59a1 1 0 0 0 0-1.41L10.7 6.7a1 1 0 0 0-1.41.01"/></svg></button></td>'
            f'<th scope="row" class="c-name"><a href="{gd["href"]}">{esc(gd["title"])}</a><span class="c-blurb" title="{esc(gd["blurb"])}">{esc(gd["blurb"])}</span></th>'
            f'<td class="c-topics"><ul class="chips">{chips}</ul></td>'
            f'<td class="c-pages"><ul class="inline-pages">{pages}</ul></td>'
            f'<td class="c-num">{count(gd)}</td>'
            f'<td class="c-date" title="{esc(meta_line(gd, html=False))}">{gd["built"] or "—"}</td></tr>'
            f'<tr class="preview" id="pv-{i}" hidden><td></td><td colspan="5">{toc_cols(gd)}</td></tr></tbody>')


app_cards = ''.join(featured(g) for g in guides if g['kind'] == 'app')
topic_rows = ''.join(topic_row(i, g) for i, g in enumerate(sorted((g for g in guides if g['kind'] == 'topic'), key=lambda g: g['title'].lower())))
color_by_folder = {g['folder']: g['color'] for g in guides}
quick = ''.join(f'<li {hue_style(color_by_folder[folder])}><a href="{href}" title="{esc(where)}">{esc(name)}</a></li>'
                for name, href, where, folder in topic_index[:QUICK_TOPICS])
if len(topic_index) > QUICK_TOPICS:
    quick += f'<li><a class="more" href="#h-topics">+{len(topic_index) - QUICK_TOPICS} more</a></li>'

fonts = ''.join(
    f"@font-face{{font-family:'{family}';font-weight:{weight};font-display:swap;src:url(data:font/woff2;base64,"
    f"{base64.b64encode(open(os.path.join(ROOT, path), 'rb').read()).decode()}) format('woff2');}}"
    for family, weight, path in getattr(cfg, 'FONTS', []))
tokens = open(os.path.join(ROOT, cfg.TOKENS_CSS) if getattr(cfg, 'TOKENS_CSS', None) else os.path.join(E, 'tokens.css'),
              encoding='utf-8').read()
depth = open(os.path.join(E, 'depth.css'), encoding='utf-8').read()

CSS = r'''
html { color-scheme: light; } html[data-theme='dark'] { color-scheme: dark; }
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body { margin: 0; background: var(--color-bg); color: var(--color-text); font-family: var(--font-family); font-size: 15px; line-height: 1.55; }
a { color: var(--color-link); text-underline-offset: 2px; }
a:focus-visible, button:focus-visible, summary:focus-visible, input:focus-visible { outline: 2px solid var(--hub-brand); outline-offset: 2px; border-radius: 6px; }
code { font-size: 0.85em; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.skip { position: absolute; left: 12px; top: -48px; z-index: 20; padding: 8px 14px; border-radius: 8px; background: var(--hub-brand); color: #fff; }
.skip:focus { top: 12px; }

.topbar { position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 12px; padding: 10px 24px;
  background: var(--color-bg-light); border-bottom: 1px solid var(--color-border-light); }
.logo { display: grid; place-items: center; width: 32px; height: 32px; border-radius: 8px; background: var(--hub-brand); }
.logo svg { width: 20px; height: 20px; fill: #fff; }
.brand { font-weight: var(--font-weight-emphasis); font-size: 17px; }
.spacer { flex: 1; }
#theme-toggle { font: inherit; font-size: 14px; font-weight: var(--font-weight-emphasis); cursor: pointer; padding: 6px 14px; border-radius: 999px;
  border: 1px solid var(--color-button-default-border); background: var(--color-button-default); color: var(--color-text); }

main { max-width: 1120px; margin: 0 auto; padding: 0 24px 64px; }
.hero { padding: 48px 0 24px; text-align: center; }
.hero h1 { margin: 0 0 8px; font-size: 32px; line-height: 1.2; font-weight: var(--font-weight-emphasis); }
.hero .lede { margin: 0 auto 24px; max-width: 620px; color: var(--color-text-light); font-size: 16px; }
.search { position: relative; max-width: 640px; margin: 0 auto; }
.search svg { position: absolute; left: 16px; top: 50%; width: 20px; height: 20px; transform: translateY(-50%); fill: var(--color-text-light); pointer-events: none; }
.search input { width: 100%; font: inherit; font-size: 16px; padding: 14px 52px 14px 46px; border-radius: 12px; border: 1px solid var(--color-border);
  background: var(--color-bg-light); color: var(--color-text); box-shadow: var(--shadow-lv1); }
.search input::placeholder { color: var(--color-text-light); }
.search kbd { position: absolute; right: 14px; top: 50%; transform: translateY(-50%); font: inherit; font-size: 12px; padding: 1px 7px;
  border: 1px solid var(--color-border); border-radius: 6px; color: var(--color-text-light); }
.quick { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 8px; margin: 18px 0 0; padding: 0; list-style: none; }
.quick-label { color: var(--color-text-light); font-size: 14px; margin-right: 2px; }
.quick a { display: inline-block; padding: 5px 14px; border-radius: 999px; font-size: 14px; font-weight: var(--font-weight-emphasis); text-decoration: none;
  background: var(--color-blue-bg); color: var(--color-blue-fg); }
.quick a:hover { text-decoration: underline; }

.results { max-width: 640px; margin: 12px auto 0; padding: 6px; list-style: none; text-align: left; border: 1px solid var(--color-border-light);
  border-radius: 12px; background: var(--color-bg-light); box-shadow: var(--shadow-lv2); }
.results ul { list-style: none; margin: 0; padding: 0; }
.r-group + .r-group { margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--color-border-light); }
.r-label { padding: 6px 14px 4px; font-size: 12px; font-weight: var(--font-weight-emphasis); text-transform: uppercase; letter-spacing: .04em; color: var(--color-text-light); }
.r-count { margin-left: 4px; padding: 0 6px; border-radius: 999px; background: var(--color-bg); font-variant-numeric: tabular-nums; }
.results [role="option"] { display: block; padding: 8px 14px; border-radius: 8px; cursor: pointer; }
.results [role="option"][aria-selected="true"] { background: var(--color-menu-item-hover); box-shadow: inset 3px 0 0 var(--hub-brand); }
.results .r-title { display: block; font-weight: var(--font-weight-emphasis); }
.results .r-ctx { display: block; font-size: 13px; color: var(--color-text-light); }
.r-kind { display: inline-block; margin-right: 6px; padding: 0 6px; border-radius: 4px; font-size: 11px; font-weight: var(--font-weight-emphasis);
  background: var(--color-bg); color: var(--color-text-light); }
.r-more { padding: 4px 14px 6px; font-size: 13px; color: var(--color-text-light); }
.results mark { background: none; color: var(--color-link); text-decoration: underline; text-decoration-thickness: 2px; }
.continue { margin-top: 8px; }
.cont-head { display: flex; align-items: baseline; gap: 12px; }
.cont-head h2 { margin-top: 24px; }
.link-btn { font: inherit; font-size: 13px; color: var(--color-text-light); background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; }
.link-btn:hover { color: var(--color-text); }
#continue-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(240px, 100%), 1fr)); gap: 12px; margin: 12px 0 0; padding: 0; list-style: none; }
.cont { display: flex; flex-direction: column; gap: 2px; height: 100%; padding: 12px 16px; border-radius: 10px; border: 1px solid var(--color-border-light);
  background: var(--color-bg-light); color: var(--color-text); text-decoration: none; }
.cont:hover { border-color: var(--hub-brand); }
.cont.first { border-left: 4px solid var(--hub-brand); }
.cont-guide { font-size: 12px; color: var(--color-text-light); }
.cont-where { font-weight: var(--font-weight-emphasis); }
.cont-when { font-size: 12px; color: var(--color-text-light); }
.results .none { padding: 14px; color: var(--color-text-light); }

h2 { font-size: 20px; margin: 40px 0 4px; }
h2 .count { font-size: 15px; font-weight: var(--font-weight-regular); color: var(--color-text-light); }
.section-intro { margin: 0 0 16px; color: var(--color-text-light); }
.card { display: flex; flex-direction: column; background: var(--color-bg-light); border: 1px solid var(--color-border-light); border-radius: 14px;
  padding: 22px 24px; box-shadow: var(--shadow-lv1); }
.card h3 { margin: 0; font-size: 19px; line-height: 1.3; }
.card h3 a { color: var(--color-text); text-decoration: none; } .card h3 a:hover { text-decoration: underline; }
.blurb { margin: 6px 0 0; color: var(--color-text-light); }
.meta { margin: 8px 0 0; font-size: 13px; color: var(--color-text-light); }
.btn { display: inline-flex; align-items: center; gap: 6px; flex: none; padding: 8px 16px; border-radius: 999px; font-weight: var(--font-weight-emphasis);
  font-size: 14px; text-decoration: none; color: var(--color-text); border: 1px solid var(--color-button-default-border); background: var(--color-button-default); }
.btn:hover { background: var(--color-menu-item-hover); }
.btn.primary { background: var(--hub-brand); border-color: var(--hub-brand); color: #fff; }
.btn.primary:hover { filter: brightness(1.1); }
.num { display: inline-grid; place-items: center; flex: none; width: 22px; height: 22px; border-radius: 50%; font-size: 12px;
  font-weight: var(--font-weight-emphasis); background: var(--color-blue-bg); color: var(--color-blue-fg); }

.featured { border-top: 4px solid var(--hub-brand); }
.card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; }
.card-head h3 { font-size: 22px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(190px, 100%), 1fr)); gap: 12px; margin: 20px 0 0; padding: 0; list-style: none; }
.tile { display: flex; gap: 10px; height: 100%; padding: 14px; border-radius: 10px; border: 1px solid var(--color-border-light);
  background: var(--color-bg); color: var(--color-text); text-decoration: none; }
.tile:hover { border-color: var(--hub-brand); }
.tile-body { display: flex; flex-direction: column; gap: 4px; }
.tile-title { font-weight: var(--font-weight-emphasis); }
.tile-blurb { font-size: 13px; color: var(--color-text-light); }
.tile-count { margin-top: auto; font-size: 12px; color: var(--color-link); font-weight: var(--font-weight-emphasis); }

.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0 0; padding: 0; list-style: none; }
.chips li { padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: var(--font-weight-emphasis); background: var(--color-blue-bg); color: var(--color-blue-fg); }
.chips { margin: 0; }
.table-tools { display: flex; align-items: center; gap: 12px; margin: 0 0 10px; }
#tf { font: inherit; font-size: 14px; width: 260px; max-width: 100%; padding: 7px 12px; border-radius: 8px; border: 1px solid var(--color-border);
  background: var(--color-bg-light); color: var(--color-text); }
.table-wrap { overflow-x: auto; border: 1px solid var(--color-border-light); border-radius: 12px; background: var(--color-bg-light); box-shadow: var(--shadow-lv1); }
table.guides { width: 100%; border-collapse: collapse; font-size: 14px; }
.guides thead th { text-align: left; font-size: 12px; font-weight: var(--font-weight-emphasis); text-transform: uppercase; letter-spacing: .04em;
  color: var(--color-text-light); padding: 10px 12px; border-bottom: 1px solid var(--color-border-light); white-space: nowrap; }
.guides thead button { font: inherit; text-transform: inherit; letter-spacing: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }
.guides thead button::after { content: ' ↕'; opacity: .45; }
.guides th[aria-sort="ascending"] button::after { content: ' ↑'; opacity: 1; }
.guides th[aria-sort="descending"] button::after { content: ' ↓'; opacity: 1; }
.guides thead button:hover { color: var(--color-text); }
.guides tbody + tbody .row > * { border-top: 1px solid var(--color-border-light); }
.guides .row > * { padding: 10px 12px; vertical-align: top; text-align: left; font-weight: inherit; }
.guides .row { cursor: pointer; }
.guides .row:hover { background: var(--color-menu-item-hover); }
.c-toggle { width: 36px; padding-right: 0 !important; }
.c-name { min-width: 220px; }
.c-name a { display: block; font-weight: var(--font-weight-emphasis); font-size: 15px; color: var(--color-text); text-decoration: none; }
.c-name a:hover { text-decoration: underline; }
.c-blurb { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; margin-top: 2px; font-size: 13px; color: var(--color-text-light); }
.c-num, .c-date { white-space: nowrap; color: var(--color-text-light); }
.c-num { text-align: right !important; font-variant-numeric: tabular-nums; }
.inline-pages { display: flex; flex-wrap: wrap; gap: 2px 14px; margin: 0; padding: 0; list-style: none; }
.inline-pages li { white-space: nowrap; }
.inline-pages a { text-decoration: none; } .inline-pages a:hover { text-decoration: underline; }
.expand { display: grid; place-items: center; width: 26px; height: 26px; border-radius: 6px; border: 1px solid var(--color-border-light);
  background: var(--color-bg); color: var(--color-text-light); cursor: pointer; }
.expand svg { width: 18px; height: 18px; fill: currentcolor; transition: transform .15s; }
.expand[aria-expanded="true"] svg { transform: rotate(90deg); }
.expand:hover { color: var(--color-text); border-color: var(--color-border); }
.preview td { padding: 0 12px 14px; }
.preview .toc-cols { margin-top: 0; padding: 12px 14px; border-radius: 10px; background: var(--color-bg); }
.quick .more { background: none; color: var(--color-link); }
@media (max-width: 860px) { .guides .c-topics { display: none; } }
@media (max-width: 640px) { .guides .c-pages, .guides .c-date { display: none; } .c-name { min-width: 0; } .c-blurb { -webkit-line-clamp: 2; } }
.toc { margin-top: 14px; }
.toc summary { cursor: pointer; width: max-content; font-size: 14px; font-weight: var(--font-weight-emphasis); color: var(--color-link); padding: 2px 0; }
.toc-cols { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(200px, 100%), 1fr)); gap: 16px 24px; margin-top: 12px; }
.toc-page { display: flex; align-items: center; gap: 8px; font-weight: var(--font-weight-emphasis); color: var(--color-text); text-decoration: none; }
.toc-cols ul { margin: 6px 0 0; padding: 0 0 0 30px; list-style: none; }
.toc-cols li { margin: 3px 0; font-size: 14px; }
.toc-cols li a { text-decoration: none; } .toc-cols li a:hover { text-decoration: underline; }
.toc-cols li.grp { margin-top: 8px; font-size: 12px; font-weight: var(--font-weight-emphasis); text-transform: uppercase; letter-spacing: .04em; color: var(--color-text-light); }
.toc-cols li.in-grp { padding-left: 12px; }

footer { color: var(--color-text-light); font-size: 13px; text-align: center; padding: 24px; border-top: 1px solid var(--color-border-light); }
@media (max-width: 640px) {
  .card-head { flex-direction: column; } .hero { padding-top: 32px; } .hero h1 { font-size: 26px; }
  .search kbd { display: none; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }


/* ---------- each guide's color (--h, its BRAND_COLOR) as a small marker only; surfaces and shadows come from depth.css ---------- */
.topbar { background: color-mix(in srgb, var(--color-bg-light) 80%, transparent); backdrop-filter: blur(12px); }
.search input { border-color: transparent; box-shadow: var(--shadow-lv2), 0 0 0 1px var(--color-border-light); }
.search input:focus { box-shadow: var(--shadow-lv2), 0 0 0 2px var(--hub-brand); outline: none; }
.quick a { background: var(--color-bg-light); color: var(--color-text); box-shadow: var(--shadow-lv1), 0 0 0 1px var(--color-border-light); }
.quick a::before { content: ''; display: inline-block; width: 8px; height: 8px; margin-right: 7px; border-radius: 2px; background: var(--h); }
.quick a:hover { text-decoration: none; box-shadow: var(--shadow-lv1), 0 0 0 1px var(--color-border); }
.quick .more { background: none; box-shadow: none; } .quick .more::before { content: none; }
.c-name a::before, .r-label::before, .cont-guide::before {
  content: ''; display: inline-block; width: 8px; height: 8px; margin-right: 8px; border-radius: 2px; background: var(--h, var(--hub-brand)); }

.card { border-color: var(--color-border-light); box-shadow: var(--shadow-lv2); }
.featured { border-top: 3px solid var(--hub-brand); }
.tile { border-color: var(--color-border-light); background: var(--color-bg-light); box-shadow: var(--shadow-lv1); transition: transform .15s, box-shadow .15s; }
.tile:hover { transform: translateY(-1px); border-color: var(--color-border); box-shadow: var(--shadow-lv2); }
.tile .num { background: var(--h-bg); color: var(--h-fg); }

.table-wrap { border-color: var(--color-border-light); box-shadow: var(--shadow-lv2); }
.guides thead th { background: var(--surface-2); }
.guides .row > :first-child { box-shadow: inset 3px 0 0 var(--h); }
.c-name a::before { vertical-align: 1px; }
#tf { border-color: transparent; box-shadow: var(--shadow-lv1), 0 0 0 1px var(--color-border-light); }

.results { border-color: var(--color-border-light); box-shadow: var(--shadow-lv3); }

.cont { border-color: var(--color-border-light); border-left: 3px solid var(--h); box-shadow: var(--shadow-lv1); transition: transform .15s, box-shadow .15s; }
.cont.first { border-left-color: var(--h); }
.cont:hover { transform: translateY(-1px); border-color: var(--color-border); border-left-color: var(--h); box-shadow: var(--shadow-lv2); }
footer { background: var(--color-bg-light); }
@media (prefers-reduced-motion: reduce) { .tile:hover, .cont:hover { transform: none; } }
'''

JS = r'''
(function () {
  var root = document.documentElement, KEY = '__STORE__-theme', stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) { /* storage unavailable */ }
  root.setAttribute('data-theme', stored || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('theme-toggle');
    var label = function () {
      var dark = root.getAttribute('data-theme') === 'dark';
      btn.textContent = dark ? '☀ Light' : '☾ Dark';
      btn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    };
    label();
    btn.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* storage unavailable */ }
      label();
    });

    var INDEX = JSON.parse(document.getElementById('search-index').textContent);
    var RECENT_KEY = '__STORE__-recent', PER_GUIDE = 6;
    var HUE = JSON.parse(document.getElementById('guide-colors').textContent);
    var hueStyle = function (c) {
      return c ? ' style="--h: ' + c + '; --h-bg: color-mix(in srgb, ' + c + ' 16%, var(--color-bg-light)); --h-fg: color-mix(in srgb, ' + c + ' 75%, var(--color-text))"' : '';
    };
    var input = document.getElementById('q'), list = document.getElementById('results'),
        status = document.getElementById('status'), browse = document.getElementById('browse'), quick = document.getElementById('quick');
    var plain = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); };
    function highlight(s, words) {
      var low = s.toLowerCase(), marks = [];
      words.forEach(function (w) { var i = low.indexOf(w); if (i >= 0) marks.push([i, i + w.length]); });
      marks.sort(function (a, b) { return a[0] - b[0]; });
      var out = '', at = 0;
      marks.forEach(function (m) { if (m[0] >= at) { out += plain(s.slice(at, m[0])) + '<mark>' + plain(s.slice(m[0], m[1])) + '</mark>'; at = m[1]; } });
      return out + plain(s.slice(at));
    }
    function recent() { try { return JSON.parse(localStorage.getItem(RECENT_KEY)) || []; } catch (e) { return []; } }
    function ago(t) {
      var m = Math.round((Date.now() - t) / 60000);
      return m < 1 ? 'just now' : m < 60 ? m + ' min ago' : m < 1440 ? Math.round(m / 60) + ' h ago' : Math.round(m / 1440) + ' d ago';
    }
    function where(e) { return e.trail.length ? e.trail[e.trail.length - 1] : 'Start of guide'; }

    var options = [], active = -1, n = 0;
    function option(href, title, ctx) {
      return '<li role="option" id="ro-' + (n++) + '" data-href="' + plain(href) + '" aria-selected="false"><span class="r-title">' + title +
        '</span><span class="r-ctx">' + ctx + '</span></li>';
    }
    function group(label, items, extra, hue) {
      var id = 'rg-' + (n++);
      return '<li role="presentation" class="r-group"' + hueStyle(hue) + '><div class="r-label" id="' + id + '">' + label + '</div>' +
        '<ul role="group" aria-labelledby="' + id + '">' + items.join('') + '</ul>' + (extra || '') + '</li>';
    }
    function show(html, msg) {
      list.innerHTML = html;
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      options = Array.prototype.slice.call(list.querySelectorAll('[role="option"]'));
      select(-1);
      status.textContent = msg;
    }
    function close() {
      list.hidden = true;
      list.innerHTML = '';
      options = [];
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
    }
    function select(i) {
      active = i;
      options.forEach(function (o, j) { o.setAttribute('aria-selected', j === i ? 'true' : 'false'); });
      if (i < 0) { input.removeAttribute('aria-activedescendant'); return; }
      input.setAttribute('aria-activedescendant', options[i].id);
      options[i].scrollIntoView({ block: 'nearest' });
    }
    function showRecent() {
      var r = recent();
      if (!r.length) { close(); return; }
      n = 0;
      show(group('Recently read', r.map(function (e) {
        return option(e.href, plain(where(e)), plain(e.title) + ' · ' + ago(e.t)).replace('<li ', '<li' + hueStyle(HUE[e.g]) + ' ');
      })), r.length + ' recently read pages. Use up and down arrows to choose.');
    }
    function run() {
      var raw = input.value.trim(), q = raw.toLowerCase();
      browse.hidden = quick.hidden = !!q;
      if (!q) { if (document.activeElement === input) showRecent(); else close(); return; }
      var words = q.split(/\s+/), hits = [];
      INDEX.forEach(function (e) {
        var t = e.t.toLowerCase(), all = (e.t + ' ' + e.g + ' ' + e.c).toLowerCase();
        if (!words.every(function (w) { return all.indexOf(w) >= 0; })) return;
        var rank = t.indexOf(q) === 0 ? 0 : t.indexOf(q) >= 0 ? 1 : words.every(function (w) { return t.indexOf(w) >= 0; }) ? 2 : 3;
        hits.push({ s: rank * 2 + (e.k === 'Heading' ? 1 : 0), e: e });
      });
      n = 0;
      if (!hits.length) { show('<li role="presentation" class="none">Nothing matches “' + plain(raw) + '”. Try a shorter word.</li>', 'No results.'); return; }
      hits.sort(function (a, b) { return a.s - b.s; });
      var byGuide = {}, order = [], hueOf = {};
      hits.forEach(function (h) { if (!byGuide[h.e.g]) { byGuide[h.e.g] = []; order.push(h.e.g); hueOf[h.e.g] = HUE[h.e.u]; } byGuide[h.e.g].push(h); });
      show(order.map(function (g) {
        var all = byGuide[g], items = all.slice(0, PER_GUIDE).map(function (h) {
          return option(h.e.h, highlight(h.e.t, words), '<span class="r-kind">' + h.e.k + '</span>' + plain(h.e.c));
        });
        var more = all.length > PER_GUIDE ? '<div class="r-more">+' + (all.length - PER_GUIDE) + ' more in this guide. Add a word to narrow it down.</div>' : '';
        return group(plain(g) + ' <span class="r-count">' + all.length + '</span>', items, more, hueOf[g]);
      }).join(''), hits.length + (hits.length === 1 ? ' result' : ' results') + ' in ' + order.length + (order.length === 1 ? ' guide.' : ' guides.') + ' Use up and down arrows to choose, Enter to open.');
    }
    function go(o) { if (o) location.href = o.dataset.href; }
    input.addEventListener('input', run);
    input.addEventListener('focus', function () { if (!input.value.trim()) showRecent(); });
    input.addEventListener('blur', function () { if (!input.value.trim()) close(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (list.hidden) run(); select(Math.min(active + 1, options.length - 1)); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); select(Math.max(active - 1, -1)); }
      else if (e.key === 'Enter') { e.preventDefault(); go(options[active >= 0 ? active : 0]); }
      else if (e.key === 'Escape') { e.preventDefault(); if (input.value) { input.value = ''; run(); } else close(); }
    });
    list.addEventListener('mousedown', function (e) { e.preventDefault(); });
    list.addEventListener('click', function (e) { go(e.target.closest('[role="option"]')); });
    list.addEventListener('mousemove', function (e) { var o = e.target.closest('[role="option"]'); if (o && options.indexOf(o) !== active) select(options.indexOf(o)); });

    var cont = document.getElementById('continue'), contList = document.getElementById('continue-list');
    function renderContinue() {
      var r = recent().slice(0, 4);
      cont.hidden = !r.length;
      contList.innerHTML = r.map(function (e, i) {
        return '<li' + hueStyle(HUE[e.g]) + '><a class="cont' + (i ? '' : ' first') + '" href="' + plain(e.href) + '"><span class="cont-guide">' + plain(e.title) + '</span>' +
          '<span class="cont-where">' + plain(where(e)) + '</span><span class="cont-when">' + ago(e.t) + '</span></a></li>';
      }).join('');
    }
    document.getElementById('continue-clear').addEventListener('click', function () {
      try { localStorage.removeItem(RECENT_KEY); } catch (e) { /* storage unavailable */ }
      renderContinue();
      input.focus();
    });
    renderContinue();
    addEventListener('pageshow', renderContinue);

    var asked = new URLSearchParams(location.search).get('q');
    if (asked) { input.value = asked; input.focus(); run(); }

    var table = document.getElementById('guides'), groups = table ? Array.prototype.slice.call(table.tBodies) : [];
    if (table) {
    table.addEventListener('click', function (e) {
      var row = e.target.closest('.row');
      if (!row || (e.target.closest('a') && !e.target.closest('.expand'))) return;
      var b = row.querySelector('.expand');
      var open = b.getAttribute('aria-expanded') !== 'true';
      b.setAttribute('aria-expanded', open);
      document.getElementById(b.getAttribute('aria-controls')).hidden = !open;
    });
    var tf = document.getElementById('tf'), tfCount = document.getElementById('tf-count');
    function filterRows() {
      var words = tf.value.trim().toLowerCase().split(/\s+/).filter(Boolean), shown = 0;
      groups.forEach(function (g) {
        var hit = words.every(function (w) { return g.dataset.words.indexOf(w) >= 0; });
        g.hidden = !hit; if (hit) shown++;
      });
      tfCount.textContent = words.length ? shown + ' of ' + groups.length + ' guides' : groups.length + ' guides';
      document.getElementById('tf-empty').hidden = shown > 0;
    }
    tf.addEventListener('input', filterRows);
    tf.addEventListener('keydown', function (e) { if (e.key === 'Escape') { tf.value = ''; filterRows(); } });
    filterRows();
    table.querySelectorAll('thead button[data-sort]').forEach(function (b) {
      b.addEventListener('click', function () {
        var th = b.parentElement, key = b.dataset.sort, cur = th.getAttribute('aria-sort');
        var dir = cur === 'ascending' ? 'descending' : cur === 'descending' ? 'ascending' : key === 'name' ? 'ascending' : 'descending';
        table.querySelectorAll('thead th[aria-sort]').forEach(function (x) { x.setAttribute('aria-sort', 'none'); });
        th.setAttribute('aria-sort', dir);
        var val = function (g) { return key === 'sections' ? +g.dataset.sections : g.dataset[key]; };
        groups.sort(function (a, c) { var x = val(a), y = val(c), r = x < y ? -1 : x > y ? 1 : 0; return dir === 'ascending' ? r : -r; })
          .forEach(function (g) { table.appendChild(g); });
      });
    });
    }
    document.addEventListener('keydown', function (e) {
      var typing = /INPUT|TEXTAREA/.test(document.activeElement.tagName);
      if ((e.key === '/' && !typing) || (e.key === 'k' && (e.metaKey || e.ctrlKey))) { e.preventDefault(); input.focus(); input.select(); }
    });
  });
})();
'''

LOGO = getattr(cfg, 'LOGO_SVG', None) or ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z"/></svg>')
SEARCH_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 1 0-.7.7l.27.28v.79l4.25 4.25a1 1 0 0 0 '
               '1.42-1.42zm-6 0a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9"/></svg>')
n_sections = sum(count(g) for g in guides)
n_topic_guides = sum(1 for g in guides if g['kind'] == 'topic')
start_here = (f'<section aria-labelledby="h-start"><h2 id="h-start">Start here</h2>\n'
              f'<p class="section-intro">The whole app, end to end. New to {esc(APP)}? Read this first.</p>\n{app_cards}</section>'
              if app_cards else '')
topic_table = f"""<section aria-labelledby="h-topics"><h2 id="h-topics">Topic guides <span class="count">({n_topic_guides})</span></h2>
<p class="section-intro">One technology each, and exactly how {esc(APP)} uses it. Select a row to preview its sections.</p>
<div class="table-tools"><label class="sr-only" for="tf">Filter topic guides</label>
<input id="tf" type="search" placeholder="Filter topic guides" autocomplete="off">
<span id="tf-count" class="meta" aria-live="polite"></span></div>
<div class="table-wrap"><table class="guides" id="guides">
<thead><tr><th scope="col" class="c-toggle"><span class="sr-only">Preview</span></th>
<th scope="col" aria-sort="ascending"><button type="button" data-sort="name">Guide</button></th>
<th scope="col" class="c-topics">Topics</th><th scope="col" class="c-pages">Pages</th>
<th scope="col" class="c-num" aria-sort="none"><button type="button" data-sort="sections">Sections</button></th>
<th scope="col" class="c-date" aria-sort="none"><button type="button" data-sort="updated">Updated</button></th></tr></thead>
{topic_rows}
</table></div>
<p id="tf-empty" class="meta" hidden>No topic guide matches that filter.</p></section>""" if topic_rows else ''
quick_html = f'<ul class="quick" id="quick" aria-label="Jump to a topic"><li class="quick-label" aria-hidden="true">Jump to:</li>{quick}</ul>' if quick else '<ul class="quick" id="quick" hidden></ul>'
index_json = json.dumps(search_index).replace('</', '<\\/')
headline = getattr(cfg, 'HEADLINE', None) or f'Learn the {APP} codebase'
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(cfg.TITLE)}</title>
<style>{fonts}
{tokens}
:root {{ --hub-brand: {cfg.BRAND_COLOR}; }}
{CSS}
{depth}</style>
<script>{JS.replace('__STORE__', STORE)}</script>
<script type="application/json" id="guide-colors">{json.dumps(color_by_folder)}</script>
<script type="application/json" id="search-index">{index_json}</script></head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar"><div class="logo">{LOGO}</div><span class="brand">{esc(cfg.TITLE)}</span><span class="spacer"></span>
<button id="theme-toggle" type="button">☾ Dark</button></header>
<main id="main">
<section class="hero" aria-labelledby="hero-title">
<h1 id="hero-title">{esc(headline)}</h1>
<p class="lede">{plural(len(guides), 'guide')} and {plural(n_sections, 'section')} in one place. Start with the big picture, then go deep on one technology.</p>
<div class="search" role="search">{SEARCH_ICON}
<label class="sr-only" for="q">Search every guide</label>
<input id="q" type="search" placeholder="Search all guides, sections and headings" autocomplete="off" role="combobox" aria-expanded="false" aria-autocomplete="list" aria-controls="results" aria-describedby="status">
<kbd aria-hidden="true">/</kbd></div>
<p id="status" class="sr-only" aria-live="polite"></p>
<ul id="results" class="results" role="listbox" hidden aria-label="Search results"></ul>
{quick_html}
</section>
<div id="browse">
<section id="continue" class="continue" hidden aria-labelledby="h-cont"><div class="cont-head"><h2 id="h-cont">Continue reading</h2><button type="button" id="continue-clear" class="link-btn">Clear history</button></div><ul id="continue-list"></ul></section>
{start_here}
{topic_table}
</div>
</main>
<footer>{getattr(cfg, 'FOOTER', None) or f'Built {TODAY.isoformat()} from {plural(len(guides), "guide")} for the <code>{esc(REPO_NAME)}</code> repository. Internal use only.'}</footer>
</body></html>
"""
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
print(f'OK {os.path.join(ROOT, "index.html")}: {plural(len(guides), "guide")}, {plural(len(topic_index), "topic")}, {plural(n_sections, "section")}')
for w in warnings:
    print('WARNING', w)
