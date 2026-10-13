"""Page chrome: compact header, collapsible sections, and the floating tree sidebar."""
import html
import re

# Progressive disclosure: sections that explain what the app is and how it fits together start
# open. Deep dives and reference material start collapsed and open on demand.
# Collapse defaults. build.py overwrites these from guide_config.py before wrapping sections.
COLLAPSED_SECTIONS = set()          # section ids that start collapsed
COLLAPSED_SUBSECTIONS = set()       # (section id, h3 title) pairs that start collapsed
COLLAPSED_GROUP_SECTIONS = set()    # sections whose table group rows start collapsed
OPEN_TABLE_GROUPS = set()           # group labels that stay open inside those sections
COLLAPSED_TABLE_GROUPS = set()      # group labels that start collapsed anywhere

CHEVRON = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.29 6.71a.996.996 0 0 0 0 1.41L13.17 12l-3.88 3.88a.996.996 0 1 0 1.41 1.41l4.59-4.59a.996.996 0 0 0 0-1.41L10.7 6.7c-.38-.38-1.02-.38-1.41.01"/></svg>'


def slug(text):
    text = html.unescape(re.sub(r'<[^>]+>', '', text))
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def wrap_section(section_html, sid):
    """Make the section body and its top-level <h3> subsections collapsible.

    Returns the new HTML and the subsections as [(id, title)] for the sidebar.
    """
    m = re.match(r'(?s)(.*?<section id="\w+">\s*)<h2>(.*?)</h2>(\s*<p class="sub">.*?</p>)?(.*)(</section>\s*)$', section_html)
    assert m, sid
    prefix, title, sub, body, suffix = m.groups()
    sub = sub or ''
    subsections = []
    parts = re.split(r'(?m)^  (<h3[^>]*>.*?</h3>)\s*$', body)
    out = [parts[0]]
    for i in range(1, len(parts), 2):
        h3, content = parts[i], parts[i + 1]
        h3_title = re.sub(r'^<h3[^>]*>|</h3>$', '', h3)
        sub_id = f'{sid}--{slug(h3_title)}'
        collapsed = (sid, h3_title) in COLLAPSED_SUBSECTIONS
        subsections.append((sub_id, h3_title))
        out.append(
            f'\n  <div class="subsec" id="{sub_id}"{" data-collapsed-default" if collapsed else ""}>'
            f'<h3 class="subsec-title"><button type="button" class="toggle" aria-expanded="true" aria-controls="{sub_id}-body">'
            f'{CHEVRON}<span>{h3_title}</span></button></h3>'
            f'<div class="subsec-body" id="{sub_id}-body">{content}</div></div>\n')
    body = ''.join(out)
    def mark_group(row):
        text = re.sub(r'<svg.*?</svg>', '', row.group(0), flags=re.S)
        label = re.sub(r'<[^>]+>', '', text)
        in_open = any(group in label for group in OPEN_TABLE_GROUPS)
        if (sid in COLLAPSED_GROUP_SECTIONS and not in_open) or any(group in label for group in COLLAPSED_TABLE_GROUPS):
            return row.group(0).replace('<tr class="group"', '<tr class="group" data-collapsed-default', 1)
        return row.group(0)
    body = re.sub(r'<tr class="group"[^>]*>.*?</tr>', mark_group, body, flags=re.S)
    collapsed = ' data-collapsed-default' if sid in COLLAPSED_SECTIONS else ''
    open_tag = '<section id="%s">' % sid
    prefix = prefix.replace(open_tag, '<section id="%s" class="sec"%s>' % (sid, collapsed))
    new = (f'{prefix}'
           f'<h2 class="sec-title"><button type="button" class="toggle" aria-expanded="true" aria-controls="{sid}-body">'
           f'{CHEVRON}<span>{title}</span></button><span class="sec-state">Collapsed</span></h2>{sub}'
           f'\n  <div class="sec-body" id="{sid}-body">{body}</div>\n{suffix}')
    return new, subsections


def strip_step(title):
    return re.sub(r'^\d+ · ', '', title)


