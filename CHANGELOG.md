# Changelog

All notable changes to this plugin. Versions match `version` in `.claude-plugin/plugin.json`; update an installed
copy with `/plugin marketplace update`.

## 1.6.0 (2026-10-14)

### Skill

- **Guide hubs.** New `scripts/new_hub.py` creates `<app>-guides/`, one page for every guide about a repo. It
  features the whole-app guide with a tile per page, lists topic guides in a sortable, filterable table with
  section previews, searches every guide's pages, sections and headings (a combobox with results grouped by guide,
  recent pages when empty, `?q=` links), and shows "Continue reading". The hub engine lives in `hub/`. Guides with
  the same `SOURCE_REPO` beside the hub are found automatically; `OTHER_GUIDES` lists guides built another way.
- **Connected guides.** With `HUB_URL` set, a guide's header gets a breadcrumb root (`HUB_TITLE`) and a **Guides**
  menu (disclosure pattern; arrow keys, Esc). The logo links to the hub, the guide's search ends with "Search all
  guides for …", the light/dark choice is shared (`THEME_KEY`), and reading position feeds the hub's "Continue
  reading". This comes from the hub's `nav.js`; a guide without it keeps a plain "All guides" link.
- `new_guide.py` connects a new guide to the hub next to it for the same repo (`--no-hub` skips this), and
  suggests `new_hub.py` when a repo gets its second guide. `new_hub.py --connect` connects an existing guide, gives
  a topic guide still on the default brand color a palette color of its own, and with `--update-engine` re-copies
  an engine that predates hubs.
- Every build of a connected guide re-runs its hub's build (`--no-hub` skips it), so the hub stays current.
- **Depth.** New `engine/depth.css`, shared with hubs: layered surfaces (gray-blue and white in light mode, deep
  navy in dark), soft shadows on cards, tables, code blocks, diagrams and the sidebar, and a frosted header. Color
  stays in small markers. `DEPTH_CSS = False` keeps a custom `TOKENS_CSS`'s own surfaces.
- Starter configs gain `GUIDE_KIND`, `HUB_URL`, `HUB_TITLE`, `THEME_KEY` and `DEPTH_CSS`. New
  `references/hub.md`.

### Repo

- New `tests/test_hub.py`: hub creation and auto-connect, guide builds refreshing the hub, every hub link and search
  entry resolving to a real anchor, standalone guides, and the refusal paths.

## 1.5.1 (2026-10-13)

### Skill

- `changed_since.py --mark-docs` no longer needs `SOURCE_REPO`/`SOURCE_COMMIT`: recording a docs check only touches
  `TOPICS`.
- The topic starter's flow diagram labels its middle zone `APP CODE` instead of a mixed-case "<Topic> IN <App>".

### Repo

- The demo has a second deep dive, **PostgreSQL** (node-postgres), on the same Topics page, added with
  `new_guide.py --into` and researched by `tech-researcher`. The main guide's Tech stack and Architecture sections
  and the Express walkthrough link to it. New screenshot `guide-topics.png` shows both topics in the sidebar.

## 1.5.0 (2026-10-13)

### Skill

- Deep dives now land on one **Topics** page in the main guide instead of a new top-level page each.
  `new_guide.py --into` adds each topic as a group on that page, creating it before Reference the first time.
- Engine: a part's items in `PARTS` can include topic groups, `(id, title, blurb, [sections])`. Each renders as a
  "Topic · <name>" banner before its sections (linkable as `#topic-<id>`) and a labeled group in the sidebar, which
  the sidebar filter hides when none of its sections match.
- Fixed the sidebar highlight and breadcrumb keeping the previous page's section when a page's banners push its
  first section below the scroll-tracking band.

### Repo

- The demo's Express deep dive moved to a Topics page; screenshots recaptured.

## 1.4.0 (2026-10-13)

### Skill

- New **`glossary-scout`** agent for the glossary phase of both skills. It reads the guide as its audience would
  and writes `qa/glossary-work/scout.md`, sorting terms into **add** (a row), **explainer** (needs a topic deep dive
  or a section; offered to the user, never started without a yes), **skip** (known to the audience, one-off, or an
  everyday word the auto-linker would over-match), and **fix** (unused rows, missing names, colliding aliases),
  with priorities and evidence. `glossary-drafter` now drafts from the scout's add list instead of every candidate.
- `extract_text.py` writes `glossary-usage.txt` (how often each glossary term is used, and where), adds the sections
  each candidate appears in to `candidates.txt`, strips page chrome (Copy buttons, collapse badges) from the text,
  and drops sentence-initial ordinary words from the candidates.
- The glossary phase's **Done when** now requires the scout's P1 terms and fixes to be handled and its explainer
  suggestions shown to the user.

### Repo

- Demo glossary updated from a `glossary-scout` run: new Express, `app.use`, React Router, and Vite rows; missing
  names added (Error middleware, SSO, `VITE_FLAG_NEW_ADMIN`, node-postgres). "React Router" in the tech stack no
  longer links to the Express router definition.
- Tests for the new `extract_text.py` outputs.

## 1.3.0 (2026-10-13)

### Skill

- New **topic-explainer** skill: a smaller guide to one technology and how the app uses it. It covers what the
  technology is, core concepts, a usage map and flow diagram, a guided walkthrough of one real flow, patterns and
  gotchas, common changes, the pinned version compared with the latest release, and official docs. It runs only
  when asked for by name (`/topic-explainer`, "topic explainer") or after the user accepts an offer; a plain "what is
  X and how do we use it" question gets a direct answer.
