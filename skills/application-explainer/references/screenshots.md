# Screenshots with Claude in Chrome

Optional. This adds a Screen column to the features table and a gallery to the site map.

## Before capturing (ask the user)

- **Which environment** (staging, local), and confirm the user is signed in to it in Chrome.
- **Is the data synthetic?** If any real personal data could appear, stop and confirm scope first. Prefer synthetic test accounts.
- **Staff names and avatars:** always scrub them (below), even on staging.
- **Window size:** Chrome must be a normal window, not fullscreen. Resize to 1440×900, which gives a viewport of about 1440×723.

## Capture loop

1. Load the browser tools once (`tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`, `javascript_tool`, `find`, `resize_window`, `browser_batch`). Use a new tab.
2. In the app tab, define these helpers. Redefine them after every full page load.

```js
window.__settle = async function (ms) { ms = ms || 12000; const t0 = Date.now(); await new Promise(r => setTimeout(r, 600));
  while (Date.now() - t0 < ms) { if (!document.querySelector('[role=progressbar],[class*=spinner],[class*=Spinner],[class*=Skeleton]')) break;
    await new Promise(r => setTimeout(r, 300)); } await new Promise(r => setTimeout(r, 700)); };
// SPA navigation without a reload (works for history-based routers)
window.__go = async function (path) { history.pushState({}, '', path); dispatchEvent(new PopStateEvent('popstate')); await __settle(); return location.pathname + location.search; };
// Scrub staff identity. Set STAFF_DOMAIN to the company's email domain first.
const STAFF_DOMAIN = 'example.com';
// Emails, "Name (Role)", "Name, Role", avatars, names above role lines
const ROLE = /\b(Lead|Coordinator|Manager|Admin|Engineer|Specialist|Agent|Representative|Director|Analyst|Support)\b/;
window.__scrub = function () { let n = 0; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const nodes = [];
  while (w.nextNode()) nodes.push(w.currentNode);
  nodes.forEach(t => { let v = t.nodeValue, o = v;
    v = v.replace(new RegExp('[A-Za-z0-9._%+-]+@' + STAFF_DOMAIN.replace(/\./g, '\\.'), 'g'), 'staff@' + STAFF_DOMAIN);
    v = v.replace(/\b[A-Z][a-z]+(?: [A-Z][a-z'-]+){1,2} \((?=[^)]*\b(?:Lead|Coordinator|Manager|Admin|Specialist))[^)]*\)/g, 'Staff member');
    if (v !== o) { t.nodeValue = v; n++; } });
  document.querySelectorAll('img[src*="googleusercontent"],img[class*=vatar],[class*=vatar] img,[class*=Avatar]').forEach(e => { e.style.filter = 'blur(6px)'; n++; });
  document.querySelectorAll('*').forEach(el => { if (el.children.length) return; const nx = el.nextElementSibling || (el.parentElement && el.parentElement.nextElementSibling);
    if (nx && ROLE.test(nx.textContent || '') && (nx.textContent || '').length < 60 && /^[A-Z][a-z]+(?: [A-Z][a-z'-]+){1,2}$/.test((el.textContent || '').trim())) { el.style.filter = 'blur(5px)'; n++; } });
  return n; };
window.__go2 = async function (p) { const r = await __go(p); await __settle(); return [r, __scrub()]; };
```

3. For each screen:
   1. Run `await __go2('/route')`.
   2. Take a quick screenshot at scale 0.5 to check it looks right.
   3. Blur any columns that could identify real people (caller lists, contact tables).
   4. Move the mouse out of frame: hover at the bottom-right corner (1435, 718).
   5. Take the real screenshot with `save_to_disk: true, scale: 0.75`, which gives 1080 px wide.
4. Recompress into the guide (zsh doesn't word-split variables, so loop in Python for batches):

```bash
# macOS
sips -s format jpeg -s formatOptions 72 <saved-path> --out <guide>/screenshots/<name>.jpg
# Linux/Windows (ImageMagick)
magick <saved-path> -quality 72 <guide>/screenshots/<name>.jpg
```

5. Use `browser_batch` to chain navigate → settle → hover → screenshot. Keep long JS probes under about 40 s, or split them.

## Map screenshots in `shots.py`

- `AREAS`: gallery groups in display order: (area, icon key, color family, description).
- `SHOTS`: name → (area, title, route, note). Use `:id` placeholders in routes, not real IDs.
- `FEATURE_SHOTS`: features-table row (first bold text) → list of shot names, or a reason string ("Restricted: needs X role").
- `NOT_CAPTURED`: (route, what showed, why). For each one, tell the user what would unblock it (role, group, feature flag, test data, or a bug fix).

## Gotchas

- **Empty screens:** an empty state for the capturing user still shows the layout. Say so in the note ("Empty for the capturing user").
- **Gated screens:** flags or roles hide screens. Read the route's gate in code before concluding a page is broken.
- **Changing your own account:** don't toggle feature flags, roles, or groups on the user's account without explicit permission. That's an account change.
- **Size:** screenshots dominate file size (≈ 85 KB each). The build always writes a `-no-screenshots` share version too.
