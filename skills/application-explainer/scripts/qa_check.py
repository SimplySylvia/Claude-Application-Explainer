#!/usr/bin/env python3
"""Headless checks for a built guide (needs Google Chrome).

    python3 qa_check.py path/to/guide.html [--screenshot out.png]

Reports JS errors, broken in-page links, images that failed to load, page/section counts, glossary links,
diagram count, and runs a navigation test (page tabs, sidebar link, search result, glossary jump, back button).
A second pass at 1280x800 checks that diagrams too wide for a laptop window show their scroll hint.
Exit code 1 if anything failed.
"""
import html, json, os, re, subprocess, sys, tempfile

CHROME_CANDIDATES = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'google-chrome', 'chromium', 'chromium-browser']

PROBE = r'''<script>
(function(){
var o={errors:window.__e,fails:[]};
function fail(m){o.fails.push(m)}
var q=[];function then(f,ms){q.push([f,ms||300])}
function done(){var p=document.createElement('pre');p.id='QA_OUT';p.textContent=JSON.stringify(o);document.body.appendChild(p)}
function run(){if(!q.length){done();return}var t=q.shift();try{t[0]()}catch(err){fail('probe: '+err.message)}setTimeout(run,t[1])}
function visible(){return [].filter.call(document.querySelectorAll('main .page'),function(p){return !p.hidden}).map(function(p){return p.dataset.page})}
then(function(){
  o.pages=document.querySelectorAll('main .page').length;
  o.sections=document.querySelectorAll('section.sec').length;
  o.diagrams=document.querySelectorAll('svg.dg').length;
  o.glossaryTerms=document.querySelectorAll('#glossary tr[id^="gl-"]').length;
  o.glossaryLinks=document.querySelectorAll('a.gl-term').length;
  o.images=document.querySelectorAll('img[data-shot]').length;
  o.badImages=[].filter.call(document.querySelectorAll('img[data-shot]'),function(i){return !i.src||i.src.indexOf('data:image')!==0}).length;
  var ids={};document.querySelectorAll('[id]').forEach(function(e){ids[e.id]=1});
  o.brokenLinks=[].map.call(document.querySelectorAll('a[href^="#"]'),function(a){return a.getAttribute('href').slice(1)}).filter(function(id){return id&&!ids[decodeURIComponent(id)]}).filter(function(v,i,a){return a.indexOf(v)===i});
  o.todos=(document.querySelector('main').textContent.match(/\bTODO\b/g)||[]).length;
  if(o.pages<1)fail('no pages');
  if(visible().length!==1)fail('expected exactly one visible page, got '+visible().length);
});
then(function(){var tabs=document.querySelectorAll('.page-tabs a');var last=tabs[tabs.length-1];last.click()});
then(function(){var tabs=document.querySelectorAll('.page-tabs a');if(visible()[0]!==tabs[tabs.length-1].dataset.page)fail('page tab did not switch pages')});
then(function(){var a=document.querySelector('#sidebar a[data-target]');o.sidebarTarget=a&&a.getAttribute('data-target');if(a)a.click()});
then(function(){var t=document.getElementById(o.sidebarTarget);if(t&&t.closest('.page').hidden)fail('sidebar link landed on a hidden page')});
then(function(){history.back()},400);
then(function(){o.afterBack=visible()[0]});
then(function(){var i=document.querySelector('.doc-search input');var w=(document.querySelector('section.sec .sec-title .toggle span')||{}).textContent||'the';i.focus();i.value=w.split(' ')[0];i.dispatchEvent(new Event('input'))});
then(function(){var h=document.querySelectorAll('.doc-search-hit');o.searchHits=h.length;if(!h.length)fail('search returned nothing');else h[h.length-1].click()});
then(function(){var c=document.querySelector('mark.find-current');if(o.searchHits&&!c)fail('search pick did not highlight a match');document.querySelector('.doc-search input').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))});
then(function(){var a=document.querySelector('main a.gl-term');if(a){o.glossaryJump=a._gl&&a._gl.term;a.click()}});
then(function(){if(o.glossaryJump){var f=document.querySelector('#glossary .search-flash');if(!f)fail('glossary link did not reveal its row')}});
setTimeout(run,1500);
})();
</script>'''