def sidebar(parts, subsections, esc):
    items = []
    for pid, num, title, _blurb, sections in parts:
        links = []
        for sid, label in sections:
            subs = subsections.get(sid, [])
            sub_html = ''
            if subs:
                sub_html = ('<ul class="tree-sub">' + ''.join(
                    f'<li><a href="#{sub_id}" data-target="{sub_id}">{strip_step(t)}</a></li>' for sub_id, t in subs) + '</ul>')
            twisty = (f'<button type="button" class="tree-twisty" aria-label="Show {esc(label)} subsections" aria-expanded="false">{CHEVRON}</button>'
                      if subs else '<span class="tree-twisty-spacer"></span>')
            links.append(f'<li class="tree-sec{" has-sub" if subs else ""}" data-sec="{sid}">{twisty}'
                         f'<a href="#{sid}" data-target="{sid}">{esc(label)}</a>'
                         f'<span class="tree-dot" title="Collapsed on the page"></span>{sub_html}</li>')
        items.append(f'<li class="tree-part" data-part="{pid}"><button type="button" class="tree-part-toggle" aria-expanded="true">'
                     f'{CHEVRON}<span class="tree-part-num">{num}</span>{esc(title)}</button>'
                     f'<ul class="tree-secs">{"".join(links)}</ul></li>')
    return (
        '<aside class="sidebar" id="sidebar" aria-label="Page contents">'
        '<div class="sidebar-head"><span>Contents</span>'
        '<button type="button" class="icon-btn" id="sidebar-close" title="Hide contents ([)" aria-label="Hide contents">'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.71 6.71a.996.996 0 0 0-1.41 0L8.71 11.3a.996.996 0 0 0 0 1.41l4.59 4.59a.996.996 0 1 0 1.41-1.41L10.83 12l3.88-3.88c.39-.39.38-1.03 0-1.41"/></svg>'
        '</button></div>'
        '<div class="sidebar-actions"><button type="button" class="chip-btn" data-all="expand">Expand all</button>'
        '<button type="button" class="chip-btn" data-all="collapse">Collapse all</button>'
        '<button type="button" class="chip-btn" data-all="reset" title="Back to the recommended open/closed sections">Reset</button></div>'
        f'<nav class="tree"><ul>{"".join(items)}</ul></nav>'
        '<div class="sidebar-foot">Shortcuts: <kbd>[</kbd> toggle contents · <kbd>/</kbd> filter · <kbd>⌘K</kbd> search · <kbd>Enter</kbd> find on page</div>'
        '</aside>')


def header(logo_svg, page_tabs='', title='Guide', short_title='Guide'):
    return (
        '<header class="topbar">'
        '<button type="button" class="icon-btn" id="sidebar-open" title="Show contents ([)" aria-label="Show contents" aria-controls="sidebar">'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 18h16c.55 0 1-.45 1-1s-.45-1-1-1H4c-.55 0-1 .45-1 1s.45 1 1 1m0-5h16c.55 0 1-.45 1-1s-.45-1-1-1H4c-.55 0-1 .45-1 1s.45 1 1 1M3 7c0 .55.45 1 1 1h16c.55 0 1-.45 1-1s-.45-1-1-1H4c-.55 0-1 .45-1 1"/></svg></button>'
        f'<div class="logo">{logo_svg}</div>'
        f'<div class="topbar-title"><h1 title="{title}">{short_title}</h1>'
        f'{page_tabs}<nav class="topbar-crumb" id="crumb" aria-label="You are here"></nav></div>'
        '<span class="topbar-spacer"></span>'
        '<button id="theme-toggle" type="button">☾ Dark</button>'
        '</header>')


