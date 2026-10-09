(function () {
  var MAX_RESULTS = 40;

  function textOf(el) { return (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim(); }

  // Build the index from the DOM: every heading, table row, list item, caption, and site-map entry.
  function buildIndex() {
    var items = [];
    var selector = [
      'main h2.sec-title', 'main h3.subsec-title', 'main .card h3', 'main tr',
      'main li', 'main .gallery-head h4', 'main p.sub', 'main p.caption', 'main .sitemap summary', 'main figcaption', 'main .part'
    ].join(',');
    document.querySelectorAll(selector).forEach(function (el) {
      if (el.closest('.shot-modal, .dg-modal, nav.tree')) return;
      if (el.matches('li') && el.querySelector('li')) return;
      if (el.matches('tr') && !el.querySelector('td')) return;
      var text = el.matches('tr') ? [].map.call(el.cells, textOf).filter(Boolean).join(' — ') : textOf(el);
      if (!text || text.length < 2) return;
      var sec = el.closest('section.sec');
      var sub = el.closest('.subsec');
      var part = sec ? sec.previousElementSibling : null;
      while (part && !part.classList.contains('part')) part = part.previousElementSibling;
      var kind = el.matches('h2, .part') ? 'Section' : el.matches('h3') ? 'Heading' : el.matches('tr') ? (el.classList.contains('group') ? 'Group' : 'Row') :
        el.matches('figcaption') ? 'Screen' : el.matches('summary') ? 'Route' : el.matches('li') ? 'Item' : 'Text';
      var title = text;
      if (el.matches('h2, h3') && el.querySelector('.toggle span')) title = text = textOf(el.querySelector('.toggle span'));
      if (el.matches('.part')) title = textOf(el.querySelector('.part-title'));
      if (el.matches('tr')) {
        var first = el.querySelector('.group-label') || el.querySelector('td');
        title = textOf(first);
        if (el.classList.contains('group')) text = title;
      }
      items.push({
        el: el, kind: kind, text: text, lower: text.toLowerCase(), title: title.slice(0, 90),
        crumb: [part && part.querySelector('.part-title') ? textOf(part.querySelector('.part-title')) : '',
                sec ? textOf(sec.querySelector('.sec-title .toggle span')) : '',
                sub ? textOf(sub.querySelector('.subsec-title .toggle span')) : ''].filter(Boolean).join(' › '),
        weight: kind === 'Section' ? 6 : kind === 'Heading' ? 5 : kind === 'Group' ? 4 : kind === 'Row' ? 3 : kind === 'Route' ? 3 : 1
      });
    });
    return items;
  }

  function score(item, terms) {
    var s = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i];
      var at = item.lower.indexOf(t);
      if (at < 0) return 0;
      s += 10 - Math.min(at / 40, 8);
      if (item.title.toLowerCase().indexOf(t) >= 0) s += 6;
      if (new RegExp('\\b' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(item.lower)) s += 3;
    }
    return s + item.weight * 2 - Math.min(item.text.length / 200, 4);
  }

  function snippet(text, terms) {
    var lower = text.toLowerCase();
    var at = lower.indexOf(terms[0]);
    var start = Math.max(0, at - 50);
    var out = (start > 0 ? '…' : '') + text.slice(start, start + 170) + (start + 170 < text.length ? '…' : '');
    return out;
  }

  function highlight(container, text, terms) {
    container.textContent = '';
    var re = new RegExp('(' + terms.map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')', 'gi');
    var last = 0;
    text.replace(re, function (m, _g, idx) {
      container.append(text.slice(last, idx));
      var mark = document.createElement('mark');
      mark.textContent = m;
      container.append(mark);
      last = idx + m.length;
      return m;
    });
    container.append(text.slice(last));
  }

  var MAX_FIND = 2000;
  var FIND_SKIP = 'script, style, svg, textarea, input, .group-preview, .sec-state, .shot-modal, .dg-modal, nav.tree';

  function escapeRe(t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  // Wrap every occurrence of any term in the page body in <mark class="find-hit">.
  function markAll(root, terms) {
    var re = new RegExp(terms.map(escapeRe).sort(function (a, b) { return b.length - a.length; }).join('|'), 'gi');
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (!n.nodeValue.trim() || n.parentElement.closest(FIND_SKIP)) return NodeFilter.FILTER_REJECT;
        re.lastIndex = 0;
        return re.test(n.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      }
    });
    var nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    var marks = [];
    for (var i = 0; i < nodes.length && marks.length < MAX_FIND; i++) {
      var node = nodes[i];
      var text = node.nodeValue;
      var frag = document.createDocumentFragment();
      var last = 0;
      re.lastIndex = 0;
      var m;
      while ((m = re.exec(text)) && marks.length < MAX_FIND) {
        frag.append(text.slice(last, m.index));
        var mk = document.createElement('mark');
        mk.className = 'find-hit';
        mk.textContent = m[0];
        frag.append(mk);
        marks.push(mk);
        last = m.index + m[0].length;
      }
      frag.append(text.slice(last));
      node.replaceWith(frag);
    }
    return marks;
  }
  function unmarkAll(marks) {
    var parents = new Set();
    marks.forEach(function (mk) {
      if (!mk.parentNode) return;
      parents.add(mk.parentNode);
      mk.replaceWith(mk.textContent);
    });
    parents.forEach(function (p) { p.normalize(); });
  }

  function init() {
    var host = document.querySelector('header.topbar');
    if (!host) return;
    var wrap = document.createElement('div');
    wrap.className = 'doc-search';
    wrap.innerHTML =
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14"/></svg>' +
      '<input type="search" placeholder="Search the guide…" aria-label="Search the guide" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="doc-search-results">' +
      '<span class="find-bar" hidden><span class="find-count" aria-live="polite"></span>' +
      '<button type="button" class="find-btn" data-find="-1" title="Previous match (Shift+Enter)" aria-label="Previous match">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.12 14.71 12 10.83l3.88 3.88a.996.996 0 1 0 1.41-1.41L12.7 8.71a.996.996 0 0 0-1.41 0L6.7 13.3a.996.996 0 0 0 0 1.41c.39.38 1.03.39 1.42 0"/></svg></button>' +
      '<button type="button" class="find-btn" data-find="1" title="Next match (Enter)" aria-label="Next match">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.88 9.29 12 13.17 8.12 9.29a.996.996 0 1 0-1.41 1.41l4.59 4.59c.39.39 1.02.39 1.41 0l4.59-4.59a.996.996 0 0 0 0-1.41c-.39-.38-1.03-.39-1.42 0"/></svg></button></span>' +
      '<kbd>' + (/Mac|iPhone|iPad/.test(navigator.platform) ? '⌘K' : 'Ctrl K') + '</kbd>' +
      '<div class="doc-search-results" id="doc-search-results" role="listbox" hidden></div>';
    var theme = host.querySelector('#theme-toggle');
    host.insertBefore(wrap, theme);
    var input = wrap.querySelector('input');
    var panel = wrap.querySelector('.doc-search-results');
    var index = null;
    var results = [];
    var active = 0;
    var picked = false;
    var bar = wrap.querySelector('.find-bar');
    var countEl = wrap.querySelector('.find-count');
    var find = { query: '', marks: [], at: -1 };

    function clearFind() {
      if (find.marks.length) unmarkAll(find.marks);
      find = { query: '', marks: [], at: -1 };
      bar.hidden = true;
      wrap.classList.remove('finding');
    }
    function showFindCount() {
      var n = find.marks.length;
      countEl.textContent = n ? (find.at + 1) + ' / ' + n + (n === MAX_FIND ? '+' : '') : 'No matches';
      wrap.classList.toggle('find-none', !n);
    }
    function stepFind(d) {
      var n = find.marks.length;
      if (!n) return;
      if (find.at >= 0) find.marks[find.at].classList.remove('find-current');
      find.at = (find.at + d + n) % n;
      var mk = find.marks[find.at];
      mk.classList.add('find-current');
      showFindCount();
      window.guideDoc.revealElement(mk);
      setTimeout(function () { mk.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 30);
    }
    function flash(el) {
      el.classList.remove('search-flash');
      void el.offsetWidth;
      el.classList.add('search-flash');
    }
    // With an anchor, start at the first match inside it (or the next one after it); otherwise below the scroll position.
    function startFind(q, anchor) {
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      clearFind();
      if (!terms.length) return;
      panel.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      find.query = q;
      find.marks = markAll(document.querySelector('main'), terms);
      bar.hidden = false;
      wrap.classList.add('finding');
      var start = anchor ?
        find.marks.findIndex(function (mk) { return anchor.contains(mk) || (anchor.compareDocumentPosition(mk) & Node.DOCUMENT_POSITION_FOLLOWING); }) :
        find.marks.findIndex(function (mk) { var r = mk.getBoundingClientRect(); return r.height && r.top > 120; });
      find.at = (start < 0 ? 0 : start) - 1;
      showFindCount();
      stepFind(1);
    }

    function render(q) {
      if (!index) index = buildIndex();
      var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
      if (!terms.length) { panel.hidden = true; input.setAttribute('aria-expanded', 'false'); return; }
      results = index.map(function (it) { return { it: it, s: score(it, terms) }; })
        .filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, MAX_RESULTS);
      panel.innerHTML = '';
      if (!results.length) {
        panel.innerHTML = '<div class="doc-search-empty">No matches. Try fewer words or a route like <code>/admin</code>.</div>';
      } else {
        var head = document.createElement('div');
        head.className = 'doc-search-count';
        head.textContent = results.length + (results.length === MAX_RESULTS ? '+' : '') + ' results · Enter highlights every match · click a result (or ↑↓ then Enter) to start from it';
        panel.appendChild(head);
        results.forEach(function (r, i) {
          var opt = document.createElement('button');
          opt.type = 'button';
          opt.className = 'doc-search-hit';
          opt.setAttribute('role', 'option');
          opt.dataset.i = i;
          var top = document.createElement('div');
          top.className = 'hit-top';
          var kind = document.createElement('span');
          kind.className = 'hit-kind';
          kind.textContent = r.it.kind;
          var title = document.createElement('span');
          title.className = 'hit-title';
          highlight(title, r.it.title, terms);
          top.append(kind, title);
          var crumb = document.createElement('div');
          crumb.className = 'hit-crumb';
          crumb.textContent = r.it.crumb;
          var snip = document.createElement('div');
          snip.className = 'hit-snip';
          if (r.it.text !== r.it.title) highlight(snip, snippet(r.it.text, terms), terms);
          opt.append(top, crumb, snip);
          panel.appendChild(opt);
        });
      }
      active = 0;
      picked = false;
      mark();
      panel.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }
    function mark() {
      panel.querySelectorAll('.doc-search-hit').forEach(function (b, i) {
        b.classList.toggle('active', picked && i === active);
        if (i === active) b.scrollIntoView({ block: 'nearest' });
      });
    }
    function go(i) {
      var r = results[i];
      if (!r) return;
      window.guideDoc.revealElement(r.it.el);
      startFind(input.value, r.it.el);
      if (!find.marks.length) setTimeout(function () { r.it.el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 30);
      flash(r.it.el);
    }

    var timer = null;
    input.addEventListener('input', function () {
      if (find.query && input.value !== find.query) clearFind();
      clearTimeout(timer);
      timer = setTimeout(function () { render(input.value); }, 80);
    });
    input.addEventListener('focus', function () { if (input.value && !find.query) render(input.value); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' && !panel.hidden) { active = picked ? Math.min(active + 1, results.length - 1) : 0; picked = true; mark(); e.preventDefault(); }
      else if (e.key === 'ArrowUp' && !panel.hidden) { active = Math.max(active - 1, 0); picked = true; mark(); e.preventDefault(); }
      else if (e.key === 'Enter') {
        e.preventDefault();
        if (picked && !panel.hidden && results[active]) go(active);
        else if (find.query === input.value && find.query) stepFind(e.shiftKey ? -1 : 1);
        else startFind(input.value);
      }
      else if (e.key === 'Escape') { if (find.query) clearFind(); else if (input.value) { input.value = ''; render(''); } else { input.blur(); } }
    });
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('[data-find]');
      if (b) stepFind(+b.getAttribute('data-find'));
    });
    panel.addEventListener('click', function (e) { var b = e.target.closest('.doc-search-hit'); if (b) go(+b.dataset.i); });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target)) { panel.hidden = true; input.setAttribute('aria-expanded', 'false'); } });
    document.addEventListener('keydown', function (e) {
      if (document.querySelector('.dg-modal:not([hidden]), .shot-modal:not([hidden])')) return;
      if (e.key === 'g' && (e.metaKey || e.ctrlKey) && find.marks.length) {
        e.preventDefault();
        stepFind(e.shiftKey ? -1 : 1);
        return;
      }
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        e.stopImmediatePropagation();
        input.focus();
        input.select();
      }
    }, true);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