# Second pass at a laptop-sized window: every diagram that overflows its box must show the scroll hint.
NARROW = (1280, 800)
NARROW_PROBE = r'''<script>
(function(){
var o={overflowing:[],unhinted:[]};
var tabs=[].slice.call(document.querySelectorAll('.page-tabs a')),i=0;
function step(){
  document.querySelectorAll('main .page:not([hidden]) .diagram').forEach(function(d){
    var name=(d.querySelector('svg.dg')||{getAttribute:function(){return '?'}}).getAttribute('aria-label');
    if(d.scrollWidth>d.clientWidth+1){o.overflowing.push(name);if(!d.classList.contains('dg-overflow'))o.unhinted.push(name)}
  });
  if(i<tabs.length){tabs[i++].click();setTimeout(step,300)}
  else{var p=document.createElement('pre');p.id='QA_OUT';p.textContent=JSON.stringify(o);document.body.appendChild(p)}
}
setTimeout(step,1000);
})();
</script>'''


def probe(doc, src, script, size, budget):
    """Run one probe script in headless Chrome against a copy of the guide and return its JSON result (or None)."""
    tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, dir=os.path.dirname(src), prefix='.qa-')
    tmp.write(doc.replace('</body>', script + '</body>')); tmp.close()
    try:
        out = subprocess.run([chrome(), '--headless=new', '--disable-gpu', f'--virtual-time-budget={budget}',
                              f'--window-size={size[0]},{size[1]}', '--dump-dom', 'file://' + tmp.name],
                             capture_output=True, text=True, timeout=180).stdout
    finally:
        os.unlink(tmp.name)
    m = re.search(r'<pre id="QA_OUT">(.*?)</pre>', out, re.S)
    return json.loads(html.unescape(m.group(1))) if m else None


def chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c) or subprocess.run(['which', c], capture_output=True).returncode == 0:
            return c
    sys.exit('Google Chrome not found')


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = os.path.abspath(sys.argv[1])
    doc = open(src, encoding='utf-8').read()
    pre = "<script>window.__e=[];window.addEventListener('error',function(e){window.__e.push(e.message+' @'+e.lineno)});try{localStorage.clear()}catch(e){}</script>"
    doc = doc.replace('<style>', pre + '<style>', 1).replace("behavior: 'smooth'", "behavior: 'auto'")
    r = probe(doc, src, PROBE, (1440, 900), 20000)
    if r is None:
        sys.exit('QA probe produced no output (page crashed or took too long)')
    narrow = probe(doc, src, NARROW_PROBE, NARROW, 8000) or {'overflowing': [], 'unhinted': ['(narrow probe produced no output)']}
    if '--screenshot' in sys.argv:
        shot = os.path.abspath(sys.argv[sys.argv.index('--screenshot') + 1])
        subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--virtual-time-budget=6000', '--window-size=1440,900',
                        f'--screenshot={shot}', 'file://' + src], capture_output=True, timeout=120)
        print('screenshot:', shot, '(headless Chrome renders blank if the page is scrolled; screenshots show the top of page 1)')
    for k in ('pages', 'sections', 'diagrams', 'images', 'badImages', 'glossaryTerms', 'glossaryLinks', 'searchHits', 'todos'):
        print(f'{k:15} {r.get(k)}')
    print(f'{"narrowOverflow":15} {len(narrow["overflowing"])} of the diagrams scroll sideways at {NARROW[0]}x{NARROW[1]}')
    problems = list(r['fails']) + [f'JS error: {e}' for e in r['errors']] + [f'broken link #{b}' for b in r['brokenLinks']]
    problems += [f'diagram {n!r} overflows at {NARROW[0]}px without the scroll hint' for n in narrow['unhinted']]
    if r.get('badImages'):
        problems.append(f'{r["badImages"]} screenshot(s) did not load')
    for p in problems:
        print('FAIL', p)
    if r.get('todos'):
        print(f'NOTE {r["todos"]} TODO placeholder(s) remain in the content')
    print('PASS' if not problems else f'{len(problems)} problem(s)')
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