CSS = r'''
/* ---------- in-page pages ---------- */
.page[hidden] { display: none; }
.page-tabs { flex: none; display: flex; gap: 2px; padding: 3px; border-radius: var(--border-radius-full);
  background: var(--color-bg); border: 1px solid var(--color-border-light); }
.page-tabs a { display: flex; align-items: center; gap: 6px; padding: 4px 12px 4px 5px; border-radius: var(--border-radius-full);
  color: var(--color-text-light); font-weight: var(--font-weight-emphasis); font-size: 13px; line-height: 20px; text-decoration: none; white-space: nowrap; }
.page-tabs a:hover { background: var(--color-menu-item-hover); color: var(--color-text); }
.page-tabs a[aria-current="page"] { background: var(--color-button-primary); color: var(--color-button-primary-text); }
.page-tab-num { display: inline-grid; place-items: center; width: 20px; height: 20px; border-radius: 50%; font-size: 11px;
  background: color-mix(in srgb, currentColor 18%, transparent); }
.pager { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-lg); margin: var(--space-3xl) 0 0; padding-top: var(--space-xl); border-top: 1px solid var(--color-border-light); }
.pager a { display: flex; flex-direction: column; gap: 2px; padding: var(--space-lg) var(--space-xl); border: 1px solid var(--color-border-light); border-radius: var(--border-radius-lg);
  background: var(--color-bg-light); color: var(--color-text); text-decoration: none; box-shadow: var(--shadow-lv1); transition: border-color .15s ease, transform .15s ease; }
.pager a:hover { border-color: var(--color-link); transform: translateY(-1px); }
.pager-next { text-align: right; grid-column: 2; }
.pager-dir { font-size: 12px; font-weight: var(--font-weight-emphasis); color: var(--color-link); text-transform: uppercase; letter-spacing: .06em; }
.pager-title { font-size: 18px; font-weight: var(--font-weight-emphasis); }
.pager-blurb { font-size: 13px; color: var(--color-text-light); }
@media (max-width: 1100px) { .page-tabs a:not([aria-current]) .page-tab-label { display: none; } .page-tabs a:not([aria-current]) { padding-right: 5px; } }
@media (max-width: 760px) { .page-tabs .page-tab-label { display: none; } .page-tabs a { padding-right: 5px; } }
.tree-part.current > .tree-part-toggle { color: var(--color-text); }
.tree-part:not(.current) > .tree-part-toggle { opacity: .75; }
@media (max-width: 700px) { .pager { grid-template-columns: 1fr; } .pager-next { grid-column: 1; } }
@media print { .page[hidden] { display: block !important; } .page-tabs, .pager { display: none !important; } }

/* ---------- glossary terms ---------- */
a.gl-term { color: inherit; text-decoration: underline dotted color-mix(in srgb, var(--color-link) 70%, transparent); text-decoration-thickness: 1.5px;
  text-underline-offset: 3px; cursor: help; border-radius: 2px; }
a.gl-term:hover, a.gl-term:focus-visible, a.gl-term.gl-active { color: var(--color-link); text-decoration-style: solid; background: color-mix(in srgb, var(--color-link) 10%, transparent); outline: none; }
.gl-tip { position: fixed; z-index: calc(var(--z-fullpage) + 5); width: min(380px, calc(100vw - 16px)); padding: var(--space-md) var(--space-lg) var(--space-sm);
  background: var(--color-bg-light); color: var(--color-text); border: 1px solid var(--color-border); border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lv4, 0 12px 32px rgba(0,0,0,.35)); font-size: 13.5px; line-height: 1.55; }
.gl-tip::before { content: ""; position: absolute; left: var(--arrow-x, 24px); top: -6px; width: 10px; height: 10px; margin-left: -5px; transform: rotate(45deg);
  background: var(--color-bg-light); border-left: 1px solid var(--color-border); border-top: 1px solid var(--color-border); }
.gl-tip.above::before { top: auto; bottom: -6px; transform: rotate(225deg); }
.gl-tip.side-right::before { left: -6px; margin-left: 0; top: var(--arrow-y, 24px); margin-top: -5px; transform: rotate(-45deg); }
.gl-tip.side-left::before { left: auto; right: -6px; margin-left: 0; top: var(--arrow-y, 24px); margin-top: -5px; transform: rotate(135deg); }
.gl-tip-def a.gl-term { cursor: pointer; }
.gl-tip-head { display: flex; flex-direction: column; gap: 1px; margin-bottom: 6px; }
.gl-tip-kicker { font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--color-link); font-weight: var(--font-weight-emphasis); }
.gl-tip-term { font-size: 15px; }
.gl-tip-def code, .gl-tip-where code { font-size: 11.5px; padding: 0 3px; overflow-wrap: anywhere; }
.gl-tip-where { margin-top: 6px; font-size: 12px; color: var(--color-text-light); }
.gl-tip-where:empty { display: none; }
.gl-tip-where span { font-weight: var(--font-weight-emphasis); }
.gl-tip-link { display: inline-block; margin-top: var(--space-sm); padding-top: var(--space-sm); width: 100%; border-top: 1px solid var(--color-border-light);
  font-size: 12.5px; font-weight: var(--font-weight-emphasis); color: var(--color-link); text-decoration: none; }
.gl-tip-link:hover { text-decoration: underline; }
@media print { a.gl-term { text-decoration: none; } .gl-tip { display: none !important; } }

/* ---------- page search ---------- */
.doc-search { position: relative; flex: 0 1 320px; min-width: 170px; display: flex; align-items: center; gap: var(--space-xs); height: 36px; padding: 0 var(--space-sm);
  border: 1px solid var(--color-border-light); border-radius: var(--border-radius-md); background: var(--color-bg-light); }
.doc-search:focus-within { border-color: var(--color-button-primary); box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-button-primary) 20%, transparent); }
.doc-search > svg { width: 18px; height: 18px; fill: currentColor; opacity: .6; flex: none; }
.doc-search input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; color: inherit; font: inherit; font-size: 14px; }
.doc-search input::-webkit-search-cancel-button { cursor: pointer; }
.doc-search kbd { flex: none; font-size: 11px; opacity: .65; }
.doc-search-results { position: absolute; top: calc(100% + 6px); right: 0; width: min(560px, 92vw); max-height: min(70vh, 640px); overflow-y: auto;
  background: var(--color-bg-light); border: 1px solid var(--color-border-light); border-radius: var(--border-radius-md); box-shadow: var(--shadow-lv2, 0 8px 28px rgba(0,0,0,.25)); padding: 4px; }
.doc-search-count, .doc-search-empty { padding: 8px 10px; font-size: 12px; opacity: .7; }
.doc-search-hit { display: block; width: 100%; text-align: left; border: 0; background: transparent; color: inherit; font: inherit; padding: 8px 10px; border-radius: 6px; cursor: pointer; }
.doc-search-hit.active, .doc-search-hit:hover { background: color-mix(in srgb, var(--color-button-primary) 14%, transparent); }
.doc-search-hit .hit-top { display: flex; gap: 8px; align-items: baseline; }
.doc-search-hit .hit-kind { flex: none; font-size: 10px; text-transform: uppercase; letter-spacing: .06em; opacity: .6; min-width: 52px; }
.doc-search-hit .hit-title { font-weight: 600; font-size: 14px; }
.doc-search-hit .hit-crumb { font-size: 11px; opacity: .6; margin: 2px 0 0 60px; }
.doc-search-hit .hit-snip { font-size: 12px; opacity: .85; margin: 2px 0 0 60px; line-height: 1.4; }
.doc-search-hit .hit-snip:empty { display: none; }
.doc-search mark { background: color-mix(in srgb, #f5c400 45%, transparent); color: inherit; border-radius: 2px; padding: 0 1px; }
.find-bar { flex: none; display: flex; align-items: center; gap: 2px; }
.find-bar[hidden] { display: none; }
.find-count { font-size: 12px; font-variant-numeric: tabular-nums; opacity: .8; padding: 0 6px; white-space: nowrap; }
.doc-search.find-none .find-count { color: var(--color-text-danger, #e5484d); opacity: 1; }
.find-btn { display: grid; place-items: center; width: 26px; height: 26px; border: 0; border-radius: 6px; background: transparent; color: inherit; cursor: pointer; }
.find-btn:hover { background: color-mix(in srgb, var(--color-button-primary) 16%, transparent); }
.find-btn svg { width: 18px; height: 18px; fill: currentColor; }
.doc-search.finding kbd { display: none; }
mark.find-hit { background: color-mix(in srgb, #f5c400 40%, transparent); color: inherit; border-radius: 2px; padding: 0 1px; }
mark.find-hit.find-current { background: #f5a300; color: #111; box-shadow: 0 0 0 2px #f5a300; scroll-margin-top: 160px; }
@keyframes search-flash { 0%, 40% { background: color-mix(in srgb, #f5c400 35%, transparent); } 100% { background: transparent; } }
.search-flash { animation: search-flash 2.2s ease-out; scroll-margin-top: 140px; }
@media (max-width: 900px) { .doc-search kbd { display: none; } .doc-search { flex-basis: 200px; } }
@media print { .doc-search { display: none; } }

/* ---------- compact top bar ---------- */
header.topbar { position: sticky; top: 0; z-index: var(--z-fullpage); display: flex; align-items: center; gap: var(--space-md);
  height: 56px; padding: 0 var(--space-lg); background: var(--color-bg-light); border-bottom: 1px solid var(--color-border-light); box-shadow: var(--shadow-lv1); }
header.topbar .logo { width: 32px; height: 32px; border-radius: var(--border-radius-md); }
header.topbar .logo svg { width: 20px; height: 20px; }
.topbar-title { display: flex; align-items: center; gap: var(--space-md); min-width: 0; }
.topbar-title h1 { margin: 0; font-size: var(--font-size-body-lg); line-height: var(--line-height-body-lg); letter-spacing: 0; white-space: nowrap; }
.topbar-title { flex: 1; }
.topbar-spacer { flex: none; }
.topbar-crumb { display: flex; align-items: center; gap: var(--space-xs); min-width: 0; overflow: hidden; color: var(--color-text-light);
  font-size: var(--font-size-body-sm); white-space: nowrap; padding-left: var(--space-md); border-left: 1px solid var(--color-border-light); }
.topbar-crumb a { color: inherit; text-decoration: none; border-radius: var(--border-radius-sm); padding: 2px var(--space-xs); overflow: hidden; text-overflow: ellipsis; }
.topbar-crumb a:hover { color: var(--color-link); background: var(--color-menu-item-hover); }
.topbar-crumb a:last-child { color: var(--color-text); font-weight: var(--font-weight-emphasis); }
.topbar-crumb .sep { color: var(--color-icon-light); flex: none; }
.topbar-crumb:empty { display: none; }
@media (max-width: 1500px) { .topbar-crumb a:not(:last-child), .topbar-crumb .sep { display: none; } }
@media (max-width: 1360px) { .topbar-crumb { display: none; } }
header.topbar #theme-toggle { margin-left: var(--space-sm); align-self: center; }
.icon-btn { display: inline-grid; place-items: center; width: 32px; height: 32px; flex: none; border-radius: var(--border-radius-md);
  border: 0; background: var(--color-button-icon); color: var(--color-icon); cursor: pointer; }
.icon-btn:hover { background: var(--color-button-icon-hover); color: var(--color-icon-hover); }
.icon-btn:focus-visible, .toggle:focus-visible, .chip-btn:focus-visible, .tree a:focus-visible, .tree button:focus-visible { outline: none; box-shadow: var(--focus-glow); }
.icon-btn svg { width: 22px; height: 22px; fill: currentcolor; }
body.sidebar-open #sidebar-open { visibility: hidden; }

/* ---------- floating tree sidebar ---------- */
.sidebar { position: fixed; z-index: var(--z-dropdown); top: 68px; bottom: 12px; left: 12px; width: 272px; display: flex; flex-direction: column;
  background: var(--color-bg-light); border: 1px solid var(--color-border-light); border-radius: var(--border-radius-lg); box-shadow: var(--shadow-lv2);
  transform: translateX(calc(-100% - 24px)); transition: transform .2s var(--bezier-in); }
body.sidebar-open .sidebar { transform: none; }
.sidebar-head { display: flex; align-items: center; justify-content: space-between; padding: var(--space-sm) var(--space-sm) var(--space-xs) var(--space-lg);
  font-size: 12px; font-weight: var(--font-weight-emphasis); letter-spacing: .06em; text-transform: uppercase; color: var(--color-text-light); }
.sidebar-actions { display: flex; gap: var(--space-xs); padding: 0 var(--space-md) var(--space-sm); border-bottom: 1px solid var(--color-border-light); }
.chip-btn { font: inherit; font-size: 12px; font-weight: var(--font-weight-emphasis); color: var(--color-text); cursor: pointer;
  background: var(--color-tag-default); border: 0; border-radius: var(--border-radius-full); padding: 2px var(--space-sm); }
.chip-btn:hover { background: var(--color-tag-default-hover); }
.tree { flex: 1; overflow-y: auto; padding: var(--space-sm) var(--space-sm) var(--space-md); }
.tree ul { list-style: none; margin: 0; padding: 0; }
.tree .chev { width: 16px; height: 16px; fill: currentcolor; transition: transform .15s; flex: none; }
.tree-part { margin-bottom: var(--space-xs); }
.tree-part-toggle { display: flex; align-items: center; gap: var(--space-xs); width: 100%; font: inherit; font-size: 12px; font-weight: var(--font-weight-emphasis);
  text-transform: uppercase; letter-spacing: .06em; color: var(--color-text-light); background: none; border: 0; cursor: pointer;
  padding: var(--space-xs) var(--space-xs); border-radius: var(--border-radius-sm); text-align: left; }
.tree-part-toggle:hover { color: var(--color-text); background: var(--color-menu-item-hover); }
.tree-part-toggle[aria-expanded="true"] .chev, .tree-twisty[aria-expanded="true"] .chev { transform: rotate(90deg); }
.tree-part-num { display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: var(--border-radius-full);
  background: var(--guide-brand); color: var(--hex-white); font-size: 11px; letter-spacing: 0; }
.tree-part-toggle[aria-expanded="false"] + .tree-secs { display: none; }
.tree-sec { display: grid; grid-template-columns: 20px 1fr auto; align-items: center; }
.tree-twisty, .tree-twisty-spacer { width: 20px; height: 28px; display: grid; place-items: center; background: none; border: 0; padding: 0; color: var(--color-icon); cursor: pointer; }
.tree-twisty:hover { color: var(--color-text); }
.tree a { display: block; color: var(--color-nav-item-inactive-text); text-decoration: none; font-size: var(--font-size-body-sm);
  padding: var(--space-xs) var(--space-sm); border-radius: var(--border-radius-md); line-height: 18px; }
.tree a:hover { color: var(--color-nav-item-inactive-text-hover); background: var(--color-menu-item-hover); }
.tree a.active { color: var(--color-nav-item-active-text); background: var(--color-nav-item-active-bg); font-weight: var(--font-weight-emphasis); }
.tree-sub { grid-column: 2 / 4; display: none; border-left: 1px solid var(--color-border); margin: 2px 0 var(--space-xs) var(--space-sm); padding-left: var(--space-xs) !important; }
.tree-sec.open .tree-sub { display: block; }
.tree-sub a { font-size: 12.5px; padding-top: 3px; padding-bottom: 3px; color: var(--color-text-light); }
.tree-dot { width: 6px; height: 6px; border-radius: var(--border-radius-full); background: transparent; margin-right: var(--space-xs); }
.tree-sec.is-collapsed > .tree-dot { background: var(--color-icon-light); }
.tree mark { background: var(--color-yellow-bg); color: inherit; border-radius: 2px; }
.tree-filter { margin: var(--space-md) var(--space-md) var(--space-sm); }
.tree-filter input { width: 100%; font: inherit; font-size: var(--font-size-body-sm); color: var(--color-text); background: var(--color-input-bg);
  border: 1px solid var(--color-input-border); border-radius: var(--border-radius-md); padding: 6px var(--space-sm); }
.tree-filter input:focus { outline: none; border-color: var(--color-input-border-focus); box-shadow: var(--focus-glow); }
.tree li.filtered-out { display: none; }
.sidebar-foot { padding: var(--space-sm) var(--space-lg); border-top: 1px solid var(--color-border-light); font-size: 12px; color: var(--color-text-light); }
kbd { font: 11px ui-monospace, SFMono-Regular, Menlo, monospace; padding: 0 4px; border: 1px solid var(--color-border); border-radius: var(--border-radius-sm); background: var(--color-bg); }

@media (min-width: 1180px) {
  body.sidebar-open main { margin-left: 296px; }
  main { transition: margin-left .2s var(--bezier-in); }
}
@media (max-width: 1179px) {
  .sidebar { top: 64px; left: 8px; bottom: 8px; }
  body.sidebar-open::after { content: ""; position: fixed; inset: 56px 0 0 0; background: hsl(0 0% 0% / 25%); z-index: calc(var(--z-dropdown) - 1); }
  .topbar-title h1 { display: none; }
  .topbar-crumb { border-left: 0; padding-left: 0; }
}

/* ---------- collapsible sections ---------- */
section, .part { scroll-margin-top: 64px; }
.subsec { scroll-margin-top: 112px; }
h2.sec-title { display: flex; align-items: center; gap: var(--space-sm); position: sticky; top: 56px; z-index: 6;
  margin: 0 -12px; padding: var(--space-sm) 12px; background: var(--color-bg); }
h2.sec-title.stuck { box-shadow: 0 1px 0 var(--color-border-light), 0 6px 8px -8px hsl(0 0% 0% / 25%); }
h3.subsec-title { position: sticky; top: 104px; z-index: 5; margin-left: -12px; margin-right: -12px; padding: var(--space-xs) 12px;
  background: var(--color-bg); }
h3.subsec-title.stuck { box-shadow: 0 1px 0 var(--color-border-light); }
.sec.collapsed > h2.sec-title, .subsec.collapsed > h3.subsec-title { position: static; box-shadow: none; }
.toggle { display: inline-flex; align-items: center; gap: var(--space-xs); font: inherit; color: inherit; background: none; border: 0;
  padding: 0 var(--space-xs) 0 0; margin-left: -28px; cursor: pointer; text-align: left; border-radius: var(--border-radius-md); }
.toggle .chev { width: 24px; height: 24px; fill: var(--color-icon); transition: transform .15s; flex: none; }
.toggle[aria-expanded="true"] .chev { transform: rotate(90deg); }
.toggle:hover .chev { fill: var(--color-link); }
.toggle:hover span { color: var(--color-link); }
.sec-state { display: none; font-size: 12px; font-weight: var(--font-weight-emphasis); color: var(--color-text-light); background: var(--color-tag-default);
  border-radius: var(--border-radius-full); padding: 0 var(--space-sm); line-height: 20px; letter-spacing: 0; }
.sec.collapsed .sec-state { display: inline-block; }
.sec.collapsed > .sec-body, .subsec.collapsed > .subsec-body { display: none; }
.sec.collapsed { padding-bottom: var(--space-xs); }
h3.subsec-title { margin-top: var(--space-lg); }
.subsec-title .toggle { margin-left: -24px; }
.subsec-title .toggle .chev { width: 20px; height: 20px; }
.subsec.collapsed > .subsec-title { opacity: .85; }
tr.group[data-toggleable] td { cursor: pointer; user-select: none; }
tr.group .group-chev { margin-left: auto; flex: none; width: 20px; height: 20px; fill: var(--color-icon); transition: transform .15s; transform: rotate(90deg); }
tr.group.collapsed .group-chev { transform: none; }
.group-line { display: flex; align-items: center; gap: var(--space-md); min-width: 0; }
.group-label { flex: none; white-space: nowrap; }
.stack { table-layout: fixed; }
.group-preview { display: none; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; font-size: var(--font-size-body-sm); font-weight: var(--font-weight-regular); color: var(--color-text-light); }
.group-preview b { font-weight: var(--font-weight-emphasis); color: var(--color-text-light); margin-right: var(--space-xs); }
tr.group.collapsed .group-preview { display: block; }
tr.group.collapsed:hover td { filter: brightness(.98); }
tr.row-hidden { display: none; }
table td code { overflow-wrap: anywhere; word-break: break-word; }
/* ---------- screenshots ---------- */
.shot-thumb { position: relative; display: block; width: 100%; padding: 0; border: 1px solid var(--color-border); border-radius: var(--border-radius-md);
  overflow: hidden; background: var(--color-bg); cursor: zoom-in; line-height: 0; }
.shot-thumb img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; object-position: top left; }
.shot-thumb:hover { border-color: var(--color-link); box-shadow: var(--focus-glow); }
.shot-more { position: absolute; right: 4px; bottom: 4px; line-height: 16px; font-size: 11px; font-weight: var(--font-weight-emphasis);
  background: var(--color-toast-bg); color: var(--color-toast-text); border-radius: var(--border-radius-full); padding: 0 6px; }
td.shot-none { font-size: 12px; color: var(--color-text-light); }
.gallery-jump { display: flex; flex-wrap: wrap; gap: var(--space-xs); margin: var(--space-md) 0 var(--space-lg); }
.gallery-jump a { display: inline-flex; align-items: center; gap: 6px; padding: 4px 6px 4px 10px; border-radius: var(--border-radius-full);
  background: var(--k-bg); color: var(--k-fg); font-size: 13px; font-weight: var(--font-weight-emphasis); text-decoration: none; }
.gallery-jump a:hover { box-shadow: inset 0 0 0 1px var(--k); }
.gallery-jump svg { width: 16px; height: 16px; fill: currentColor; }
.gallery-jump b { min-width: 20px; padding: 0 6px; line-height: 18px; border-radius: var(--border-radius-full); text-align: center;
  background: var(--k); color: var(--color-bg-light); font-size: 11px; }
.gallery-group { margin: 0 0 var(--space-xl); scroll-margin-top: 150px; }
.gallery-head { display: flex; align-items: center; gap: var(--space-md); padding: var(--space-sm) var(--space-md); margin-bottom: var(--space-md);
  border-radius: var(--border-radius-lg); border-left: 4px solid var(--k);
  background: linear-gradient(90deg, color-mix(in srgb, var(--k) 16%, var(--color-bg-light)), var(--color-bg-light) 70%); }
.gallery-icon { width: 36px; height: 36px; flex: none; display: grid; place-items: center; border-radius: var(--border-radius-md); background: var(--k); }
.gallery-icon svg { width: 22px; height: 22px; fill: var(--color-bg-light); }
.gallery-head-text { flex: 1; min-width: 0; }
.gallery-head h4 { margin: 0; font-size: var(--font-size-heading-sm, 18px); line-height: 1.3; font-weight: var(--font-weight-emphasis); color: var(--color-text); }
.gallery-head p { margin: 2px 0 0; font-size: 13px; color: var(--color-text-light); }
.gallery-count { flex: none; font-size: 12px; font-weight: var(--font-weight-emphasis); color: var(--k-fg); background: var(--k-bg);
  padding: 2px 10px; border-radius: var(--border-radius-full); }
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-lg); }
.shot-card { margin: 0; background: var(--color-bg-light); border: 1px solid var(--color-border-light); border-radius: var(--border-radius-lg);
  overflow: hidden; box-shadow: var(--shadow-lv1); }
.shot-card { transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease; }
.shot-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lv2); border-color: var(--k, var(--color-link)); }
.shot-card button { position: relative; display: block; width: 100%; padding: 0; border: 0; background: var(--color-bg); cursor: zoom-in; line-height: 0;
  border-bottom: 1px solid var(--color-border-light); }
.shot-card code.shot-route-chip { position: absolute; left: 8px; bottom: 8px; max-width: calc(100% - 16px); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  line-height: 18px; font-size: 11px; padding: 1px 6px; border: 0; border-radius: var(--border-radius-sm, 4px); background: hsl(0 0% 0% / 72%); color: #fff; }
.shot-card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; object-position: top left; }
.shot-card button:hover img { opacity: .9; }
.shot-card figcaption { display: flex; flex-direction: column; gap: 2px; padding: var(--space-sm) var(--space-md) var(--space-md); }
.shot-card figcaption b { font-size: 14px; }
.shot-card figcaption .shot-note-line { font-size: 12px; color: var(--color-text-light); }
.shot-modal { position: fixed; inset: 0; z-index: var(--z-modal); display: flex; flex-direction: column; background: hsl(0 0% 0% / 85%); }
.shot-modal[hidden] { display: none; }
.shot-bar { display: flex; align-items: center; gap: var(--space-sm); padding: var(--space-sm) var(--space-lg); background: var(--color-bg-light); flex-wrap: wrap; }
.shot-title { font-weight: var(--font-weight-emphasis); }
.shot-note, .shot-count { color: var(--color-text-light); font-size: var(--font-size-body-sm); }
.shot-bar button { font: inherit; font-size: var(--font-size-body-sm); cursor: pointer; color: var(--color-text); background: var(--color-button-default);
  border: 1px solid var(--color-button-default-border); border-radius: var(--border-radius-md); padding: var(--space-xs) var(--space-md); }
.shot-bar .shot-close { background: var(--color-button-primary); color: var(--color-button-primary-text); border-color: transparent; }
.shot-stage { flex: 1; overflow: auto; display: grid; place-items: center; padding: var(--space-lg); }
.shot-stage img { max-width: 100%; max-height: calc(100vh - 110px); box-shadow: var(--shadow-lv4); border-radius: var(--border-radius-md); cursor: zoom-in; }
.shot-stage img.actual { max-width: none; max-height: none; cursor: zoom-out; }
@media print { .shot-modal { display: none !important; } }

/* ---------- site map tree ---------- */
.sitemap { background: var(--color-bg-light); border: 1px solid var(--color-border-light); border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lv1); padding: var(--space-md) var(--space-lg); font-size: var(--font-size-body-sm); }
.sitemap details { margin-left: var(--space-lg); border-left: 1px solid var(--color-border); padding-left: var(--space-md); }
.sitemap > details { margin-left: 0; border-left: 0; padding-left: 0; }
.sitemap summary { cursor: pointer; padding: 3px var(--space-xs); border-radius: var(--border-radius-sm); list-style: none; display: flex; gap: var(--space-sm); align-items: center; flex-wrap: wrap; }
.sitemap summary::-webkit-details-marker { display: none; }
.sitemap summary::before { content: "▸"; color: var(--color-icon); width: 10px; transition: transform .15s; display: inline-block; }
.sitemap details[open] > summary::before { transform: rotate(90deg); }
.sitemap details:not(:has(> ul, > details)) > summary::before { content: "•"; transform: none; }
.sitemap summary:hover { background: var(--color-menu-item-hover); }
.sitemap summary > span, .sitemap li > span { color: var(--color-text-light); }
.sitemap ul { list-style: none; margin: 2px 0 var(--space-xs) var(--space-lg); padding-left: var(--space-md); border-left: 1px dashed var(--color-border); }
.sitemap li { padding: 2px 0; line-height: 1.6; }
.sitemap li span { margin-left: var(--space-xs); }
@media (max-width: 900px) { .toggle { margin-left: 0; } }

@media print {
  h2.sec-title, h3.subsec-title { position: static !important; box-shadow: none !important; }
  .sidebar, #sidebar-open, #theme-toggle, .dg-expand, .dg-scroll-hint { display: none !important; }
  .sec.collapsed > .sec-body, .subsec.collapsed > .subsec-body { display: block !important; }
  tr.row-hidden { display: table-row !important; }
  body.sidebar-open main { margin-left: auto; }
}
'''
