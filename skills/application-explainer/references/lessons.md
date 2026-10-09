# Lessons learned (from the first guide)

The accuracy rules and common mistakes are summarized in `SKILL.md`; this file has the detail and the tooling gotchas.

## Accuracy

- **Spot-check agent findings before acting.** Several confident review findings were wrong (e.g. "the pre-commit hook doesn't run lint-staged" when an Nx target did). Several were right and important: wrong deploy order, which services call an AI model directly, routes that were server endpoints and not pages.
- **Easy-to-get-wrong claims:**
  - how data reaches the warehouse (live queries vs scheduled exports)
  - deploy order and which service deploys separately
  - load balancer and auth-proxy details
  - counts
  - which engine backs each AI feature
- **Redirect-only routes:** read what a route actually does, e.g. a route that only redirects and logs an event.
- **Gates aren't always data:** a tab that says "page not found" may be behind a feature flag, not missing data. Read the gate in code.
- **Unclear vendor names:** grep with lowercase and snake_case variants (`acme_vendor` for "Acme Vendor"), not just display names.

## Build and tooling

- **Shell quirks:** zsh doesn't word-split `$var` in loops, so use Python for batch file operations. macOS has no `timeout`. Python 3.9 rejects backslashes inside f-string expressions, so precompute them.
- **Safe edits:** for text edits in big files, use exact-match replace with an `assert` count == 1. Broad regex replaces once corrupted a whole table column.
- **Headless screenshots:** headless Chrome screenshots of a scrolled page come out blank. For visual QA, move the element to the top of the page in a throwaway copy, or check with `--dump-dom` + a JS probe.
- **Headless timing:** `requestAnimationFrame` and smooth scrolling don't advance in headless runs. In test copies, swap `'smooth'` for `'auto'` (qa_check.py does this).

## Linking and size

- **Glossary aliases:** remove aliases that collide with everyday words or common product names before writing. e.g. an alias "portal" ends up linking every "Portal".
- **Share version:** screenshots can make the file several times larger (e.g. 4 MB vs 1 MB). The share version is built automatically.

## Browser automation

- **Window state:** Chrome must not be fullscreen to resize. If resizing fails, close the tab and start a fresh window.
- **Ask first:** account changes (flags, roles), OAuth consent, and publishing need explicit user permission each time.
