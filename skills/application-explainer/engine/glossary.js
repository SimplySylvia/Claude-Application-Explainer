(function () {
  // Parenthetical text that is context rather than another name for the term.
  var CONTEXT_PAREN = /^(as |zus$|911 )/i;
  var SKIP = 'h1, h2, h3, h4, a, code, pre, kbd, svg, button, script, style, textarea, input, mark, .gl-term, .group-preview, .sec-state, .shot-modal, .dg-modal, .diagram, .pill';

  function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }
  function escapeRe(t) { return t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  function aliasesFor(term) {
    var out = [];
    var paren = term.match(/\(([^)]*)\)/);
    var base = term.replace(/\s*\([^)]*\)/g, '');
    base.split(/\s+\/\s+/).forEach(function (a) { if (a) out.push(a); });
    if (paren && !CONTEXT_PAREN.test(paren[1])) {
      paren[1].replace(/["“”…]/g, '').split(/\s*[,/]\s*/).forEach(function (a) { if (a.trim()) out.push(a.trim()); });
    }
    return out.filter(function (a) { return a.length > 1; });
  }
  // Acronyms and mixed-case identifiers (e.g. API, ncT3, ModelV2Switch) match exactly; plain words ignore case.
  function caseSensitive(a) { return /[A-Z]/.test(a.slice(1)) || /\d/.test(a); }

  function init() {
    var section = document.getElementById('glossary');
    if (!section || !window.guideDoc) return;
    var entries = [];
    var byAlias = {};
    var byId = {};
    section.querySelectorAll('tr').forEach(function (row) {
      var b = row.querySelector('td:first-child > b');
      var def = row.cells[1];
      if (!b || !def) return;
      var term = b.textContent.trim();
      row.id = row.id || 'gl-' + slug(term);
      var entry = { term: term, row: row, def: def, where: row.cells[2] };
      entries.push(entry);
      byId[row.id] = entry;
      aliasesFor(term).forEach(function (a) {
        var key = caseSensitive(a) ? a : a.toLowerCase();
        if (!byAlias[key]) byAlias[key] = entry;
      });
    });
    var aliases = Object.keys(byAlias).sort(function (a, b) { return b.length - a.length; });
    if (!aliases.length) return;
    var re = new RegExp('(?<![\\w@/.-])(' + aliases.map(function (a) {
      return caseSensitive(a) ? escapeRe(a) : escapeRe(a).replace(/[a-z]/g, function (c) { return '[' + c + c.toUpperCase() + ']'; });
    }).join('|') + ')(?:s|es)?(?![\\w-])', 'g');
    function lookup(match) {
      var bare = match;
      var e = byAlias[bare] || byAlias[bare.toLowerCase()];
      if (!e) { bare = match.replace(/(es|s)$/, ''); e = byAlias[bare] || byAlias[bare.toLowerCase()]; }
      if (!e) { bare = match.replace(/s$/, ''); e = byAlias[bare] || byAlias[bare.toLowerCase()]; }
      return e;
    }

    // Link the first mention of each term per section (per definition inside the glossary), so prose stays readable.
    var scopes = [];
    document.querySelectorAll('main section.sec').forEach(function (sec) { if (sec !== section) scopes.push({ root: sec, used: new Set() }); });
    entries.forEach(function (e) { scopes.push({ root: e.def, used: new Set([e]) }); });
    scopes.forEach(function (scope) {
      var used = scope.used;
      var walker = document.createTreeWalker(scope.root, NodeFilter.SHOW_TEXT, {
        acceptNode: function (n) {
          return n.nodeValue.trim().length > 1 && !n.parentElement.closest(SKIP) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
        }
      });
      var nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);
      nodes.forEach(function (node) {
        var text = node.nodeValue;
        var frag = null;
        var last = 0;
        re.lastIndex = 0;
        var m;
        while ((m = re.exec(text))) {
          var e = lookup(m[0]);
          if (!e || used.has(e)) continue;
          used.add(e);
          frag = frag || document.createDocumentFragment();
          frag.append(text.slice(last, m.index));
          var a = document.createElement('a');
          a.className = 'gl-term';
          a.href = '#' + e.row.id;
          a.textContent = m[0];
          a.setAttribute('aria-describedby', 'gl-tip');
          a._gl = e;
          frag.append(a);
          last = m.index + m[0].length;
        }
        if (frag) { frag.append(text.slice(last)); node.replaceWith(frag); }
      });
    });

    // ---------------------------------------------------------------- stacked tooltips
    // Hovering a term inside a tooltip opens another tooltip beside it, so readers can follow a chain of definitions.
    var MAX_DEPTH = 8;
    var stack = [];
    var hideTimer = null;
    var trimTimer = null;
    var restoringFocus = false;

    function entryFor(a) { return a._gl || byId[(a.getAttribute('href') || '').slice(1)]; }
    function levelOf(node) {
      var t = node.closest && node.closest('.gl-tip');
      return t ? +t.dataset.level : -1;
    }
    function fill(tip, e, parent) {
      tip.innerHTML = '<div class="gl-tip-head"><span class="gl-tip-kicker"></span><b class="gl-tip-term"></b></div>' +
        '<div class="gl-tip-def"></div><div class="gl-tip-where"></div>' +
        '<a class="gl-tip-link" href="#' + e.row.id + '">Open in glossary →</a>';
      tip.querySelector('.gl-tip-kicker').textContent = parent ? 'Glossary › from ' + parent.term : 'Glossary';
      tip.querySelector('.gl-tip-term').textContent = e.term;
      var def = tip.querySelector('.gl-tip-def');
      [].forEach.call(e.def.childNodes, function (n) { def.appendChild(n.cloneNode(true)); });
      def.querySelectorAll('mark.find-hit').forEach(function (mk) { mk.replaceWith(mk.textContent); });
      def.querySelectorAll('a.gl-term').forEach(function (a) { a.removeAttribute('aria-describedby'); a.classList.remove('gl-active'); });
      var where = tip.querySelector('.gl-tip-where');
      if (e.where && e.where.textContent.trim()) {
        var label = document.createElement('span');
        label.textContent = 'Where: ';
        where.append(label);
        [].forEach.call(e.where.childNodes, function (n) { where.appendChild(n.cloneNode(true)); });
      }
    }
    function placeBelow(tip, r) {
      var w = tip.offsetWidth;
      var h = tip.offsetHeight;
      var left = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), innerWidth - w - 8);
      var below = r.bottom + 8 + h < innerHeight - 8;
      tip.classList.add(below ? 'below' : 'above');
      tip.style.left = left + 'px';
      tip.style.top = (below ? r.bottom + 8 : Math.max(8, r.top - h - 8)) + 'px';
      tip.style.setProperty('--arrow-x', Math.min(Math.max(14, r.left + r.width / 2 - left), w - 14) + 'px');
    }
    function place(level) {
      var item = stack[level];
      var tip = item.el;
      tip.classList.remove('below', 'above', 'side-right', 'side-left');
      tip.style.left = '0px';
      tip.style.top = '0px';
      var r = item.anchor.getBoundingClientRect();
      if (!level) { placeBelow(tip, r); return; }
      var p = stack[level - 1].el.getBoundingClientRect();
      var w = tip.offsetWidth;
      var h = tip.offsetHeight;
      var mid = r.top + r.height / 2;
      var top = Math.min(Math.max(8, mid - 28), innerHeight - h - 8);
      // Beside the parent, on whichever side fits without covering an earlier tooltip; otherwise under the term.
      var others = stack.slice(0, level - 1).map(function (it) { return it.el.getBoundingClientRect(); });
      function clear(x) { return x >= 8 && x + w <= innerWidth - 8 && others.every(function (o) { return x + w <= o.left || x >= o.right || top + h <= o.top || top >= o.bottom; }); }
      var right = p.right + 10;
      var leftSide = p.left - w - 10;
      var prefersLeft = stack[level - 1].el.classList.contains('side-left');
      var sides = prefersLeft ? [['side-left', leftSide], ['side-right', right]] : [['side-right', right], ['side-left', leftSide]];
      var pick = sides.find(function (sd) { return clear(sd[1]); });
      if (!pick) { placeBelow(tip, r); return; }
      tip.classList.add(pick[0]);
      var left = pick[1];
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
      tip.style.setProperty('--arrow-y', Math.min(Math.max(14, mid - top), h - 14) + 'px');
    }
    function trim(level) {
      while (stack.length > level) {
        var item = stack.pop();
        item.el.remove();
        item.anchor.classList.remove('gl-active');
      }
    }
    function openAt(level, anchor, e) {
      if (!e || level >= MAX_DEPTH) return;
      clearTimeout(hideTimer);
      clearTimeout(trimTimer);
      if (stack[level] && stack[level].anchor === anchor) { trim(level + 1); return; }
      trim(level);
      var tip = document.createElement('div');
      tip.className = 'gl-tip';
      tip.id = level ? 'gl-tip-' + level : 'gl-tip';
      tip.dataset.level = level;
      tip.setAttribute('role', 'tooltip');
      tip.style.zIndex = 'calc(var(--z-fullpage) + ' + (5 + level) + ')';
      fill(tip, e, level ? stack[level - 1].entry : null);
      document.body.appendChild(tip);
      if (level) anchor.classList.add('gl-active');
      stack.push({ el: tip, anchor: anchor, entry: e });
      place(level);
    }
    function hideSoon() {
      clearTimeout(hideTimer);
      hideTimer = setTimeout(function () { trim(0); }, 200);
    }
    function open(e) {
      trim(0);
      window.guideDoc.revealElement(e.row);
      window.guideDoc.setHash(e.row.id);
      setTimeout(function () {
        e.row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        e.row.classList.remove('search-flash');
        void e.row.offsetWidth;
        e.row.classList.add('search-flash');
      }, 30);
    }

    document.addEventListener('mouseover', function (ev) {
      if (!ev.target.closest) return;
      var level = levelOf(ev.target);
      var a = ev.target.closest('a.gl-term');
      if (a) { openAt(level + 1, a, entryFor(a)); return; }
      if (level >= 0) {
        // Back on a tooltip's body: keep it, and close anything opened from it after a short pause.
        clearTimeout(hideTimer);
        clearTimeout(trimTimer);
        if (stack.length > level + 1) trimTimer = setTimeout(function () { trim(level + 1); }, 400);
      }
    });
    document.addEventListener('mouseout', function (ev) {
      if (ev.target.closest && (ev.target.closest('a.gl-term') || ev.target.closest('.gl-tip'))) hideSoon();
    });
    document.addEventListener('focusin', function (ev) {
      var a = ev.target.closest && ev.target.closest('a.gl-term');
      if (a && !restoringFocus) openAt(levelOf(a) + 1, a, entryFor(a));
      else if (ev.target.closest && ev.target.closest('.gl-tip')) clearTimeout(hideTimer);
    });
    document.addEventListener('focusout', function (ev) {
      if (ev.target.closest && (ev.target.closest('a.gl-term') || ev.target.closest('.gl-tip'))) hideSoon();
    });
    document.addEventListener('click', function (ev) {
      var a = ev.target.closest && ev.target.closest('a.gl-term, .gl-tip-link');
      if (!a) return;
      var e = entryFor(a);
      if (e) { ev.preventDefault(); open(e); }
    });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && stack.length) {
        var top = stack[stack.length - 1];
        trim(stack.length - 1);
        if (stack.length) { restoringFocus = true; top.anchor.focus({ preventScroll: true }); restoringFocus = false; }
      }
    });
    window.addEventListener('scroll', function () { for (var i = 0; i < stack.length; i++) place(i); }, { passive: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
