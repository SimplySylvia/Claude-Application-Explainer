// Copy buttons on code blocks (build/highlight.py renders them). Falls back to a selection copy where the
// Clipboard API isn't available, e.g. some browsers on file:// URLs.
(function () {
  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) { /* nothing else to try */ }
    document.body.removeChild(ta);
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.code-copy');
    if (!btn) return;
    var text = btn.closest('.code-block').querySelector('pre code').textContent;
    var done = function () { btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = 'Copy'; }, 1500); };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
    else { fallback(text); done(); }
  });
})();
