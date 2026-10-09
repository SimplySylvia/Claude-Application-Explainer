(function () {
  function init() {
    var dataEl = document.getElementById('shots-data');
    if (!dataEl) return;
    var data = JSON.parse(dataEl.textContent);
    document.querySelectorAll('img[data-shot]').forEach(function (img) {
      var s = data[img.getAttribute('data-shot')];
      if (s) { img.src = s.src; img.alt = s.title; }
    });

    var box = document.createElement('div');
    box.className = 'shot-modal';
    box.hidden = true;
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'true');
    box.innerHTML =
      '<div class="shot-bar"><span class="shot-title"></span><code class="shot-route"></code><span class="shot-note"></span>' +
      '<span class="dg-spacer"></span><span class="shot-count"></span>' +
      '<button type="button" data-act="prev" aria-label="Previous screenshot">‹</button>' +
      '<button type="button" data-act="next" aria-label="Next screenshot">›</button>' +
      '<button type="button" data-act="close" class="shot-close">Close</button></div>' +
      '<div class="shot-stage"><img alt=""></div>';
    document.body.appendChild(box);
    var list = [];
    var idx = 0;
    var last = null;

    function show() {
      var s = data[list[idx]];
      box.querySelector('.shot-stage img').src = s.src;
      box.querySelector('.shot-title').textContent = s.title;
      box.querySelector('.shot-route').textContent = s.route;
      box.querySelector('.shot-note').textContent = s.note || '';
      box.querySelector('.shot-count').textContent = list.length > 1 ? (idx + 1) + ' / ' + list.length : '';
      box.querySelectorAll('[data-act="prev"],[data-act="next"]').forEach(function (b) { b.hidden = list.length < 2; });
    }
    function open(names, start) {
      list = names.filter(function (n) { return data[n]; });
      if (!list.length) return;
      idx = Math.max(0, list.indexOf(start));
      last = document.activeElement;
      box.hidden = false;
      document.documentElement.classList.add('dg-lock');
      show();
      box.querySelector('.shot-close').focus();
    }
    function close() {
      box.hidden = true;
      document.documentElement.classList.remove('dg-lock');
      if (last) last.focus();
    }
    function step(d) { idx = (idx + d + list.length) % list.length; show(); }

    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]');
      if (b) {
        var a = b.getAttribute('data-act');
        if (a === 'close') close(); else if (a === 'prev') step(-1); else if (a === 'next') step(1);
      } else if (e.target.classList.contains('shot-stage')) close();
    });
    box.querySelector('.shot-stage img').addEventListener('click', function (e) { e.currentTarget.classList.toggle('actual'); });
    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') step(1);
      else if (e.key === 'ArrowLeft') step(-1);
      else return;
      e.preventDefault();
    });
    document.addEventListener('click', function (e) {
      var t = e.target.closest('[data-shots]');
      if (!t || box.contains(t)) return;
      e.preventDefault();
      open(t.getAttribute('data-shots').split(','), t.getAttribute('data-start') || '');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
