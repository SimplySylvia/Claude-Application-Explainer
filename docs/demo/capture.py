#!/usr/bin/env python3
"""Capture the README screenshots of a built guide with headless Chrome.

    python3 capture.py path/to/guide.html out_dir/

Writes guide-engineering.png (light theme), guide-glossary.png and guide-search.png (dark theme), and three shots of
the Topics page's Express deep dive (topic explainer): guide-topic.png, guide-topic-code.png, and guide-topic-link.png, at 1800px wide.
Each shot is a copy of the guide with a small script that sets up the view on load. Headless Chrome renders blank
once a page has scrolled, so the script switches pages by clicking the header tab instead of using a URL hash, and
FOCUS brings a section to the top by hiding what comes before it instead of scrolling.
"""
import os, subprocess, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..',
                                'skills', 'application-explainer', 'scripts'))
from qa_check import chrome  # noqa: E402

LIGHT = "if (document.documentElement.getAttribute('data-theme') !== 'light') document.getElementById('theme-toggle').click();"
DARK = "if (document.documentElement.getAttribute('data-theme') === 'light') document.getElementById('theme-toggle').click();"
# Hide everything before element `id` inside <main>, so it renders at the top of the viewport without scrolling.
FOCUS = ("function focusOn(id) { var el = document.getElementById(id); var main = document.querySelector('main');"
         " for (var n = el; n && n !== main; n = n.parentElement) for (var s = n.previousElementSibling; s; s = s.previousElementSibling)"
         " s.style.display = 'none'; }")
SHOTS = {  # name: (page, setup script)
    'engineering': ('engineering', LIGHT),
    'glossary': ('product', DARK + "document.querySelector('main .page:not([hidden]) a.gl-term')"
                                   ".dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));"),
    'search': ('product', DARK + "var i = document.querySelector('.doc-search input'); i.focus(); i.value = 'order';"
                                 "i.dispatchEvent(new Event('input', {bubbles: true}));"),
    'topic': ('topics', LIGHT),
    'topic-code': ('topics', DARK + FOCUS + "focusOn('express-concepts--concepts-in-code');"),
    'topic-link': ('engineering', LIGHT + FOCUS + "focusOn('stack');"
                                  "document.querySelectorAll('#stack tr.group').forEach(function (r) {"
                                  " if (/Backend/.test(r.textContent) && r.classList.contains('collapsed')) r.click(); });"),
}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    doc = open(src, encoding='utf-8').read()
    with tempfile.TemporaryDirectory() as tmp:
        for name, (page, setup) in SHOTS.items():
            script = ("<script>window.addEventListener('load', function () {"
                      f"document.querySelector('.page-tabs a[data-page={page}]').click(); window.scrollTo(0, 0);"
                      f"setTimeout(function () {{ {setup} }}, 300); }});</script>")
            path = os.path.join(tmp, name + '.html')
            open(path, 'w', encoding='utf-8').write(doc.replace('</body>', script + '</body>'))
            png = os.path.join(out, f'guide-{name}.png')
            subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1.25',
                            '--virtual-time-budget=4000', '--window-size=1440,900', f'--screenshot={png}', f'file://{path}'],
                           check=True, capture_output=True)
            print('wrote', png)


if __name__ == '__main__':
    main()
