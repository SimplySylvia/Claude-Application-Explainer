#!/usr/bin/env python3
"""Capture the README screenshots of the built demo with headless Chrome.

    python3 capture.py docs/demo out_dir/

Main guide: guide-engineering.png (light theme), guide-glossary.png and guide-search.png (dark theme), and three shots
of the Express deep dive on its Topics page: guide-topic.png, guide-topic-code.png and guide-topic-link.png. Hub:
hub.png (with "Continue reading"), hub-search.png (dark) and hub-table.png (a topic guide's sections previewed), plus
guide-menu.png, the PostgreSQL topic guide with its Guides menu open. All at 1800px wide.
Each shot is a copy of a page, written beside it in a temporary copy of the demo so relative links and the hub's
nav.js still load, with a small script that sets up the view on load. Headless Chrome renders blank once a page has
scrolled, so guide shots switch pages by clicking the header tab instead of using a URL hash, and FOCUS brings a
section to the top by hiding what comes before it instead of scrolling.
"""
import json, os, shutil, subprocess, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                                'skills', 'application-explainer', 'scripts'))
from qa_check import chrome  # noqa: E402

MAIN = 'shopfront-guide/shopfront-guide.html'
TOPIC = 'shopfront-postgresql-guide/shopfront-postgresql-guide.html'
HUB = 'shopfront-guides/index.html'
LIGHT = "if (document.documentElement.getAttribute('data-theme') !== 'light') document.getElementById('theme-toggle').click();"
DARK = "if (document.documentElement.getAttribute('data-theme') === 'light') document.getElementById('theme-toggle').click();"
# Hide everything before element `id` inside <main>, so it renders at the top of the viewport without scrolling.
FOCUS = ("function focusOn(id) { var el = document.getElementById(id); var main = document.querySelector('main');"
         " for (var n = el; n && n !== main; n = n.parentElement) for (var s = n.previousElementSibling; s; s = s.previousElementSibling)"
         " s.style.display = 'none'; }")
SEARCH = ("var i = document.querySelector('{sel}'); i.focus(); i.value = '{q}';"
          "i.dispatchEvent(new Event('input', {{bubbles: true}}));")
# "Continue reading" on the hub, as if the reader had been in both guides.
RECENT = [
    {'g': 'shopfront-postgresql-guide', 'title': 'PostgreSQL in Shopfront', 'trail': ['Guided walkthrough'],
     'href': '../' + TOPIC + '#postgresql-walkthrough', 'ago': 12},
    {'g': 'shopfront-guide', 'title': 'Shopfront Guide', 'trail': ['Architecture'], 'href': '../' + MAIN + '#arch', 'ago': 180},
]
SEED = ("<script>try { localStorage.setItem('shopfront-guides-recent', JSON.stringify(%s.map(function (e) {"
        " e.t = Date.now() - e.ago * 60000; return e; }))); } catch (e) {}</script>" % json.dumps(RECENT))
SHOTS = {  # file name: (page, header tab to open or None, setup script)
    'guide-engineering': (MAIN, 'engineering', LIGHT),
    'guide-glossary': (MAIN, 'product', DARK + "document.querySelector('main .page:not([hidden]) a.gl-term')"
                                               ".dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));"),
    'guide-search': (MAIN, 'product', DARK + SEARCH.format(sel='.doc-search input', q='order')),
    'guide-topic': (MAIN, 'topics', LIGHT),
    'guide-topic-code': (MAIN, 'topics', DARK + FOCUS + "focusOn('express-concepts--concepts-in-code');"),
    'guide-topic-link': (MAIN, 'engineering', LIGHT + FOCUS + "focusOn('stack');"
                         "document.querySelectorAll('#stack tr.group').forEach(function (r) {"
                         " if (/Backend/.test(r.textContent) && r.classList.contains('collapsed')) r.click(); });"),
    'guide-menu': (TOPIC, 'in-app', LIGHT + "document.querySelector('.gnav-btn').click();"),
    'hub': (HUB, None, LIGHT),
    'hub-search': (HUB, None, DARK + SEARCH.format(sel='#q', q='walkthrough')),
    'hub-table': (HUB, None, LIGHT + "document.querySelector('.hero').style.display = 'none';"
                  "document.getElementById('continue').style.display = 'none';"
                  "document.querySelector('[aria-labelledby=h-start]').style.display = 'none';"
                  "document.querySelector('#guides .expand').click();"),
}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    demo, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for folder in {p.split('/')[0] for p in (MAIN, TOPIC, HUB)}:
            shutil.copytree(os.path.join(demo, folder), os.path.join(tmp, folder))
        for name, (page, tab, setup) in SHOTS.items():
            src = os.path.join(tmp, page)
            open_tab = f"document.querySelector('.page-tabs a[data-page={tab}]').click(); window.scrollTo(0, 0);" if tab else ''
            script = ("<script>window.addEventListener('load', function () {"
                      f"{open_tab} setTimeout(function () {{ {setup} }}, 400); }});</script>")
            doc = open(src, encoding='utf-8').read().replace('<head>', '<head>' + SEED, 1)
            path = os.path.join(os.path.dirname(src), f'_shot-{name}.html')
            open(path, 'w', encoding='utf-8').write(doc.replace('</body>', script + '</body>'))
            png = os.path.join(out, f'{name}.png')
            subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1.25',
                            '--virtual-time-budget=4000', '--window-size=1440,900', f'--screenshot={png}', f'file://{path}'],
                           check=True, capture_output=True)
            print('wrote', png)


if __name__ == '__main__':
    main()
