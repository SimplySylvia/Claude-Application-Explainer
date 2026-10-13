(function () {
  var STATE_KEY = '__GUIDE_KEY__-collapse';
  var SIDEBAR_KEY = '__GUIDE_KEY__-sidebar';
  var GROUP_CHEVRON = '<svg class="group-chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.29 6.71a.996.996 0 0 0 0 1.41L13.17 12l-3.88 3.88a.996.996 0 1 0 1.41 1.41l4.59-4.59a.996.996 0 0 0 0-1.41L10.7 6.7c-.38-.38-1.02-.38-1.41.01"/></svg>';

  function readState() {
    try { return JSON.parse(localStorage.getItem(STATE_KEY)) || {}; } catch (e) { return {}; }
  }
  var saved = readState();
  function persist() {
    try { localStorage.setItem(STATE_KEY, JSON.stringify(saved)); } catch (e) { /* storage unavailable */ }
  }

  // ---------------------------------------------------------------- collapsible sections & subsections
  var collapsibles = [];
  function setCollapsed(el, collapsed, remember) {
    el.classList.toggle('collapsed', collapsed);
    var btn = el.querySelector(':scope > h2 .toggle, :scope > h3 .toggle');
    if (btn) btn.setAttribute('aria-expanded', String(!collapsed));
    if (remember) { saved[el.id] = collapsed; persist(); }
    syncTree();
  }
  function initCollapsibles() {
    document.querySelectorAll('section.sec, .subsec').forEach(function (el) {
      var isDefault = el.hasAttribute('data-collapsed-default');
      collapsibles.push({ el: el, def: isDefault });
      setCollapsed(el, el.id in saved ? saved[el.id] : isDefault, false);
      var btn = el.querySelector(':scope > h2 .toggle, :scope > h3 .toggle');
      btn.addEventListener('click', function () { setCollapsed(el, !el.classList.contains('collapsed'), true); });
    });
  }

  // ---------------------------------------------------------------- collapsible table groups
  var groups = [];
  function setGroup(g, collapsed, remember) {
    g.row.classList.toggle('collapsed', collapsed);
    g.row.setAttribute('aria-expanded', String(!collapsed));
    g.rows.forEach(function (r) { r.classList.toggle('row-hidden', collapsed); });
    if (remember) { saved[g.id] = collapsed; persist(); }
  }
  function initGroups() {
    document.querySelectorAll('table').forEach(function (table, ti) {
      table.querySelectorAll('tr.group').forEach(function (row, gi) {
        var rows = [];
        var next = row.nextElementSibling;
        while (next && !next.classList.contains('group')) { rows.push(next); next = next.nextElementSibling; }
        var g = { id: 'grp-' + (table.closest('section') || {}).id + '-' + ti + '-' + gi, row: row, rows: rows, def: row.hasAttribute('data-collapsed-default') };
        var cell = row.querySelector('td');
        cell.insertAdjacentHTML('beforeend', GROUP_CHEVRON);
        var names = rows.map(function (r) {
          var first = r.querySelector('td');
          return first ? first.textContent.replace(/\s+/g, ' ').trim() : '';
        }).filter(Boolean);
        var preview = document.createElement('span');
        preview.className = 'group-preview';
        var count = document.createElement('b');
        count.textContent = rows.length + (rows.length === 1 ? ' item' : ' items');
        preview.append(count, names.join(' · '));
        preview.title = names.join(' · ');
        cell.querySelector('.group-chev').before(preview);
        var line = document.createElement('div');
        line.className = 'group-line';
        var label = document.createElement('span');
        label.className = 'group-label';
        while (cell.firstChild && cell.firstChild !== preview) label.appendChild(cell.firstChild);
        line.append(label, preview, cell.querySelector('.group-chev'));
        cell.appendChild(line);
        row.setAttribute('data-toggleable', '');
        row.setAttribute('tabindex', '0');
        row.setAttribute('role', 'button');
        var toggle = function () { setGroup(g, !row.classList.contains('collapsed'), true); };
        row.addEventListener('click', toggle);
        row.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
        setGroup(g, g.id in saved ? saved[g.id] : g.def, false);
        groups.push(g);
      });
    });
  }

  function setAll(mode) {
    collapsibles.forEach(function (c) { setCollapsed(c.el, mode === 'reset' ? c.def : mode === 'collapse', false); });
    groups.forEach(function (g) { setGroup(g, mode === 'reset' ? g.def : mode === 'collapse', false); });
    saved = {};
    if (mode !== 'reset') {
      collapsibles.forEach(function (c) { saved[c.el.id] = mode === 'collapse'; });
      groups.forEach(function (g) { saved[g.id] = mode === 'collapse'; });
    }
    persist();
  }

  // ---------------------------------------------------------------- pages (one part visible at a time)
  var pages = [];
  var currentPage = null;
  function showPage(page) {
    if (!page || page === currentPage) return;
    currentPage = page;
    pages.forEach(function (p) { p.hidden = p !== page; });
    var pid = page.getAttribute('data-page');
    document.querySelectorAll('.page-tabs a').forEach(function (a) {
      if (a.getAttribute('data-page') === pid) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    document.querySelectorAll('.tree-part').forEach(function (li) { li.classList.toggle('current', li.getAttribute('data-part') === pid); });
    document.dispatchEvent(new CustomEvent('guide:pagechange', { detail: { page: pid } }));
  }
  function initPages() {
    pages = Array.prototype.slice.call(document.querySelectorAll('main .page'));
    if (!pages.length) return;
    var target = location.hash.length > 1 && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    showPage((target && target.closest('.page')) || pages[0]);
  }
  function scrollToTarget(target, smooth) {
    if (target.classList.contains('part')) window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' });
    else target.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' });
  }

  // Open every collapsed ancestor of a target (and its page) so links, the tree, and URL hashes always land on visible content.
  function reveal(id) {
    var target = document.getElementById(id);
    if (!target) return null;
    showPage(target.closest('.page'));
    var node = target;
    while (node && node !== document.body) {
      if ((node.matches('section.sec') || node.matches('.subsec')) && node.classList.contains('collapsed')) setCollapsed(node, false, true);
      node = node.parentElement;
    }
    return target;
  }
  // Address bar: a page switch adds a history entry so Back returns to the previous page; moves within a page replace it.
  function setHash(id, pageChanged) {
    if (pageChanged) history.pushState(null, '', '#' + id); else history.replaceState(null, '', '#' + id);
  }
  function revealElement(el) {
    var before = currentPage;
    showPage(el.closest('.page'));
    if (currentPage !== before) setHash(el.id || ('part-' + currentPage.getAttribute('data-page')), true);
    var node = el;
    while (node && node !== document.body) {
      if (node.tagName === 'DETAILS') node.open = true;
      if ((node.matches('section.sec') || node.matches('.subsec')) && node.classList.contains('collapsed')) setCollapsed(node, false, true);
      node = node.parentElement;
    }
    var row = el.closest('tr');
    groups.forEach(function (g) { if (g.rows.indexOf(row) >= 0 && g.row.classList.contains('collapsed')) setGroup(g, false, true); });
  }
  window.guideDoc = { revealElement: revealElement, setHash: function (id) { history.replaceState(null, '', '#' + id); } };

  // ---------------------------------------------------------------- sidebar tree
  var body = document.body;
  var sidebar = document.getElementById('sidebar');
  var wide = window.matchMedia('(min-width: 1180px)');
  function setSidebar(open, remember) {
    body.classList.toggle('sidebar-open', open);
    document.getElementById('sidebar-open').setAttribute('aria-expanded', String(open));
    sidebar.setAttribute('aria-hidden', String(!open));
    sidebar.inert = !open;
    if (remember) { try { localStorage.setItem(SIDEBAR_KEY, open ? 'open' : 'closed'); } catch (e) { /* ignore */ } }
  }
  function initSidebar() {
    var pref = null;
    try { pref = localStorage.getItem(SIDEBAR_KEY); } catch (e) { /* ignore */ }
    setSidebar(wide.matches ? pref !== 'closed' : false, false);
    document.getElementById('sidebar-open').addEventListener('click', function () { setSidebar(true, wide.matches); });
    document.getElementById('sidebar-close').addEventListener('click', function () { setSidebar(false, wide.matches); });
    body.addEventListener('click', function (e) {
      if (!wide.matches && body.classList.contains('sidebar-open') && !sidebar.contains(e.target) && !e.target.closest('#sidebar-open')) setSidebar(false, false);
    });
    wide.addEventListener('change', function () { setSidebar(wide.matches && localStorage.getItem(SIDEBAR_KEY) !== 'closed', false); });

    sidebar.querySelectorAll('.tree-part-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () { btn.setAttribute('aria-expanded', String(btn.getAttribute('aria-expanded') !== 'true')); });
    });
    sidebar.querySelectorAll('.tree-twisty').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var li = btn.closest('.tree-sec');
        var open = !li.classList.contains('open');
        li.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', String(open));
      });
    });
    sidebar.querySelectorAll('a[data-target]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var id = a.getAttribute('data-target');
        var wasPage = currentPage;
        var target = reveal(id);
        if (!target) return;
        scrollToTarget(target, wasPage === currentPage);
        setHash(id, wasPage !== currentPage);
        if (!wide.matches) setSidebar(false, false);
      });
    });
    sidebar.querySelector('.sidebar-actions').addEventListener('click', function (e) {
      var b = e.target.closest('[data-all]');
      if (b) setAll(b.getAttribute('data-all'));
    });

    // Filter box
    var filter = document.createElement('div');
    filter.className = 'tree-filter';
    filter.innerHTML = '<input type="search" placeholder="Filter sections…" aria-label="Filter sections">';
    sidebar.querySelector('.sidebar-actions').after(filter);
    var input = filter.querySelector('input');
    var links = Array.prototype.slice.call(sidebar.querySelectorAll('.tree a'));
    links.forEach(function (a) { a.setAttribute('data-label', a.textContent); });
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      sidebar.querySelectorAll('.tree li').forEach(function (li) { li.classList.remove('filtered-out'); });
      links.forEach(function (a) { a.textContent = a.getAttribute('data-label'); });
      if (!q) return;
      sidebar.querySelectorAll('.tree-sec').forEach(function (sec) {
        var subMatch = false;
        sec.querySelectorAll('.tree-sub li').forEach(function (li) {
          var a = li.querySelector('a');
          var hit = highlight(a, q);
          li.classList.toggle('filtered-out', !hit);
          subMatch = subMatch || hit;
        });
        var selfHit = highlight(sec.querySelector(':scope > a'), q);
        if (selfHit && !subMatch) sec.querySelectorAll('.tree-sub li').forEach(function (li) { li.classList.remove('filtered-out'); });
        sec.classList.toggle('filtered-out', !selfHit && !subMatch);
        sec.classList.toggle('open', subMatch);
      });
      sidebar.querySelectorAll('.tree-part').forEach(function (part) {
        var any = part.querySelector('.tree-sec:not(.filtered-out)');
        part.classList.toggle('filtered-out', !any);
        part.querySelector('.tree-part-toggle').setAttribute('aria-expanded', 'true');
      });
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { var first = sidebar.querySelector('.tree-sec:not(.filtered-out) a'); if (first) first.click(); }
      if (e.key === 'Escape') { input.value = ''; input.dispatchEvent(new Event('input')); input.blur(); }
    });

    document.addEventListener('keydown', function (e) {
      if (document.querySelector('.dg-modal:not([hidden])')) return;
      var typing = /INPUT|TEXTAREA/.test(document.activeElement.tagName);
      if (e.key === '[' && !typing) { setSidebar(!body.classList.contains('sidebar-open'), wide.matches); }
      if (e.key === '/' && !typing) { e.preventDefault(); setSidebar(true, wide.matches); input.focus(); }
    });
  }
  function highlight(a, q) {
    var label = a.getAttribute('data-label');
    var i = label.toLowerCase().indexOf(q);
    if (i < 0) return false;
    a.innerHTML = '';
    a.append(label.slice(0, i));
    var m = document.createElement('mark');
    m.textContent = label.slice(i, i + q.length);
    a.append(m, label.slice(i + q.length));
    return true;
  }

  // Mark sections that are collapsed on the page with a dot in the tree.
  function syncTree() {
    if (!sidebar) return;
    sidebar.querySelectorAll('.tree-sec').forEach(function (li) {
      var sec = document.getElementById(li.getAttribute('data-sec'));
      li.classList.toggle('is-collapsed', !!(sec && sec.classList.contains('collapsed')));
    });
  }

  // ---------------------------------------------------------------- scroll-spy + breadcrumb
  function initScrollSpy() {
    var crumb = document.getElementById('crumb');
    var targets = Array.prototype.slice.call(document.querySelectorAll('section.sec, .subsec'));
    var visible = new Set();
    function update() {
      var current = null;
      targets.forEach(function (t) { if (visible.has(t) && (!current || t.compareDocumentPosition(current) & Node.DOCUMENT_POSITION_PRECEDING)) current = t; });
      if (!current) return;
      var sec = current.closest('section.sec');
      sidebar.querySelectorAll('.tree a.active').forEach(function (a) { a.classList.remove('active'); });
      var secLink = sidebar.querySelector('.tree-sec[data-sec="' + sec.id + '"] > a');
      if (secLink) {
        secLink.classList.add('active');
        var li = secLink.closest('.tree-sec');
        if (li.classList.contains('has-sub') && !document.querySelector('.tree-filter input').value) {
          sidebar.querySelectorAll('.tree-sec.open').forEach(function (o) { if (o !== li && !o.dataset.pinned) o.classList.remove('open'); });
          li.classList.add('open');
          var tw = li.querySelector('.tree-twisty');
          if (tw) tw.setAttribute('aria-expanded', 'true');
        }
        var partBtn = li.closest('.tree-part').querySelector('.tree-part-toggle');
        partBtn.setAttribute('aria-expanded', 'true');
      }
      if (current !== sec) {
        var subLink = sidebar.querySelector('.tree a[data-target="' + current.id + '"]');
        if (subLink) subLink.classList.add('active');
      }
      var trail = [];
      trail.push({ id: sec.id, label: sec.querySelector('.sec-title .toggle span').textContent });
      if (current !== sec) trail.push({ id: current.id, label: current.querySelector('.subsec-title .toggle span').textContent.replace(/^\d+ · /, '') });
      var key = trail.map(function (t) { return t.id; }).join('>');
      if (crumb.getAttribute('data-key') !== key) {
        crumb.setAttribute('data-key', key);
        crumb.innerHTML = '';
        trail.forEach(function (t, i) {
          if (i) { var sep = document.createElement('span'); sep.className = 'sep'; sep.textContent = '›'; crumb.appendChild(sep); }
          var a = document.createElement('a');
          a.href = '#' + t.id;
          a.textContent = t.label;
          a.addEventListener('click', function (e) { e.preventDefault(); var el = reveal(t.id); if (el) el.scrollIntoView({ behavior: 'smooth' }); history.replaceState(null, '', '#' + t.id); });
          crumb.appendChild(a);
        });
      }
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) visible.add(e.target); else visible.delete(e.target); });
      update();
    }, { rootMargin: '-64px 0px -60% 0px' });
    targets.forEach(function (t) { io.observe(t); });
  }

  function initStickyShadows() {
    var heads = document.querySelectorAll('h2.sec-title, h3.subsec-title');
    function update() {
      heads.forEach(function (h) {
        var top = parseFloat(getComputedStyle(h).top) || 0;
        var stuck = getComputedStyle(h).position === 'sticky' && Math.abs(h.getBoundingClientRect().top - top) < 1 && window.scrollY > 0;
        h.classList.toggle('stuck', stuck);
      });
    }
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { ticking = false; update(); });
    }, { passive: true });
    update();
  }

  function init() {
    initPages();
    initCollapsibles();
    initGroups();
    initSidebar();
    syncTree();
    initScrollSpy();
    initStickyShadows();
    if (location.hash.length > 1) {
      var target = reveal(decodeURIComponent(location.hash.slice(1)));
      if (target) requestAnimationFrame(function () { scrollToTarget(target, false); });
    }
    window.addEventListener('hashchange', function () {
      var wasPage = currentPage;
      var target = reveal(decodeURIComponent(location.hash.slice(1)));
      if (target) scrollToTarget(target, wasPage === currentPage);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