- Topic guides can be **separate** (`<app>-<topic>-guide/`, the default) or a **deep dive** inside an existing
  application-explainer guide. When a guide for the repo exists, Claude asks which.
- New agents `tech-researcher` (web search and fetch only, never sees the repo; prompts carry only the technology,
  version, and generic questions) and `source-verifier` (checks web claims against the cited pages).
- `new_guide.py --topic "<Topic>"` scaffolds a topic guide; `--into <guide>` adds the topic as one part before
  Reference, with `<topic>-` prefixed sections, a `TOPICS` entry, a diagram, and a checklist in `PROGRESS.md`.
- `changed_since.py` reports `DOCS STALE` for topics whose docs were never checked or were checked more than 90 days
  ago; `--mark-docs <slug>` records a re-check.
- The build opens outside links in a new tab (marked ↗) and counts them as citations. Section ids may contain
  hyphens.
- **Code blocks with syntax highlighting** in any guide: `<pre class="code" data-lang="js" data-title="…">`,
  highlighted at build time by the new `engine/highlight.py` (JavaScript/TypeScript/JSX, Python, shell, JSON, SQL,
  YAML, HTTP, GraphQL), with a language label, title, Copy button, and colors for both themes. Nothing is loaded
  from outside the file. The build warns on unknown languages and on a bare `<pre>`.
- Topic guides show concepts in code: the concepts section has a "Concepts in code" example per idea, and the
  walkthrough and recipes quote the repo lines they discuss.
- `tech-researcher` returns a fixed-shape report of about 1,000 words, with code examples for the pinned version.
  Claude saves it to `GUIDE/research/<topic>.md` and spot-checks key claims by opening the cited pages (the rule is
  that nothing from the repo goes to the web, not that only agents may fetch).
- Walkthroughs say where a flow stops when the code doesn't run end to end, and "Try it yourself" lists only steps
  that work as the repo stands.
- The application-explainer starter uses code blocks too: a copy-paste quick start in Local development, one real
  test in Testing strategy, and the weekly commands in the Cheat sheet.

### Repo

- Evals: `trigger-topic-explainer`, `nearmiss-topic-question` (answers and offers, doesn't start a guide),
  `topic-asks-guide-mode` (asks separate guide vs deep dive when a guide exists), and `safety-topic-web-queries`
  (no repo details in web searches, fetches, or the researcher's prompt; the pinned version is documented).
- Unit tests for topic scaffolding, deep dives, external links, docs freshness, and syntax highlighting.
- The live demo has an **Express deep dive** (part 5) built with the topic explainer, linked from its Tech stack and
  Architecture sections, plus code blocks in Local development, Testing, and the Cheat sheet.
- New README screenshots of the deep dive (`guide-topic.png`, `guide-topic-code.png`, `guide-topic-link.png`),
  captured by `docs/demo/capture.py`.

## 1.2.0 (2026-10-13)

### Skill

- **Done when** criteria for every phase in `SKILL.md`, including when to fan out to `repo-researcher` agents
  (more than about 1,000 tracked files or 3 deployables) and how many review findings to spot-check.
- `GUIDE/PROGRESS.md`: the scaffold writes the phase checklist plus sections for scope, decisions, open questions,
  and repo problems. Claude keeps it current, and a resumed session reads it first.
- Updating an existing guide: `guide_config.py` records `SOURCE_REPO` and `SOURCE_COMMIT`, and the new
  `scripts/changed_since.py` lists the sections that cite files changed since then (`--mark` records the new commit).
- The build warns about finished sections that cite no repo paths.
- Diagrams wider than the page now fade at the cut-off edge and show a "scroll sideways or Expand" hint, instead of
  being silently cut off on laptop-sized windows. `qa_check.py` adds a 1280×800 pass that fails if a hint is missing.
- Fixed an unclosed file handle in `engine/icons.py`.

### Repo

- Evals: `safety-secret-not-reproduced` (a hardcoded credential is reported by file, never copied) and
  `safety-screenshots-ask-first` (asks whether staging data is synthetic before capturing).
- Live demo guide for the fictional Shopfront app on GitHub Pages, rebuilt by `docs/demo/make-demo.sh`, which
  also recaptures the README screenshots.
- Unit tests (`tests/`, standard library `unittest`) for scaffolding, building, diagram geometry warnings, and
  glossary merging.
- GitHub Actions CI: unit tests on Python 3.9 and 3.13, the demo build with `qa_check.py`, a check that the
  committed demo is up to date, and a check that pull requests changing `skills/` or `agents/` bump the version.
- End-to-end eval: a new `repo-untouched-bash` grader fails the run if a shell command modifies the app repo.
- README rewrite with badges, quick start, and guardrails; workflow diagram and agent roles in
  `docs/HOW-IT-WORKS.md`.
- MIT license, issue templates, and a pull request template.

## 1.1.0 (2026-10-09)

- Restructured `SKILL.md` around a nine-phase checklist (scope → share) with approval gates, and aligned
  `references/workflow.md` and `PROMPT.md` with it.
- Added subagents: `repo-researcher`, `structure-reviewer`, and `section-verifier` (read-only), and
  `glossary-drafter`.
- Added the `claude plugin eval` suite: trigger, near-miss, and end-to-end cases on a fixture app.
- Fixed a dead `design-tokens.md` reference, made screenshot compression and email scrubbing portable,
  generalized sharing options and domain-specific wording, and added usage errors to the glossary scripts.

## 1.0.0 (2026-10-09)

- First release: the application-explainer skill (build engine, starter template, scaffold, QA, and glossary
  scripts) packaged as a Claude Code plugin with a single-plugin marketplace.
