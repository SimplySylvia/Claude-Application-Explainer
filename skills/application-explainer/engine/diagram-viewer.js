(function () {
  var MIN_SCALE = 0.2;
  var MAX_SCALE = 8;
  var ICONS = __ICONS__;

  function icon(name) {
    return '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS[name] + '</svg>';
  }

  function init() {
    var dialog = document.createElement('div');
    dialog.className = 'dg-modal';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('aria-labelledby', 'dg-modal-title');
    dialog.hidden = true;
    dialog.innerHTML =
      '<div class="dg-modal-bar">' +
      '<span class="dg-modal-title" id="dg-modal-title"></span>' +
      '<span class="dg-modal-legend"></span>' +
      '<span class="dg-spacer"></span>' +
      '<span class="dg-zoom-level" aria-live="polite">100%</span>' +
      '<button type="button" data-act="out" title="Zoom out (−)" aria-label="Zoom out">' + icon('zoomOut') + '</button>' +
      '<button type="button" data-act="in" title="Zoom in (+)" aria-label="Zoom in">' + icon('zoomIn') + '</button>' +
      '<button type="button" data-act="fit" title="Fit to screen (0)">' + icon('fit') + '<span>Fit</span></button>' +
      '<button type="button" data-act="one" title="Actual size (1)"><span>100%</span></button>' +
      '<button type="button" data-act="close" class="dg-close" title="Close (Esc)">' + icon('close') + '<span>Close</span></button>' +
      '</div>' +
      '<div class="dg-stage"><div class="dg-canvas"></div></div>' +
      '<div class="dg-hint">Drag to pan · scroll or pinch to zoom · double-click to zoom in (Shift to zoom out) · arrow keys pan · Esc closes</div>';
    document.body.appendChild(dialog);

    var stage = dialog.querySelector('.dg-stage');
    var canvas = dialog.querySelector('.dg-canvas');
    var level = dialog.querySelector('.dg-zoom-level');
    var view = { s: 1, x: 0, y: 0, w: 0, h: 0 };
    var lastFocus = null;

    function clamp(s) {
      return Math.max(MIN_SCALE, Math.min(MAX_SCALE, s));
    }
    function apply() {
      canvas.style.transform = 'translate(' + view.x + 'px,' + view.y + 'px) scale(' + view.s + ')';
      level.textContent = Math.round(view.s * 100) + '%';
    }
    function stageSize() {
      var r = stage.getBoundingClientRect();
      return { w: r.width, h: r.height, left: r.left, top: r.top };
    }
    function placeAt(scale) {
      var r = stageSize();
      view.s = clamp(scale);
      view.x = (r.w - view.w * view.s) / 2;
      view.y = (r.h - view.h * view.s) / 2;
      apply();
    }
    function fit() {
      var r = stageSize();
      placeAt(Math.min((r.w - 48) / view.w, (r.h - 48) / view.h));
    }
    function zoomAt(factor, cx, cy) {
      var next = clamp(view.s * factor);
      var k = next / view.s;
      view.x = cx - (cx - view.x) * k;
      view.y = cy - (cy - view.y) * k;
      view.s = next;
      apply();
    }
    function zoomCenter(factor) {
      var r = stageSize();
      zoomAt(factor, r.w / 2, r.h / 2);
    }
    function pan(dx, dy) {
      view.x += dx;
      view.y += dy;
      apply();
    }

    function open(diagram) {
      var svg = diagram.querySelector('svg.dg');
      var vb = svg.viewBox.baseVal;
      view.w = vb.width;
      view.h = vb.height;
      var clone = svg.cloneNode(true);
      clone.setAttribute('width', vb.width);
      clone.setAttribute('height', vb.height);
      canvas.innerHTML = '';
      canvas.style.width = vb.width + 'px';
      canvas.style.height = vb.height + 'px';
      canvas.appendChild(clone);
      dialog.querySelector('.dg-modal-title').textContent = svg.getAttribute('aria-label') || 'Diagram';
      var legendSlot = dialog.querySelector('.dg-modal-legend');
      legendSlot.innerHTML = '';
      var legend = diagram.previousElementSibling;
      if (legend && legend.classList.contains('legend')) {
        var copy = legend.cloneNode(true);
        var expand = copy.querySelector('.dg-expand');
        if (expand) expand.remove();
        legendSlot.appendChild(copy);
      }
      lastFocus = document.activeElement;
      dialog.hidden = false;
      document.documentElement.classList.add('dg-lock');
      fit();
      dialog.querySelector('.dg-close').focus();
    }
    function close() {
      dialog.hidden = true;
      document.documentElement.classList.remove('dg-lock');
      canvas.innerHTML = '';
      if (lastFocus) lastFocus.focus();
    }

    dialog.addEventListener('click', function (e) {
      var button = e.target.closest('button[data-act]');
      if (!button) return;
      var act = button.getAttribute('data-act');
      if (act === 'in') zoomCenter(1.25);
      else if (act === 'out') zoomCenter(0.8);
      else if (act === 'fit') fit();
      else if (act === 'one') placeAt(1);
      else if (act === 'close') close();
    });

    stage.addEventListener(
      'wheel',
      function (e) {
        e.preventDefault();
        var r = stageSize();
        // Trackpad pinch arrives as ctrl+wheel with small deltas.
        var factor = Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015));
        zoomAt(factor, e.clientX - r.left, e.clientY - r.top);
      },
      { passive: false },
    );

    var pointers = new Map();
    var pinchDistance = null;
    function distance() {
      var p = Array.from(pointers.values());
      return Math.hypot(p[0].x - p[1].x, p[0].y - p[1].y);
    }
    stage.addEventListener('pointerdown', function (e) {
      stage.setPointerCapture(e.pointerId);
      pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      stage.classList.add('dragging');
      if (pointers.size === 2) pinchDistance = distance();
    });
    stage.addEventListener('pointermove', function (e) {
      if (!pointers.has(e.pointerId)) return;
      var prev = pointers.get(e.pointerId);
      var cur = { x: e.clientX, y: e.clientY };
      pointers.set(e.pointerId, cur);
      if (pointers.size === 1) {
        pan(cur.x - prev.x, cur.y - prev.y);
      } else if (pointers.size === 2 && pinchDistance) {
        var p = Array.from(pointers.values());
        var r = stageSize();
        var d = distance();
        zoomAt(d / pinchDistance, (p[0].x + p[1].x) / 2 - r.left, (p[0].y + p[1].y) / 2 - r.top);
        pinchDistance = d;
      }
    });
    function release(e) {
      pointers.delete(e.pointerId);
      if (pointers.size < 2) pinchDistance = null;
      if (pointers.size === 0) stage.classList.remove('dragging');
    }
    stage.addEventListener('pointerup', release);
    stage.addEventListener('pointercancel', release);
    stage.addEventListener('dblclick', function (e) {
      var r = stageSize();
      zoomAt(e.shiftKey ? 0.5 : 2, e.clientX - r.left, e.clientY - r.top);
    });

    document.addEventListener('keydown', function (e) {
      if (dialog.hidden) return;
      var step = e.shiftKey ? 200 : 60;
      switch (e.key) {
        case 'Escape': close(); break;
        case '+': case '=': zoomCenter(1.25); break;
        case '-': case '_': zoomCenter(0.8); break;
        case '0': fit(); break;
        case '1': placeAt(1); break;
        case 'ArrowLeft': pan(step, 0); break;
        case 'ArrowRight': pan(-step, 0); break;
        case 'ArrowUp': pan(0, step); break;
        case 'ArrowDown': pan(0, -step); break;
        case 'Tab': {
          var focusable = dialog.querySelectorAll('button');
          var first = focusable[0];
          var last = focusable[focusable.length - 1];
          if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
          else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
          return;
        }
        default: return;
      }
      e.preventDefault();
    });
    window.addEventListener('resize', function () {
      if (!dialog.hidden) fit();
    });

    document.querySelectorAll('.diagram').forEach(function (diagram) {
      var svg = diagram.querySelector('svg.dg');
      if (!svg) return;
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'dg-expand';
      button.innerHTML = icon('expand') + '<span>Expand</span>';
      button.setAttribute('aria-label', 'Open “' + (svg.getAttribute('aria-label') || 'diagram') + '” fullscreen');
      button.addEventListener('click', function () { open(diagram); });
      var legend = diagram.previousElementSibling;
      if (legend && legend.classList.contains('legend')) legend.appendChild(button);
      else diagram.insertBefore(button, diagram.firstChild);
      svg.addEventListener('click', function () { open(diagram); });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
