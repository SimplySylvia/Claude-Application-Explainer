/* Shared navigation for every guide connected to a hub. The hub's build.py writes nav.js from this file, replacing
   __MANIFEST__. Each guide loads <hub>/nav.js (from HUB_URL); without it the guide keeps its plain "All guides" link. */
(function () {
  var MANIFEST = __MANIFEST__;
  var RECENT_KEY = MANIFEST.recentKey, THEME_KEY = MANIFEST.themeKey, MAX_RECENT = 8;
  var script = document.currentScript;
  var hubBase = script ? script.src.replace(/[^/]*$/, '') : '';
  var hubUrl = hubBase + MANIFEST.hub;

  var path = decodeURIComponent(location.pathname);
  var here = MANIFEST.guides.filter(function (g) { return path.indexOf('/' + g.folder + '/') >= 0; })[0];
  var file = path.split('/').pop();

  function plain(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }
  function store(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* storage unavailable */ } }
  function load(key) { try { return JSON.parse(localStorage.getItem(key)) || []; } catch (e) { return []; } }

  var css = document.createElement('style');
  css.textContent =
    '.gnav { position: relative; flex: none; }' +
    '.gnav-btn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px 5px 12px; border-radius: var(--border-radius-full); cursor: pointer;' +
    '  border: 1px solid var(--color-button-default-border); background: var(--color-button-default); color: var(--color-text); font: inherit;' +
    '  font-size: var(--font-size-body-sm); font-weight: var(--font-weight-emphasis); white-space: nowrap; }' +
    '.gnav-btn:hover { background: var(--color-button-default-hover); }' +
    '.gnav-btn svg { width: 14px; height: 14px; fill: currentcolor; }' +
    '.gnav-btn .chev-d { width: 18px; height: 18px; transition: transform .15s; }' +
    '.gnav-btn[aria-expanded="true"] .chev-d { transform: rotate(180deg); }' +
    '.gnav-menu { position: absolute; right: 0; top: calc(100% + 6px); z-index: 1000; min-width: 280px; max-height: 70vh; overflow: auto; padding: 6px;' +
    '  border-radius: var(--border-radius-lg); border: 1px solid var(--color-border-light); background: var(--color-bg-light); box-shadow: var(--shadow-lv3); }' +
    '.gnav-menu[hidden] { display: none; }' +
    '.gnav-menu ul { list-style: none; margin: 0; padding: 0; }' +
    '.gnav-menu a { display: block; padding: 8px 12px; border-radius: var(--border-radius-md); color: var(--color-text); text-decoration: none; font-size: var(--font-size-body-sm); }' +
    '.gnav-menu a:hover, .gnav-menu a:focus-visible { background: var(--color-menu-item-hover); outline: none; }' +
    '.gnav-menu a[aria-current="page"] { font-weight: var(--font-weight-emphasis); color: var(--color-link); }' +
    '.gnav-menu a[aria-current="page"]::after { content: " · you are here"; font-weight: var(--font-weight-regular); color: var(--color-text-light); }' +
    '.gnav-menu .gnav-home { font-weight: var(--font-weight-emphasis); }' +
    '.gnav-dot { display: inline-block; width: 9px; height: 9px; margin-right: 9px; border-radius: 3px; vertical-align: 0; }' +
    '.gnav-menu a[aria-current="page"] { background: var(--color-menu-item-hover); }' +
    '.gnav-menu .gnav-label { padding: 8px 12px 2px; font-size: 11px; font-weight: var(--font-weight-emphasis); text-transform: uppercase; letter-spacing: .05em; color: var(--color-text-light); }' +
    '.gnav-menu hr { border: 0; border-top: 1px solid var(--color-border-light); margin: 6px 0; }' +
    '.doc-search-all { display: block; margin: 6px; padding: 10px 12px; border-radius: var(--border-radius-md); border: 1px dashed var(--color-border);' +
    '  color: var(--color-link); font-weight: var(--font-weight-emphasis); font-size: var(--font-size-body-sm); text-decoration: none; }' +
    '.doc-search-all:hover, .doc-search-all:focus-visible { background: var(--color-menu-item-hover); outline: none; }';
  document.head.appendChild(css);

  // ---------------------------------------------------------------- guide switcher (disclosure pattern)
  function switcher() {
    var link = document.querySelector('header .hub-link');
    if (!link) return;
    var wrap = document.createElement('div');
    wrap.className = 'gnav';
    var group = function (label, kind) {
      var gs = MANIFEST.guides.filter(function (g) { return g.kind === kind; });
      return gs.length ? '<div class="gnav-label">' + label + '</div><ul>' + gs.map(item).join('') + '</ul>' : '';
    };
    var item = function (g) {
      return '<li><a href="' + new URL(g.href, hubBase).href + '"' + (g === here ? ' aria-current="page"' : '') + '><span class="gnav-dot" style="background:' + g.color + '"></span>' + plain(g.title) + '</a></li>';
    };
    wrap.innerHTML =
      '<button type="button" class="gnav-btn" aria-expanded="false" aria-controls="gnav-menu" aria-label="Guides">' + link.querySelector('svg').outerHTML + '<span class="gnav-btn-text">Guides</span>' +
      '<svg class="chev-d" viewBox="0 0 24 24" aria-hidden="true"><path d="M8.12 9.29 12 13.17l3.88-3.88a.996.996 0 1 1 1.41 1.41l-4.59 4.59a.996.996 0 0 1-1.41 0L6.7 10.7a.996.996 0 0 1 0-1.41c.39-.38 1.03-.39 1.42 0"/></svg></button>' +
      '<nav class="gnav-menu" id="gnav-menu" aria-label="' + plain(MANIFEST.title) + '" hidden>' +
      '<ul><li><a class="gnav-home" href="' + hubUrl + '">All guides &amp; search</a></li></ul><hr>' +
      group('Start here', 'app') + group('Topic guides', 'topic') + '</nav>';
    link.replaceWith(wrap);
    var btn = wrap.querySelector('button'), menu = wrap.querySelector('nav');
    function set(open, refocus) {
      btn.setAttribute('aria-expanded', open);
      menu.hidden = !open;
      if (!open && refocus) btn.focus();
    }
    btn.addEventListener('click', function () { set(menu.hidden); });
    wrap.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) { e.stopPropagation(); set(false, true); }
      if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && !menu.hidden) {
        var links = Array.prototype.slice.call(menu.querySelectorAll('a')), i = links.indexOf(document.activeElement);
        e.preventDefault();
        links[(i + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length].focus();
      }
    });
    wrap.addEventListener('focusout', function (e) { if (!wrap.contains(e.relatedTarget)) set(false); });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) set(false); });
  }

  // ---------------------------------------------------------------- reading position (one entry per guide, newest first)
  function remember() {
    if (!here) return;
    var crumb = document.getElementById('crumb');
    var timer = null;
    function save() {
      var links = crumb ? crumb.querySelectorAll('a') : [];
      var last = links[links.length - 1];
      var hash = last ? last.getAttribute('href') : '';
      var entry = { g: here.folder, title: here.title, trail: Array.prototype.map.call(links, function (a) { return a.textContent; }),
                    href: '../' + here.folder + '/' + file + hash, t: Date.now() };
      var list = load(RECENT_KEY).filter(function (r) { return r.g !== here.folder; });
      list.unshift(entry);
      store(RECENT_KEY, list.slice(0, MAX_RECENT));
    }
    save();
    if (crumb) new MutationObserver(function () { clearTimeout(timer); timer = setTimeout(save, 1200); })
      .observe(crumb, { attributes: true, attributeFilter: ['data-key'] });
    addEventListener('pagehide', save);
  }

  // ---------------------------------------------------------------- hand a guide search over to the hub's search
  function searchHandoff() {
    var panel = document.getElementById('doc-search-results');
    var input = panel && panel.parentElement.querySelector('input[type="search"]');
    if (!panel || !input) return;
    new MutationObserver(function () {
      if (panel.hidden || !input.value.trim() || panel.querySelector('.doc-search-all')) return;
      var a = document.createElement('a');
      a.className = 'doc-search-all';
      a.href = hubUrl + '?q=' + encodeURIComponent(input.value.trim());
      a.textContent = 'Search all ' + MANIFEST.title + ' for “' + input.value.trim() + '” →';
      panel.appendChild(a);
    }).observe(panel, { childList: true, attributes: true, attributeFilter: ['hidden'] });
  }

  // ---------------------------------------------------------------- keep the theme in step with other open guides
  addEventListener('storage', function (e) {
    if (e.key !== THEME_KEY || !e.newValue) return;
    document.documentElement.setAttribute('data-theme', e.newValue);
    var t = document.getElementById('theme-toggle');
    if (t) t.textContent = e.newValue === 'dark' ? '☀ Light' : '☾ Dark';
  });

  function homeLogo() {
    var logo = document.querySelector('header.topbar .logo');
    if (!logo || logo.closest('a')) return;
    var a = document.createElement('a');
    a.href = hubUrl;
    a.title = MANIFEST.title;
    a.setAttribute('aria-label', MANIFEST.title);
    a.style.display = 'contents';
    logo.replaceWith(a);
    a.appendChild(logo);
  }

  // A deferred script runs before DOMContentLoaded, so the guide's own scripts (search box, breadcrumb) aren't set up yet.
  var started = false;
  function init() { if (started) return; started = true; homeLogo(); switcher(); remember(); searchHandoff(); }
  if (document.readyState === 'complete') init();
  else { document.addEventListener('DOMContentLoaded', function () { setTimeout(init, 0); }); addEventListener('load', init); }
})();
